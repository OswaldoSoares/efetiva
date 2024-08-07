import decimal
import time
from django.db import connection, reset_queries


from datetime import date, datetime, timedelta

from core.tools import apos_meia_noite, calcular_diferenca, str_hora
from clientes.models import (
    Cliente,
    Tabela,
    TabelaCapacidade,
    TabelaPerimetro,
    TabelaVeiculo,
)
from dateutil.relativedelta import relativedelta

# from django.db.models import Max
from django.db.models import Max, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from pessoas.models import Pessoal
from romaneios.models import NotasClientes, RomaneioNotas, Romaneios
from veiculos.models import CategoriaVeiculo, Veiculo

from minutas.forms import (
    CadastraMinutaKMFinal,
    CadastraMinutaKMInicial,
    CadastraMinutaHoraFinal,
)
from minutas.models import (
    Minuta,
    MinutaColaboradores,
    MinutaItens,
    MinutaNotas,
)
from minutas.itens_card import criar_itens_card_minuta


def string_to_decimal(string):
    converte = decimal.Decimal(string.replace(".", "").replace(",", "."))
    return converte


def string_to_timedelta(string):
    hora_datetime = datetime.strptime(string, "%H:%M")
    hora_timedelta = timedelta(
        days=0, hours=hora_datetime.hour, minutes=hora_datetime.minute
    )
    return hora_timedelta


def nome_curto(nome):
    apelido = nome
    if nome:
        apelido = nome.split()
    if len(apelido) > 2:
        if len(apelido[1]) > 2:
            del apelido[2:]
        else:
            del apelido[3:]
        apelido = " ".join(apelido)
    else:
        apelido = nome
    return apelido


def nome_curto_underscore(nome):
    apelido = nome
    if nome:
        apelido = nome.split()
    if len(apelido) > 2:
        if len(apelido[1]) > 2:
            del apelido[2:]
        else:
            del apelido[3:]
        apelido = "_".join(apelido)
    else:
        apelido = "_".join(apelido)
    return apelido


class MinutaSelecionada:
    def __init__(self, idminuta):
        minuta = Minuta.objects.get(idMinuta=idminuta)
        self.idminuta = minuta.idMinuta
        self.numero = minuta.Minuta
        self.data = minuta.DataMinuta
        self.hora_inicial = minuta.HoraInicial
        self.hora_final = minuta.HoraFinal
        self.coleta = minuta.Coleta
        self.entrega = minuta.Entrega
        self.obs = minuta.Obs
        self.idcliente = minuta.idCliente.idCliente
        self.cliente = minuta.idCliente.Fantasia
        self.motorista = MinutaMotorista(idminuta).nome
        self.ajudantes = MinutaAjudantes(idminuta).nome
        self.ajudante_avulso = self.get_ajudante_avulso()
        self.veiculo_solicitado = minuta.idCategoriaVeiculo
        self.veiculo = minuta.idVeiculo
        self.km_inicial = minuta.KMInicial
        self.km_final = minuta.KMFinal
        self.despesas = MinutaDespesa(idminuta).descricao
        self.t_despesas = self.total_despesas()
        self.entregas = MinutaEntrega(idminuta).nota
        self.quantidade_entregas = self.get_quantidade_entregas()
        self.t_entregas = self.total_notas()
        self.perimetro = self.get_perimetro()
        self.romaneio = self.get_romaneio()
        self.romaneio_pesos = self.get_romaneio_pesos()
        self.tabela = ClienteTabela(minuta.idCliente).tabela
        self.tabela_veiculo = ClienteTabelaVeiculo(minuta.idCliente).tabela
        self.tabela_perimetro = ClienteTabelaPerimetro(minuta.idCliente).tabela
        self.tabela_capacidade = ClienteTabelaCapacidade(
            minuta.idCliente
        ).tabela
        self.total_horas = self.get_total_horas()
        self.total_horas_str = self.get_total_horas_str()
        self.total_kms = self.get_total_kms()
        self.CategoriaDespesa = MinutaCategoriaDespesas().Categoria
        self.proxima_saida = self.entrega_saida()
        self.status_minuta = minuta.StatusMinuta
        self.paga = self.carrega_valores_paga()
        self.paga_motorista = self.valor_total_motorista()
        self.paga_minuta = self.valor_total_minuta()
        self.paga_realizada_motorista = self.verifica_pagamento_motorista()
        self.paga_realizada_ajudantes = self.verifica_pagamento_ajudantes()
        self.recebe = self.carrega_valores_recebe()
        self.recebe_minuta = self.valor_recebe_total_minuta()
        self.recebe_realizada = self.verifica_recebimentos()
        self.fatura = minuta.idFatura
        self.valor_minuta = minuta.Valor

    def get_total_kms(self):
        calculo_kms = self.km_final - self.km_inicial
        if calculo_kms < 1:
            calculo_kms = 0
        return calculo_kms

    def get_romaneio(self):
        romaneio = Romaneios.objects.filter(idMinuta_id=self.idminuta)
        num_romaneio = []
        for i in romaneio:
            num_romaneio.append(i.Romaneio)
        return num_romaneio

    def get_romaneio_pesos(self):
        romaneios = self.romaneio
        lista_romaneio_peso = []
        for i in romaneios:
            peso = RomaneioNotas.objects.filter(idRomaneio=i).aggregate(
                peso=Sum("idNotasClientes__Peso")
            )
            lista_romaneio_peso.append({"romaneio": i, "peso": peso["peso"]})
        return lista_romaneio_peso

    def total_ajudantes(self):
        self.total_ajudantes_avulso()
        total_ajudantes = len(self.ajudantes)
        return total_ajudantes

    def total_ajudantes_avulso(self):
        total_ajudantes_avulso = len(self.ajudantes)
        for itens in self.ajudantes:
            if itens["tipo"] == "MENSALISTA":
                total_ajudantes_avulso += -1
        return total_ajudantes_avulso

    def extra_ajudante_cobra(self):
        total_horas = self.get_total_horas()
        dezhoras = timedelta(days=0, hours=10, minutes=0)
        fator = 0.00
        recebe_extra_ajudante = float(self.tabela[0]["AjudanteCobra"])
        if total_horas < dezhoras:
            horas = str(total_horas)[0:1]
        else:
            horas = str(total_horas)[0:2]
        minutos = str(total_horas)[3:5]
        if total_horas > dezhoras:
            fator_minuto = [1, 16, 31, 46, 59]
            fator_decimal = [0.00, 0.25, 0.50, 0.75, 1.00]
            for index, itens in enumerate(fator_minuto):
                if int(minutos) < itens:
                    fator = fator_decimal[index]
                    break
            recebe_extra_ajudante = (
                float(self.tabela[0]["AjudanteCobraHoraExtra"]) * fator
            )
            recebe_extra_ajudante += float(
                self.tabela[0]["AjudanteCobraHoraExtra"]
            ) * (int(horas) - 10)
            recebe_extra_ajudante += float(self.tabela[0]["AjudanteCobra"])
        return recebe_extra_ajudante

    def saidas_ajudante(self):
        if self.ajudantes:
            saidas = len(self.entregas)
            return saidas

    def get_ajudante_avulso(self):
        ajudantes = self.ajudantes
        lista_tipo_pgto = []
        for i in ajudantes:
            lista_tipo_pgto.append(i["tipo"])
        if "SAIDA" in lista_tipo_pgto or "MINUTA" in lista_tipo_pgto:
            return True

    def get_total_horas(self):
        periodo = timedelta(hours=0, minutes=0)
        if self.hora_final:
            inicial = datetime.combine(self.data, self.hora_inicial)
            final = datetime.combine(self.data, self.hora_final)
            if inicial < final:
                periodo = final - inicial
        return periodo

    def get_total_horas_str(self):
        total_horas_str = str(self.total_horas)
        if total_horas_str.__len__() == 7:
            total_horas_str = f"0{total_horas_str}"
        total_horas_str = total_horas_str[0:5]
        return total_horas_str

    def horas_excede(self):
        excede = timedelta(hours=0, minutes=0)
        minimo = timedelta(hours=0, minutes=0)
        periodo = self.get_total_horas()
        filtro_tabela_veiculo = self.filtro_tabela_veiculo()
        if filtro_tabela_veiculo:
            minimo = timedelta(
                days=0,
                hours=filtro_tabela_veiculo["HoraMinimo"].hour,
                minutes=filtro_tabela_veiculo["HoraMinimo"].minute,
            )
        if periodo > minimo:
            excede = periodo - minimo
        excede_str = str(excede)
        excede = datetime.strptime(excede_str, "%H:%M:%S")
        return excede

    def get_quantidade_entregas(self):
        entregas = self.entregas
        lista = [x["NotaGuia"] for x in entregas]
        nova_lista = [x for x in lista if x == "0"]
        return len(nova_lista)

    def get_perimetro(self):
        perimetro = (
            MinutaNotas.objects.values("Cidade")
            .filter(idMinuta=self.idminuta)
            .exclude(Cidade="SÃO PAULO")
        )
        return True if perimetro else False

    def total_notas(self):
        totais = dict()
        totais["valor_entregas"] = sum(
            [itens["ValorNota"] for itens in self.entregas]
        )
        totais["volume_entregas"] = sum(
            [itens["Volume"] for itens in self.entregas]
        )
        totais["peso_entregas"] = sum(
            [itens["Peso"] for itens in self.entregas]
        )
        totais["total_entregas"] = len(self.entregas)
        return totais

    def total_despesas(self):
        d_total_despesas = dict()
        d_total_despesas["valor_despesas"] = sum(
            [itens["Valor"] for itens in self.despesas]
        )
        d_total_despesas["total_despesas"] = len(self.despesas)
        return d_total_despesas

    @staticmethod
    def saldo_porcentagem_nota(porcento, valor):
        porcentagem = porcento
        total_notas = valor
        saldo = total_notas * porcentagem / 100
        return saldo

    def filtro_tabela_veiculo(self):
        filtro_tabela_veiculo = [
            itens
            for itens in self.tabela_veiculo
            if itens["idCategoriaVeiculo"] == self.veiculo_solicitado
        ]
        if filtro_tabela_veiculo:
            return filtro_tabela_veiculo[0]

    def entrega_saida(self):
        lista_notas = [itens["Nota"] for itens in self.entregas]
        lista_saida = list(filter(lambda itens: "SAIDA" in itens, lista_notas))
        numero_saidas = len(lista_saida)
        proxima_saida = f"{numero_saidas + 1}ª SAIDA"
        return proxima_saida

    def carrega_valores_paga(self):
        v_paga = cria_dict_paga()
        tabela_veiculo = self.filtro_tabela_veiculo()
        capacidade = [
            itens["CapacidadePaga"]
            for itens in self.tabela_capacidade
            if itens["CapacidadeInicial"]
            # Verificar peso total 12/06/2024
            #  <= self.total_kms()
            <= itens["CapacidadeFinal"]
        ]
        perimetro = [
            itens["PerimetroPaga"]
            for itens in self.tabela_perimetro
            if itens["PerimetroInicial"]
            <= self.get_total_kms()
            <= itens["PerimetroFinal"]
        ]
        phkesc = self.tabela[0]["phkescPaga"]
        if tabela_veiculo:
            if self.motorista:
                if self.motorista[0]["obj"].TipoPgto != "MENSALISTA":
                    v_paga["v_porc"] = tabela_veiculo["PorcentagemPaga"]
                    v_paga["m_porc"] = self.t_entregas["valor_entregas"]
                    v_paga["t_porc"] = (
                        tabela_veiculo["PorcentagemPaga"]
                        / 100
                        * v_paga["m_porc"]
                    )
                    v_paga["c_porc"] = True if int(phkesc[0:1]) else False
                    v_paga["v_hora"] = self.filtro_tabela_veiculo()["HoraPaga"]
                    v_paga["m_hora"] = self.filtro_tabela_veiculo()[
                        "HoraMinimo"
                    ]
                    v_paga["t_hora"] = calcula_valor_hora(
                        100, v_paga["m_hora"], v_paga["v_hora"]
                    )
                    v_paga["c_hora"] = True if int(phkesc[1:2]) else False
                    v_paga["v_exce"] = 100
                    v_paga["m_exce"] = self.horas_excede().time()
                    v_paga["t_exce"] = calcula_valor_hora(
                        100, v_paga["m_exce"], v_paga["v_hora"]
                    )
                    v_paga["c_exce"] = True if int(phkesc[1:2]) else False
                    v_paga["v_kilm"] = self.filtro_tabela_veiculo()["KMPaga"]
                    v_paga["m_kilm"] = self.get_total_kms()
                    v_paga["t_kilm"] = (
                        self.filtro_tabela_veiculo()["KMPaga"]
                        * self.get_total_kms()
                    )
                    v_paga["c_kilm"] = True if int(phkesc[2:3]) else False
                    v_paga["v_entr"] = self.filtro_tabela_veiculo()[
                        "EntregaPaga"
                    ]
                    v_paga["m_entr"] = self.quantidade_entregas
                    v_paga["t_entr"] = (
                        self.filtro_tabela_veiculo()["EntregaPaga"]
                        * v_paga["m_entr"]
                    )
                    v_paga["c_entr"] = True if int(phkesc[3:4]) else False
                    v_paga["v_enkg"] = self.filtro_tabela_veiculo()[
                        "EntregaKGPaga"
                    ]
                    v_paga["m_enkg"] = self.t_entregas["peso_entregas"]
                    v_paga["t_enkg"] = (
                        self.filtro_tabela_veiculo()["EntregaKGPaga"]
                        * v_paga["m_enkg"]
                    )
                    v_paga["c_enkg"] = True if int(phkesc[4:5]) else False
                    v_paga["v_evol"] = self.filtro_tabela_veiculo()[
                        "EntregaVolumePaga"
                    ]
                    v_paga["m_evol"] = self.t_entregas["volume_entregas"]
                    v_paga["t_evol"] = (
                        self.filtro_tabela_veiculo()["EntregaVolumePaga"]
                        * v_paga["m_evol"]
                    )
                    v_paga["c_evol"] = True if int(phkesc[5:6]) else False
                    v_paga["v_said"] = self.filtro_tabela_veiculo()[
                        "SaidaPaga"
                    ]
                    v_paga["c_said"] = True if int(phkesc[6:7]) else False
                    if capacidade:
                        v_paga["v_capa"] = capacidade[0]
                    v_paga["c_capa"] = True if int(phkesc[7:8]) else False
                    if perimetro:
                        v_paga["v_peri"] = perimetro[0]
                        v_paga["c_peri"] = True
                    v_paga = self.base_valor_perimetro(v_paga)
                    v_paga["t_peri"] = (
                        float(v_paga["v_peri"]) / 100 * float(v_paga["m_peri"])
                    )
                    v_paga["m_pnoi"] = v_paga["m_peri"]
        if self.total_ajudantes_avulso() > 0:
            v_paga["v_ajud"] = float(self.tabela[0]["AjudantePaga"])
            if int(self.entrega_saida()[0:1]) > 2:
                v_paga["v_ajud"] = (
                    float(self.tabela[0]["AjudantePaga"]) + 10.00
                )
            v_paga["m_ajud"] = self.total_ajudantes_avulso()
            v_paga["t_ajud"] = v_paga["v_ajud"] * self.total_ajudantes_avulso()
            v_paga["c_ajud"] = True
        return v_paga

    @staticmethod
    def base_valor_perimetro(v_paga):
        total = 0
        total += float(v_paga["t_porc"])
        total += float(v_paga["t_hora"])
        total += float(v_paga["t_exce"])
        total += float(v_paga["t_kilm"])
        total += float(v_paga["t_entr"])
        total += float(v_paga["t_enkg"])
        total += float(v_paga["t_evol"])
        total += float(v_paga["v_said"])
        total += float(v_paga["v_capa"])
        v_paga["m_peri"] = total
        v_paga["m_pnoi"] = total
        return v_paga

    def valor_total_motorista(self):
        v_paga = self.paga
        total = 0
        total += float(v_paga["m_peri"])
        total += float(v_paga["t_peri"])
        total += float(v_paga["t_pnoi"])
        return total

    def valor_total_minuta(self):
        v_paga = self.paga
        total = 0
        total += float(v_paga["m_peri"])
        total += float(v_paga["t_peri"])
        total += float(v_paga["t_pnoi"])
        total += float(v_paga["t_ajud"])
        return total

    def carrega_valores_recebe(self):
        v_recebe = cria_dict_recebe()
        tabela_veiculo = self.filtro_tabela_veiculo()
        recebe_perimetro = self.perimetro
        peso_recebe = self.t_entregas["peso_entregas"]
        if self.romaneio_pesos:
            maior = max(self.romaneio_pesos, key=lambda x: x["peso"])
            if maior:
                peso_recebe = maior["peso"]
        capacidade = [
            itens["CapacidadeCobra"]
            for itens in self.tabela_capacidade
            if itens["CapacidadeInicial"]
            # Verificar peso total 12/06/2024
            <= peso_recebe <= itens["CapacidadeFinal"]
        ]
        perimetro = [
            itens["PerimetroCobra"]
            for itens in self.tabela_perimetro
            if itens["PerimetroInicial"]
            <= self.get_total_kms()
            <= itens["PerimetroFinal"]
        ]
        phkesc = self.tabela[0]["phkescCobra"]
        # TODO Removido a multiplcação da taxa de expedição pelo numero de romaneios 15/05/2023
        # Ativado novamente em 10/01/2024, colocar parametro para usurio selecionar se cobra ou não
        if len(self.romaneio) > 1:
            v_recebe["v_taxa"] = self.tabela[0]["TaxaExpedicao"] * len(
                self.romaneio
            )
        else:
            v_recebe["v_taxa"] = self.tabela[0]["TaxaExpedicao"]
        v_recebe["c_taxa"] = self.tabela[0]["TaxaExpedicao"] > 0
        if tabela_veiculo:
            if self.motorista:
                v_recebe["v_segu"] = self.tabela[0]["Seguro"]
                v_recebe["m_segu"] = self.t_entregas["valor_entregas"]
                v_recebe["t_segu"] = (
                    float(v_recebe["v_segu"]) / 100 * float(v_recebe["m_segu"])
                )
                v_recebe["c_segu"] = self.t_entregas["valor_entregas"] > 0
                v_recebe["v_porc"] = tabela_veiculo["PorcentagemCobra"]
                v_recebe["m_porc"] = self.t_entregas["valor_entregas"]
                v_recebe["t_porc"] = (
                    tabela_veiculo["PorcentagemCobra"]
                    / 100
                    * v_recebe["m_porc"]
                )
                v_recebe["c_porc"] = bool(int(phkesc[0:1]))
                v_recebe["v_pohe"] = 100
                v_recebe["m_pohe"] = self.horas_excede().time()
                v_recebe["t_pohe"] = calcula_valor_hora(
                    100, v_recebe["m_pohe"], v_recebe["t_porc"] / 10
                )
                v_recebe["c_pohe"] = bool(int(phkesc[0:1]))
                v_recebe["v_hora"] = self.filtro_tabela_veiculo()["HoraCobra"]
                v_recebe["m_hora"] = self.filtro_tabela_veiculo()["HoraMinimo"]
                v_recebe["t_hora"] = calcula_valor_hora(
                    100, v_recebe["m_hora"], v_recebe["v_hora"]
                )
                v_recebe["c_hora"] = bool(int(phkesc[1:2]))
                v_recebe["v_exce"] = 100
                v_recebe["m_exce"] = self.horas_excede().time()
                v_recebe["t_exce"] = calcula_valor_hora(
                    100, v_recebe["m_exce"], v_recebe["v_hora"]
                )
                v_recebe["c_exce"] = bool(int(phkesc[1:2]))
                v_recebe["v_kilm"] = self.filtro_tabela_veiculo()["KMCobra"]
                v_recebe["m_kilm"] = self.get_total_kms()
                v_recebe["t_kilm"] = (
                    self.filtro_tabela_veiculo()["KMCobra"]
                    * self.get_total_kms()
                )
                v_recebe["c_kilm"] = bool(int(phkesc[2:3]))
                v_recebe["v_kihe"] = 100
                v_recebe["m_kihe"] = self.horas_excede().time()
                v_recebe["t_kihe"] = calcula_valor_hora(
                    100, v_recebe["m_kihe"], v_recebe["t_kilm"] / 10
                )
                v_recebe["c_kihe"] = bool(int(phkesc[2:3]))
                v_recebe["v_entr"] = self.filtro_tabela_veiculo()[
                    "EntregaCobra"
                ]
                v_recebe["m_entr"] = self.quantidade_entregas
                v_recebe["t_entr"] = (
                    self.filtro_tabela_veiculo()["EntregaCobra"]
                    * v_recebe["m_entr"]
                )
                v_recebe["c_entr"] = bool(int(phkesc[3:4]))
                v_recebe["v_enhe"] = 100
                v_recebe["m_enhe"] = self.horas_excede().time()
                v_recebe["t_enhe"] = calcula_valor_hora(
                    100, v_recebe["m_enhe"], v_recebe["t_entr"] / 10
                )
                v_recebe["c_enhe"] = bool(int(phkesc[3:4]))
                v_recebe["v_enkg"] = self.filtro_tabela_veiculo()[
                    "EntregaKGCobra"
                ]
                v_recebe["m_enkg"] = peso_recebe
                v_recebe["t_enkg"] = (
                    self.filtro_tabela_veiculo()["EntregaKGCobra"]
                    * v_recebe["m_enkg"]
                )
                v_recebe["c_enkg"] = bool(int(phkesc[6:7]))
                v_recebe["v_ekhe"] = 100
                v_recebe["m_ekhe"] = self.horas_excede().time()
                v_recebe["t_ekhe"] = calcula_valor_hora(
                    100, v_recebe["m_ekhe"], v_recebe["t_enkg"] / 10
                )
                v_recebe["c_ekhe"] = bool(int(phkesc[6:7]))
                v_recebe["v_evol"] = self.filtro_tabela_veiculo()[
                    "EntregaVolumeCobra"
                ]
                v_recebe["m_evol"] = self.t_entregas["volume_entregas"]
                v_recebe["t_evol"] = (
                    self.filtro_tabela_veiculo()["EntregaVolumeCobra"]
                    * v_recebe["m_evol"]
                )
                v_recebe["c_evol"] = bool(int(phkesc[7:8]))
                v_recebe["v_evhe"] = 100
                v_recebe["m_evhe"] = self.horas_excede().time()
                v_recebe["t_evhe"] = calcula_valor_hora(
                    100, v_recebe["m_evhe"], v_recebe["t_evol"] / 10
                )
                v_recebe["c_evhe"] = bool(int(phkesc[7:8]))
                v_recebe["v_said"] = self.filtro_tabela_veiculo()["SaidaCobra"]
                v_recebe["c_said"] = bool(int(phkesc[4:5]))
                v_recebe["v_sahe"] = 100
                v_recebe["m_sahe"] = self.horas_excede().time()
                v_recebe["t_sahe"] = calcula_valor_hora(
                    100, v_recebe["m_sahe"], v_recebe["v_said"] / 10
                )
                v_recebe["c_sahe"] = bool(int(phkesc[4:5]))
                if capacidade:
                    v_recebe["v_capa"] = capacidade[0]
                v_recebe["c_capa"] = bool(int(phkesc[5:6]))
                v_recebe["v_cahe"] = 100
                v_recebe["m_cahe"] = self.horas_excede().time()
                v_recebe["t_cahe"] = calcula_valor_hora(
                    100, v_recebe["m_cahe"], v_recebe["v_capa"] / 10
                )
                v_recebe["c_cahe"] = bool(int(phkesc[5:6]))
                if perimetro and recebe_perimetro:
                    v_recebe["v_peri"] = perimetro[0]
                    v_recebe["c_peri"] = True
                v_recebe = self.base_valor_perimetro(v_recebe)
                v_recebe["t_peri"] = (
                    float(v_recebe["v_peri"]) / 100 * float(v_recebe["m_peri"])
                )
                v_recebe["v_pehe"] = 100
                v_recebe["m_pehe"] = self.horas_excede().time()
                v_recebe["t_pehe"] = calcula_valor_hora(
                    100, v_recebe["m_pehe"], v_recebe["t_peri"] / 10
                )
                v_recebe["m_pnoi"] = v_recebe["m_peri"]
        if self.total_ajudantes() > 0:
            """Valor a ser cobrado de cada ajudante, o valor era recuperado
            da tabela (self.tabela[0]["AjudanteCobra"]), mas passou a ser cobrado
            pelo valor retornado do metodo self.extra_ajudante_cobra()), que já
            verifica e retorna o valor com as horas extra se tiver ou retirna o
            valor da tabela. 19/07/2023.
            """
            v_recebe["v_ajud"] = float(self.tabela[0]["AjudanteCobra"])
            v_recebe["v_ajud"] = float(self.extra_ajudante_cobra())
            v_recebe["m_ajud"] = self.total_ajudantes()
            v_recebe["t_ajud"] = v_recebe["v_ajud"] * v_recebe["m_ajud"]
            v_recebe["c_ajud"] = True
        return v_recebe

    def valor_recebe_total_minuta(self):
        v_recebe = self.recebe
        total = 0
        total += float(v_recebe["v_taxa"])
        total += float(v_recebe["t_segu"])
        total += float(v_recebe["t_porc"])
        total += float(v_recebe["t_hora"])
        total += float(v_recebe["t_exce"])
        total += float(v_recebe["t_kilm"])
        total += float(v_recebe["t_entr"])
        total += float(v_recebe["t_enkg"])
        total += float(v_recebe["t_evol"])
        total += float(v_recebe["v_said"])
        total += float(v_recebe["v_capa"])
        total += float(v_recebe["t_peri"])
        total += float(v_recebe["t_pnoi"])
        total += float(v_recebe["t_ajud"])
        total += float(self.t_despesas["valor_despesas"])
        return total

    def verifica_pagamento_motorista(self):
        pagamentos = MinutaItens.objects.filter(
            TipoItens="PAGA",
            idMinuta=self.idminuta,
        ).exclude(Descricao="AJUDANTE")
        return True if pagamentos else False

    def verifica_pagamento_ajudantes(self):
        pagamentos = MinutaItens.objects.filter(
            TipoItens="PAGA",
            Descricao="AJUDANTE",
            idMinuta=self.idminuta,
        )
        lista = [
            {
                "idminutaitens": i.idMinutaItens,
                "valorbase": i.ValorBase,
            }
            for i in pagamentos
        ]
        return lista

    def verifica_recebimentos(self):
        recebe = MinutaItens.objects.filter(
            TipoItens="RECEBE", idMinuta=self.idminuta
        )
        return True if recebe else False


class MinutaMotorista:
    def __init__(self, idminuta):
        self.nome = self.get_motorista(idminuta)

    @staticmethod
    def get_motorista(idminuta):
        motorista = MinutaColaboradores.objects.filter(
            idMinuta=idminuta, Cargo="MOTORISTA"
        )
        lista = [
            {
                "idMinutaColaboradores": itens.idMinutaColaboradores,
                "nome": itens.idPessoal.Nome,
                "obj": itens.idPessoal,
            }
            for itens in motorista
        ]
        if lista:
            lista[0]["apelido"] = nome_curto(lista[0]["nome"])
        return lista


class MinutaAjudantes:
    def __init__(self, idminuta):
        self.nome = self.get_ajudantes(idminuta)

    @staticmethod
    def get_ajudantes(idminuta):
        ajudantes = MinutaColaboradores.objects.filter(
            idMinuta=idminuta, Cargo="AJUDANTE"
        ).order_by("idPessoal")
        lista = [
            {
                "idMinutaColaboradores": itens.idMinutaColaboradores,
                "nome": itens.idPessoal.Nome,
                "tipo": itens.idPessoal.TipoPgto,
            }
            for itens in ajudantes
        ]
        if lista:
            for index, itens in enumerate(lista):
                lista[index]["apelido"] = nome_curto(lista[index]["nome"])
        return lista


class MinutaDespesa:
    def __init__(self, idminuta):
        self.descricao = self.get_despesas(idminuta)

    @staticmethod
    def get_despesas(idminuta):
        despesas = MinutaItens.objects.filter(
            idMinuta=idminuta, TipoItens="DESPESA"
        )
        lista = [
            {
                "idMinutaItens": itens.idMinutaItens,
                "Descricao": itens.Descricao,
                "Valor": itens.Valor,
                "Obs": itens.Obs,
            }
            for itens in despesas
        ]
        return lista


class MinutaCategoriaDespesas:
    def __init__(self):
        self.Categoria = self.get_despesas_descricao()

    @staticmethod
    def get_despesas_descricao():
        categoria = (
            MinutaItens.objects.filter(TipoItens="DESPESA")
            .values("Descricao")
            .distinct()
            .order_by("Descricao")
        )
        return categoria


class MinutaEntrega:
    def __init__(self, idminuta):
        self.nota = self.get_entregas(idminuta)

    @staticmethod
    def get_entregas(idminuta):
        entregas = MinutaNotas.objects.filter(idMinuta=idminuta)
        lista = [
            {
                "idMinutaNotas": itens.idMinutaNotas,
                "Nota": itens.Nota,
                "ValorNota": itens.ValorNota,
                "Peso": itens.Peso,
                "Volume": itens.Volume,
                "Nome": itens.Nome,
                "NotaGuia": itens.NotaGuia,
                "Bairro": itens.Bairro,
                "Cidade": itens.Cidade,
                "Estado": itens.Estado,
            }
            for itens in entregas
        ]
        return lista


class ClienteTabela:
    def __init__(self, idcliente):
        self.tabela = self.get_tabela(idcliente)

    @staticmethod
    def get_tabela(idcliente):
        tabelas = Tabela.objects.filter(idCliente=idcliente)
        lista = [
            {
                "idTabela": itens.idTabela,
                "Comissao": itens.Comissao,
                "Seguro": itens.Seguro,
                "TaxaExpedicao": itens.TaxaExpedicao,
                "AjudanteCobra": itens.AjudanteCobra,
                "AjudanteCobraHoraExtra": itens.AjudanteCobraHoraExtra,
                "AjudantePaga": itens.AjudantePaga,
                "phkescCobra": itens.phkescCobra,
                "phkescPaga": itens.phkescPaga,
                "idFormaPagamento": itens.idFormaPagamento,
            }
            for itens in tabelas
        ]
        return lista


class ClienteTabelaVeiculo:
    def __init__(self, idcliente):
        self.tabela = self.get_tabela_veiculo(idcliente)

    @staticmethod
    def get_tabela_veiculo(idcliente):
        veiculos = TabelaVeiculo.objects.filter(idCliente=idcliente)
        lista = [
            {
                "idTabelaVeiculo": itens.idTabelaVeiculo,
                "idCategoriaVeiculo": itens.idCategoriaVeiculo,
                "PorcentagemCobra": itens.PorcentagemCobra,
                "PorcentagemPaga": itens.PorcentagemPaga,
                "HoraCobra": itens.HoraCobra,
                "HoraPaga": itens.HoraPaga,
                "HoraMinimo": itens.HoraMinimo,
                "KMCobra": itens.KMCobra,
                "KMPaga": itens.KMPaga,
                "KMMinimo": itens.KMMinimo,
                "EntregaCobra": itens.EntregaCobra,
                "EntregaPaga": itens.EntregaPaga,
                "EntregaKGCobra": itens.EntregaKGCobra,
                "EntregaKGPaga": itens.EntregaKGPaga,
                "EntregaVolumeCobra": itens.EntregaVolumeCobra,
                "EntregaVolumePaga": itens.EntregaVolumePaga,
                "EntregaMinimo": itens.EntregaMinimo,
                "SaidaCobra": itens.SaidaCobra,
                "SaidaPaga": itens.SaidaPaga,
            }
            for itens in veiculos
        ]
        return lista


class ClienteTabelaPerimetro:
    def __init__(self, idcliente):
        self.tabela = self.get_tabela_perimetro(idcliente)

    @staticmethod
    def get_tabela_perimetro(idcliente):
        perimetros = TabelaPerimetro.objects.filter(idCliente=idcliente)
        lista = [
            {
                "idTabelaPerimetro": itens.idTabelaPerimetro,
                "PerimetroInicial": itens.PerimetroInicial,
                "PerimetroFinal": itens.PerimetroFinal,
                "PerimetroCobra": itens.PerimetroCobra,
                "PerimetroPaga": itens.PerimetroPaga,
            }
            for itens in perimetros
        ]
        return lista


class ClienteTabelaCapacidade:
    def __init__(self, idcliente):
        self.tabela = self.get_tabela_capacidade(idcliente)

    @staticmethod
    def get_tabela_capacidade(idcliente):
        capacidades = TabelaCapacidade.objects.filter(idCliente=idcliente)
        lista = [
            {
                "idTabelaCapacidade": itens.idTabelaCapacidade,
                "CapacidadeInicial": itens.CapacidadeInicial,
                "CapacidadeFinal": itens.CapacidadeFinal,
                "CapacidadeCobra": itens.CapacidadeCobra,
                "CapacidadePaga": itens.CapacidadePaga,
            }
            for itens in capacidades
        ]
        return lista


class MinutasStatus:
    def __init__(self, status_minuta):
        self.minutas = self.get_minutas_abertas(status_minuta)

    @staticmethod
    def get_minutas_abertas(status_minuta):
        abertas = Minuta.objects.filter(StatusMinuta=status_minuta).order_by(
            "-Minuta"
        )
        lista = [
            {
                "idMinuta": m.idMinuta,
                "Minuta": m.Minuta,
                "Cliente": m.idCliente,
                "Data": m.DataMinuta,
                "Hora": m.HoraInicial,
                "Veiculo": m.idVeiculo,
                "status": m.StatusMinuta,
            }
            for m in abertas
        ]
        for x in lista:
            if x["Veiculo"]:
                x["Veiculo"] = f"{x['Veiculo'].Modelo} - {x['Veiculo'].Placa}"
            motorista = MinutaColaboradores.objects.filter(
                idMinuta_id=x["idMinuta"], Cargo="MOTORISTA"
            )
            if motorista:
                x["Motorista"] = nome_curto(motorista[0].idPessoal.Nome)
            else:
                x["Motorista"] = None
        return lista


def filtro_clientes():
    filtro = (
        Minuta.objects.all()
        .order_by("idCliente__Fantasia")
        .values("idCliente__Fantasia")
        .distinct()
    )
    return filtro


def filtro_colaboradores():
    filtro = (
        MinutaColaboradores.objects.all()
        .order_by("idPessoal__Nome")
        .values("idPessoal__Nome")
        .distinct()
    )
    return filtro


def filtro_veiculos():
    filtro = (
        Minuta.objects.all()
        .order_by("idVeiculo__Marca", "idVeiculo__Modelo", "idVeiculo__Placa")
        .values("idVeiculo__Marca", "idVeiculo__Modelo", "idVeiculo__Placa")
        .distinct()
    )
    return filtro


def filtro_cidades():
    filtro = (
        MinutaNotas.objects.all()
        .values("Cidade", "Estado")
        .order_by("Cidade", "Estado")
        .distinct()
    )
    return filtro


def filtra_consulta(request, filtro, filtro_consulta, meses, anos):
    data = dict()
    dia_hoje = date.today()
    if not meses:
        meses = 0
    if not anos:
        anos = 100
    mes_anterior = dia_hoje - relativedelta(
        years=int(anos), months=int(meses), day=1
    )
    lista = []
    if filtro_consulta == "Clientes":
        minutas = Minuta.objects.filter(
            idCliente__Fantasia=filtro, DataMinuta__gte=mes_anterior
        ).order_by("-DataMinuta")
        lista = [
            {
                "idMinuta": m.idMinuta,
                "Minuta": m.Minuta,
                "Cliente": m.idCliente,
                "Data": m.DataMinuta,
                "Hora": m.HoraInicial,
                "Veiculo": m.idVeiculo,
                "status": m.StatusMinuta,
            }
            for m in minutas
        ]
    elif filtro_consulta == "Colaboradores":
        minutas = MinutaColaboradores.objects.filter(
            idPessoal__Nome=filtro, idMinuta_id__DataMinuta__gte=mes_anterior
        ).order_by("-idMinuta__DataMinuta")
        lista_base = [
            {
                "idMinuta": m.idMinuta_id,
                "Minuta": m.idMinuta.Minuta,
                "Cliente": m.idMinuta.idCliente,
                "Data": m.idMinuta.DataMinuta,
                "Hora": m.idMinuta.HoraInicial,
                "Veiculo": m.idMinuta.idVeiculo,
                "status": m.idMinuta.StatusMinuta,
            }
            for m in minutas
        ]
        lista = {x["idMinuta"]: x for x in lista_base}.values()
    elif filtro_consulta == "Veiculos":
        minutas = Minuta.objects.filter(
            idVeiculo__Placa=filtro, DataMinuta__gte=mes_anterior
        ).order_by("-DataMinuta")
        lista = [
            {
                "idMinuta": m.idMinuta,
                "Minuta": m.Minuta,
                "Cliente": m.idCliente,
                "Data": m.DataMinuta,
                "Hora": m.HoraInicial,
                "Veiculo": m.idVeiculo,
                "status": m.StatusMinuta,
            }
            for m in minutas
        ]
    elif filtro_consulta == "Entregas_Cidades":
        local = filtro.split(" *** ")
        minutas = MinutaNotas.objects.filter(
            Cidade=local[0],
            Estado=local[1],
            idMinuta_id__DataMinuta__gte=mes_anterior,
        ).order_by("-idMinuta__DataMinuta")
        lista_base = [
            {
                "idMinuta": m.idMinuta_id,
                "Minuta": m.idMinuta.Minuta,
                "Cliente": m.idMinuta.idCliente,
                "Data": m.idMinuta.DataMinuta,
                "Hora": m.idMinuta.HoraInicial,
                "Veiculo": m.idMinuta.idVeiculo,
                "status": m.idMinuta.StatusMinuta,
            }
            for m in minutas
        ]
        lista = {x["idMinuta"]: x for x in lista_base}.values()
    elif filtro_consulta == "Destinatarios":
        minutas = (
            MinutaNotas.objects.filter(
                Nome__contains=filtro,
                idMinuta_id__DataMinuta__gte=mes_anterior,
            )
            .order_by("-idMinuta__DataMinuta")
            .distinct()
        )
        lista_base = [
            {
                "idMinuta": m.idMinuta_id,
                "Minuta": m.idMinuta.Minuta,
                "Cliente": m.idMinuta.idCliente,
                "Data": m.idMinuta.DataMinuta,
                "Hora": m.idMinuta.HoraInicial,
                "Veiculo": m.idMinuta.idVeiculo,
                "status": m.idMinuta.StatusMinuta,
            }
            for m in minutas
        ]
        lista = {x["idMinuta"]: x for x in lista_base}.values()
    for x in lista:
        if x["Veiculo"]:
            x["Veiculo"] = f"{x['Veiculo'].Modelo} - {x['Veiculo'].Placa}"
        motorista = MinutaColaboradores.objects.filter(
            idMinuta_id=x["idMinuta"], Cargo="MOTORISTA"
        )
        if motorista:
            x["Motorista"] = nome_curto(motorista[0].idPessoal.Nome)
        else:
            x["Motorista"] = None
    t_lista = lista.__len__()
    contexto = {
        "lista": lista,
        "filtro": filtro,
        "filtro_consulta": filtro_consulta,
        "t_lista": t_lista,
    }
    data["html_filtra_minuta"] = render_to_string(
        "minutas/filtraminuta.html", contexto, request=request
    )
    c_return = JsonResponse(data)
    return c_return


def cria_dict_paga():
    """
    Cria um dicionario com valores zerados para pagamentos da minuta
    v_ = Valores das Tabelas do cliente
    m_ = Dados recuperados da Minuta
    t_ = total
    c_ = usado para configurar os checkbox do html
    porc = porcentagem, hora = hora minimo, exce = hora excedente, kilm = kilometragem, entr = entregas,
    enkg = entregas kg, evol = entregas volume, said = saida, capa = capacidade(peso), peri = perimetro,
    pnoi = pernoite, ajud = ajudante
    :return: dicionario v_paga = valores pagamento
    """
    hora_zero_time = datetime.strptime("00:00", "%H:%M").time()
    v_paga = dict(
        {
            "v_porc": 0.00,
            "m_porc": 0.00,
            "t_porc": 0.00,
            "v_hora": 0.00,
            "m_hora": hora_zero_time,
            "t_hora": 0.00,
            "v_exce": 0.00,
            "m_exce": hora_zero_time,
            "t_exce": 0.00,
            "v_kilm": 0.00,
            "m_kilm": 0.00,
            "t_kilm": 0.00,
            "v_entr": 0.00,
            "m_entr": 0.00,
            "t_entr": 0.00,
            "v_enkg": 0.00,
            "m_enkg": 0.00,
            "t_enkg": 0.00,
            "v_evol": 0.00,
            "m_evol": 0.00,
            "t_evol": 0.00,
            "v_said": 0.00,
            "v_capa": 0.00,
            "v_peri": 0.00,
            "m_peri": 0.00,
            "t_peri": 0.00,
            "v_pnoi": 0.00,
            "m_pnoi": 0.00,
            "t_pnoi": 0.00,
            "v_ajud": 0.00,
            "m_ajud": 0.00,
            "t_ajud": 0.00,
            "c_porc": False,
            "c_hora": False,
            "c_exce": False,
            "c_kilm": False,
            "c_entr": False,
            "c_enkg": False,
            "c_evol": False,
            "c_said": False,
            "c_capa": False,
            "c_peri": False,
            "c_pnoi": False,
            "c_ajud": False,
        }
    )
    return v_paga


def cria_dict_recebe():
    """
    Cria um dicionario com valores zerados para receitas da minuta
    v_ = Valores das Tabelas do cliente
    m_ = Dados recuperados da Minuta
    t_ = total
    c_ = usado para configurar os checkbox do html
    porc = porcentagem, hora = hora minimo, exce = hora excedente,
    kilm = kilometragem, entr = entregas, enkg = entregas kg,
    evol = entregas volume, said = saida, capa = capacidade(peso),
    peri = perimetro, pnoi = pernoite, ajud = ajudante
    :return: dicionario v_paga = valores pagamento
    """
    hora_zero_time = datetime.strptime("00:00", "%H:%M").time()
    v_recebe = dict(
        {
            "v_taxa": 0.00,
            "v_segu": 0.00,
            "m_segu": 0.00,
            "t_segu": 0.00,
            "v_porc": 0.00,
            "m_porc": 0.00,
            "t_porc": 0.00,
            "v_pohe": 0.00,
            "m_pohe": hora_zero_time,
            "t_pohe": 0.00,
            "v_hora": 0.00,
            "m_hora": hora_zero_time,
            "t_hora": 0.00,
            "v_exce": 0.00,
            "m_exce": hora_zero_time,
            "t_exce": 0.00,
            "v_kilm": 0.00,
            "m_kilm": 0.00,
            "t_kilm": 0.00,
            "v_kihe": 0.00,
            "m_kihe": hora_zero_time,
            "t_kihe": 0.00,
            "v_entr": 0.00,
            "m_entr": 0.00,
            "t_entr": 0.00,
            "v_enhe": 0.00,
            "m_enhe": hora_zero_time,
            "t_enhe": 0.00,
            "v_enkg": 0.00,
            "m_enkg": 0.00,
            "t_enkg": 0.00,
            "v_ekhe": 0.00,
            "m_ekhe": hora_zero_time,
            "t_ekhe": 0.00,
            "v_evol": 0.00,
            "m_evol": 0.00,
            "t_evol": 0.00,
            "v_evhe": 0.00,
            "m_evhe": hora_zero_time,
            "t_evhe": 0.00,
            "v_said": 0.00,
            "v_sahe": 0.00,
            "m_sahe": hora_zero_time,
            "t_sahe": 0.00,
            "v_capa": 0.00,
            "v_cahe": 0.00,
            "m_cahe": hora_zero_time,
            "t_cahe": 0.00,
            "v_peri": 0.00,
            "m_peri": 0.00,
            "t_peri": 0.00,
            "v_pehe": 0.00,
            "m_pehe": hora_zero_time,
            "t_pehe": 0.00,
            "v_pnoi": 0.00,
            "m_pnoi": 0.00,
            "t_pnoi": 0.00,
            "v_ajud": 0.00,
            "m_ajud": 0.00,
            "t_ajud": 0.00,
            "c_taxa": False,
            "c_segu": False,
            "c_porc": False,
            "c_pohe": False,
            "c_hora": False,
            "c_exce": False,
            "c_kilm": False,
            "c_kihe": False,
            "c_entr": False,
            "c_enhe": False,
            "c_enkg": False,
            "c_ekhe": False,
            "c_evol": False,
            "c_evhe": False,
            "c_said": False,
            "c_sahe": False,
            "c_capa": False,
            "c_cahe": False,
            "c_peri": False,
            "c_pehe": False,
            "c_pnoi": False,
            "c_ajud": False,
        }
    )
    return v_recebe


def novo_status_minuta(request, idminuta, novo_status):
    minuta = get_minuta(idminuta)
    obj = minuta
    obj.StatusMinuta = novo_status
    obj.save(update_fields=["StatusMinuta"])
    data = dict()
    data = html_checklist(request, data, idminuta)
    c_return = retorna_json(data)
    return c_return


def calcula_valor_hora(porcentagem, horas, valor):
    novo_valor = valor * porcentagem / 100
    valor_hora = float(round(novo_valor, 2))
    valor_minuto = float(round(novo_valor / 60, 5))
    total_valor_hora = horas.hour * valor_hora
    total_valor_minuto = horas.minute * valor_minuto
    total = total_valor_hora + total_valor_minuto
    return total


def get_minuta(idminuta):
    return Minuta.objects.get(idMinuta=idminuta)


def get_categoria(idcategoria):
    return CategoriaVeiculo.objects.get(idCategoria=idcategoria)


def get_cliente(idcliente):
    return Cliente.objects.get(idCliente=idcliente)


def proxima_minuta():
    numero_minuta = Minuta.objects.all().aggregate(Max("Minuta"))
    return int(numero_minuta["Minuta__max"]) + 1


def km_atual(idveiculo):
    km_final = Minuta.objects.filter(idVeiculo=idveiculo).aggregate(
        Max("KMFinal")
    )
    if not km_final["KMFinal__max"]:
        km_final["KMFinal__max"] = 0
    return km_final


def edita_veiculo_solicitado(request, idminuta, idcategoriaveiculo):
    obj = get_minuta(idminuta)
    categoria = get_categoria(idcategoriaveiculo)
    mensagem = None
    tipo_mensagem = None
    if categoria != obj.idCategoriaVeiculo:
        obj.idCategoriaVeiculo = categoria
        if obj.save(update_fields=["idCategoriaVeiculo"]):
            mensagem = "O VEICULO SOLICITADO FOI ATUALIZADA."
            tipo_mensagem = "SUCESSO"
    contexto = cria_contexto(idminuta)
    data = dict()
    data["html_mensagem"] = mensagem
    data["html_tipo_mensagem"] = tipo_mensagem
    data["html_veiculo"] = render_to_string(
        "minutas/html_card_minuta_veiculo.html", contexto, request=request
    )
    c_return = JsonResponse(data)
    return c_return


def cria_contexto(idminuta):
    s_minuta = MinutaSelecionada(idminuta)
    minuta = Minuta.objects.filter(idMinuta=idminuta)
    minutaform = get_object_or_404(minuta, idMinuta=idminuta)
    form_hora_final = CadastraMinutaHoraFinal(instance=minutaform)
    form_km_inicial = CadastraMinutaKMInicial(instance=minutaform)
    form_km_final = CadastraMinutaKMFinal(instance=minutaform)
    contexto = {
        "s_minuta": s_minuta,
        "form_hora_final": form_hora_final,
        "form_km_inicial": form_km_inicial,
        "form_km_final": form_km_final,
    }
    return contexto


def edita_hora_final(request, idminuta, hora_final):
    obj = get_minuta(idminuta)
    hora_final = datetime.strptime(hora_final, "%H:%M").time()
    if hora_final <= obj.HoraInicial:
        obj.HoraFinal = "00:00"
        mensagem = f"VOCÊ DIGITOU {hora_final}, MAS A HORA FINAL TEM QUE SER MAIOR QUE {obj.HoraInicial}."
        tipo_mensagem = "ERROR"
    else:
        obj.HoraFinal = hora_final
        mensagem = "A HORA FINAL FOI ATUALIZADA."
        tipo_mensagem = "SUCESSO"
    obj.save(update_fields=["HoraFinal"])
    s_minuta = MinutaSelecionada(idminuta)
    total_horas_str = s_minuta.total_horas_str
    data = dict()
    data["html_mensagem"] = mensagem
    data["html_tipo_mensagem"] = tipo_mensagem
    data["html_total_horas"] = f"{total_horas_str} Hs"
    data = html_recebimento(request, data, idminuta)
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, idminuta)
    c_return = JsonResponse(data)
    return c_return


def edita_km_inicial(request, idminuta, km_inicial):
    obj = get_minuta(idminuta)
    km_inicial = int(km_inicial)
    if km_inicial >= obj.KMFinal:
        obj.KMInicial = km_inicial
        obj.KMFinal = 0
        mensagem = "A KILOMETRAGEM INICIAL FOi ATUALIZADA, A KILOMETRAGEM FINAL FOI ZERADA"
        tipo_mensagem = "SUCESSO"
        obj.save(update_fields=["KMInicial", "KMFinal"])
    else:
        obj.KMInicial = km_inicial
        mensagem = "A KILOMETRAGEM INICIAL FOi ATUALIZADA."
        tipo_mensagem = "SUCESSO"
        obj.save(update_fields=["KMInicial"])
    s_minuta = MinutaSelecionada(idminuta)
    total_kms = s_minuta.total_kms
    data = dict()
    data["html_mensagem"] = mensagem
    data["html_tipo_mensagem"] = tipo_mensagem
    data["html_total_kms"] = f"{total_kms} KMs"
    data = html_recebimento(request, data, idminuta)
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, idminuta)
    c_return = JsonResponse(data)
    return c_return


def edita_km_final(request, idminuta, km_final):
    obj = get_minuta(idminuta)
    km_final = int(km_final)
    if km_final <= obj.KMInicial:
        obj.KMFinal = 0
        mensagem = f"VOCÊ DIGITOU {km_final}, MAS A KILOMETRAGEM FINAL TEM QUE SER MAIOR QUE {obj.KMInicial}."
        tipo_mensagem = "ERROR"
    else:
        obj.KMFinal = km_final
        mensagem = "A KILOMETRAGEM FINAL FOI ATUALIZADA."
        tipo_mensagem = "SUCESSO"
    obj.save(update_fields=["KMFinal"])
    s_minuta = MinutaSelecionada(idminuta)
    total_kms = s_minuta.total_kms
    data = dict()
    data["html_mensagem"] = mensagem
    data["html_tipo_mensagem"] = tipo_mensagem
    data["html_total_kms"] = f"{total_kms} KMs"
    data = html_recebimento(request, data, idminuta)
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, idminuta)
    c_return = JsonResponse(data)
    return c_return


def ajudantes_disponiveis(idminuta):
    # EXCLUI O COLABORADOR TRANSEFETIVA (Coringa)
    ajudantes_minuta = (
        MinutaColaboradores.objects.filter(
            idMinuta=idminuta,
            Cargo="AJUDANTE",
        )
        .exclude(idPessoal_id=17)
        .values("idPessoal")
    )
    ajudantes_pagos = MinutaItens.objects.filter(
        idMinuta=idminuta,
        Descricao="AJUDANTE",
        TipoItens="PAGA",
    )
    if ajudantes_pagos:
        pessoas = (
            Pessoal.objects.filter(
                StatusPessoal=True,
            )
            .exclude(idPessoal__in=ajudantes_minuta)
            .exclude(
                TipoPgto="MINUTA",
            )
            .exclude(
                TipoPgto="SAIDA",
            )
        )
    else:
        pessoas = Pessoal.objects.filter(StatusPessoal=True).exclude(
            idPessoal__in=ajudantes_minuta
        )
    return pessoas


def motoristas_disponiveis():
    pessoas = Pessoal.objects.filter(StatusPessoal=True).exclude(
        Categoria="AJUDANTE"
    )
    return pessoas


def veiculo_selecionado(idpessoal, idminuta):
    veiculo = Veiculo.objects.filter(Motorista=idpessoal)
    if len(veiculo) == 1:
        km_inicial = km_atual(veiculo[0])
        obj = get_minuta(idminuta)
        obj.idVeiculo = veiculo[0]
        obj.KMInicial = km_inicial["KMFinal__max"]
        obj.save(update_fields=["idVeiculo", "KMInicial"])


def filtra_veiculo(idpessoal, opcao):
    veiculos = []
    if opcao == "PROPRIO":
        veiculos = Veiculo.objects.filter(Motorista=idpessoal).order_by(
            "Marca", "Modelo", "Placa"
        )
    elif opcao == "TRANSPORTADORA":
        veiculos = Veiculo.objects.filter(Proprietario=17).order_by(
            "Marca", "Modelo", "Placa"
        )
    elif opcao == "CADASTRADOS":
        veiculos = Veiculo.objects.all().order_by("Marca", "Modelo", "Placa")
    lista_veiculos = []
    for veiculo in veiculos:
        descricao_veiculo = (
            f"{veiculo.Marca} - {veiculo.Modelo} - {veiculo.Placa}"
        )
        lista_veiculos.append(
            {"idVeiculo": veiculo.idVeiculo, "Veiculo": descricao_veiculo}
        )
    return lista_veiculos


def remove_colaborador(request, idminutacolaborador, idminuta, cargo):
    colaborador = MinutaColaboradores.objects.get(
        idMinutaColaboradores=idminutacolaborador
    )
    colaborador.delete()
    data = dict()
    if cargo == "AJUDANTE":
        data = html_ajudantes(request, data, idminuta)
    elif cargo == "MOTORISTA":
        obj = get_minuta(idminuta)
        obj.idVeiculo = None
        obj.KMInicial = 0
        obj.KMFinal = 0
        obj.save(update_fields=["idVeiculo", "KMInicial", "KMFinal"])
        data = html_motorista(request, data, idminuta)
    data = html_recebimento(request, data, idminuta)
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, idminuta)
    return data


def remove_despessa(request, idminutaitens, idminuta):
    despesa = MinutaItens.objects.get(idMinutaItens=idminutaitens)
    despesa.delete()
    data = dict()
    data = html_despesa(request, data, idminuta)
    data = html_recebimento(request, data, idminuta)
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, idminuta)
    return data


def remove_entrega(request, idminutanota, idminuta):
    entrega = MinutaNotas.objects.get(idMinutaNotas=idminutanota)
    entrega.delete()
    data = dict()
    data = html_entrega(request, data, idminuta)
    data = html_recebimento(request, data, idminuta)
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, idminuta)
    return data


def html_cliente_data(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data["html_cliente_data"] = render_to_string(
        "minutas/html_card_minuta_cliente_dia.html", contexto, request=request
    )
    return data


def html_motorista(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data["html_veiculo"] = render_to_string(
        "minutas/html_card_minuta_veiculo.html", contexto, request=request
    )
    return data


def html_ajudantes(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data["html_ajudante"] = render_to_string(
        "minutas/html_card_minuta_ajudantes.html", contexto, request=request
    )
    return data


def html_categoria(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data["html_categoria"] = render_to_string(
        "minutas/html_card_minuta_categoria_solicitada.html",
        contexto,
        request=request,
    )
    data["html_veiculo"] = render_to_string(
        "minutas/html_card_minuta_veiculo.html", contexto, request=request
    )
    return data


def html_veiculo(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data["html_veiculo"] = render_to_string(
        "minutas/html_card_minuta_veiculo.html", contexto, request=request
    )
    return data


def html_filtro_veiculo(request, lista_veiculos):
    data = dict()
    contexto = {"lista_veiculos": lista_veiculos}
    data["html_filtro"] = render_to_string(
        "minutas/listaveiculosminuta.html", contexto, request=request
    )
    c_return = JsonResponse(data)
    return c_return


def html_coleta_entrega_obs(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data["html_coleta_entrega_obs"] = render_to_string(
        "minutas/html_card_minuta_coleta_entrega_obs.html",
        contexto,
        request=request,
    )
    return data


def html_despesa(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data["html_despesa"] = render_to_string(
        "minutas/despesaminuta.html", contexto, request=request
    )
    return data


def html_entrega(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data["html_entrega"] = render_to_string(
        "minutas/entregaminuta.html", contexto, request=request
    )
    return data


def html_recebimento(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data["html_recebimento"] = render_to_string(
        "minutas/card_recebe.html", contexto, request=request
    )
    return data


def html_pagamento(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data["html_pagamento"] = render_to_string(
        "minutas/html_card_pagamentos.html", contexto, request=request
    )
    return data


def html_checklist(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data["html_checklist"] = render_to_string(
        "minutas/card_checklist.html", contexto, request=request
    )
    return data


def retorna_json(data):
    c_return = JsonResponse(data)
    return c_return


def forn_minuta(request, c_form, c_idobj, c_url, c_view):
    data = dict()
    c_instance = None
    mensagem = None
    tipo_mensagem = None
    if request.method == "POST":
        form = c_form(request.POST)
        if form.is_valid():
            if c_view == "adiciona_minuta":
                minuta_salva = form.save()
                id_minuta_salva = minuta_salva.idMinuta
                data["id_minuta_salva"] = id_minuta_salva
            else:
                if c_view == "edita_minuta":
                    cliente = get_cliente(request.POST.get("idCliente"))
                    obj = get_minuta(c_idobj)
                    obj.idCliente = cliente
                    obj.DataMinuta = request.POST.get("DataMinuta")
                    obj.HoraInicial = request.POST.get("HoraInicial")
                    obj.save(
                        update_fields=[
                            "idCliente",
                            "DataMinuta",
                            "HoraInicial",
                        ]
                    )
                    mensagem = "OS ITENS CLIENTE, DATA E HORA INICIAL DA MINUTA FORAM ATUALIZADOS."
                    tipo_mensagem = "SUCESSO"
                    data = html_cliente_data(request, data, c_idobj)
                if c_view == "insere_ajudante":
                    form.save()
                    data = html_ajudantes(request, data, c_idobj)
                if c_view == "insere_motorista":
                    form.save()
                    idpessoal = request.POST.get("idPessoal")
                    veiculo_selecionado(idpessoal, c_idobj)
                    data = html_motorista(request, data, c_idobj)
                elif c_view == "edita_minuta_veiculo_solicitado":
                    obj = get_minuta(c_idobj)
                    if request.POST.get("idCategoriaVeiculo"):
                        categoria = get_categoria(
                            request.POST.get("idCategoriaVeiculo")
                        )
                        obj.idCategoriaVeiculo = categoria
                        mensagem = "O VEICULO SOLICITADO FOI ATUALIZADO."
                    else:
                        obj.idCategoriaVeiculo = None
                        mensagem = "O VEICULO SOLICITADO FOI REMOVIDO."
                    obj.save(update_fields=["idCategoriaVeiculo"])
                    tipo_mensagem = "SUCESSO"
                    data = html_categoria(request, data, c_idobj)
                elif c_view == "edita_minuta_veiculo_escolhido":
                    idveiculo = request.POST.get("idVeiculo")
                    if request.POST.get("idVeiculo"):
                        veiculo = Veiculo.objects.filter(idVeiculo=idveiculo)
                        km_inicial = km_atual(veiculo[0])
                        if len(veiculo) == 1:
                            obj = get_minuta(c_idobj)
                            obj.idVeiculo = veiculo[0]
                            obj.KMInicial = km_inicial["KMFinal__max"]
                            obj.save(update_fields=["idVeiculo", "KMInicial"])
                        mensagem = "O VEICULO ESCOLHIDO FOI ATUALIZADO."
                        tipo_mensagem = "SUCESSO"
                        data = html_veiculo(request, data, c_idobj)
                elif c_view == "edita_minuta_coleta_entrega_obs":
                    obj = get_minuta(c_idobj)
                    obj.Entrega = request.POST.get("Entrega")
                    obj.Coleta = request.POST.get("Coleta")
                    obj.Obs = request.POST.get("Obs")
                    obj.save(update_fields=["Coleta", "Entrega", "Obs"])
                    mensagem = "AS INFORMAÇÕES DE COLETA, ENTREGA E OBSERVAÇÕES FORAM ATUALIZADAS."
                    tipo_mensagem = "SUCESSO"
                    data = html_coleta_entrega_obs(request, data, c_idobj)
                elif c_view == "insere_minuta_despesa":
                    form.save()
                    mensagem = "DESPESA INSERIDA."
                    tipo_mensagem = "SUCESSO"
                    data = html_despesa(request, data, c_idobj)
                elif c_view == "insere_minuta_entrega":
                    form.save()
                    mensagem = "ENTREGA INSERIDA."
                    tipo_mensagem = "SUCESSO"
                    data = html_entrega(request, data, c_idobj)
                data = html_recebimento(request, data, c_idobj)
                data = html_pagamento(request, data, c_idobj)
                data = html_checklist(request, data, c_idobj)
        else:
            pass
    else:
        if c_view == "edita_minuta":
            c_instance = get_minuta(c_idobj)
        if c_view == "edita_minuta_coleta_entrega_obs":
            c_instance = get_minuta(c_idobj)
        if c_view == "edita_minuta_insere_despesa":
            c_instance = get_minuta(c_idobj)
        form = c_form(instance=c_instance)
    if c_idobj:
        ajudantes = ajudantes_disponiveis(c_idobj)
        motoristas = motoristas_disponiveis()
        idpessoal = request.GET.get("idPessoal")
        s_minuta = MinutaSelecionada(c_idobj)
        despesas = (
            MinutaItens.objects.filter(TipoItens="DESPESA")
            .values("Descricao")
            .distinct()
            .order_by("Descricao")
        )
        lista_veiculos = []
        minuta = s_minuta.numero
        contexto = {
            "form": form,
            "c_idobj": c_idobj,
            "c_url": c_url,
            "c_view": c_view,
            "ajudantes": ajudantes,
            "motoristas": motoristas,
            "lista_veiculos": lista_veiculos,
            "idpessoal": idpessoal,
            "s_minuta": s_minuta,
            "despesas": despesas,
            "minuta": minuta,
        }
    else:
        minuta = proxima_minuta()
        contexto = {
            "form": form,
            "c_idobj": c_idobj,
            "c_url": c_url,
            "c_view": c_view,
            "minuta": minuta,
        }
    data["html_form"] = render_to_string(
        "minutas/formminuta.html", contexto, request=request
    )
    data["c_view"] = c_view
    data["html_mensagem"] = mensagem
    data["html_tipo_mensagem"] = tipo_mensagem
    c_return = JsonResponse(data)
    return c_return


def create_contexto_romaneios(id_cli):
    romaneios = Romaneios.objects.filter(
        idCliente=id_cli, idMinuta__isnull=True
    ).order_by("-Romaneio")
    lista = [
        {
            "idromaneio": x.idRomaneio,
            "romaneio": x.Romaneio,
            "motorista": nome_curto(x.idMotorista.Nome),
            "veiculo": x.idVeiculo,
            "data_romaneio": x.DataRomaneio,
            "idminuta": x.idMinuta_id,
        }
        for x in romaneios
    ]
    return lista


def save_notas_romaneio_minuta(id_rom, id_min):
    rom_notas = RomaneioNotas.objects.filter(idRomaneio=id_rom)
    lista = []
    for x in rom_notas:
        nota_cliente = NotasClientes.objects.get(
            idNotasClientes=x.idNotasClientes_id
        )
        nota = dict()
        nota["numero"] = nota_cliente.NumeroNota
        nota["valor"] = nota_cliente.Valor
        nota["peso"] = nota_cliente.Peso
        nota["volume"] = nota_cliente.Volume
        if nota_cliente.LocalColeta == "DESTINATÁRIO":
            nota["nome"] = nota_cliente.Emitente
            nota["endereco"] = nota_cliente.Endereco_emi
            nota["bairro"] = nota_cliente.Bairro_emi
            nota["cidade"] = nota_cliente.Cidade_emi
            nota["estado"] = nota_cliente.Estado_emi
        else:
            nota["nome"] = nota_cliente.Destinatario
            nota["endereco"] = nota_cliente.Endereco
            nota["bairro"] = nota_cliente.Bairro
            nota["cidade"] = nota_cliente.Cidade
            nota["estado"] = nota_cliente.Estado
        nota["notaguia"] = 0
        nota["idminuta"] = id_min
        lista.append(nota)
    nova_lista = sorted(lista, key=lambda d: d["endereco"])
    atual = -1
    for itens in nova_lista:
        proximo = next(
            (
                i
                for i, x in enumerate(nova_lista)
                if x["endereco"] == itens["endereco"]
            ),
            None,
        )
        if atual == proximo:
            itens["notaguia"] = nota
        else:
            nota = itens["numero"]
        atual = proximo
    save_nota_entrega(nova_lista)
    romaneio = Romaneios.objects.get(idRomaneio=id_rom)
    obj = romaneio
    obj.idMinuta_id = id_min
    obj.save(update_fields=["idMinuta_id"])


def save_nota_entrega(nota_lista):
    for nota in nota_lista:
        obj = MinutaNotas()
        obj.Nota = nota["numero"]
        obj.ValorNota = nota["valor"]
        obj.Peso = nota["peso"]
        obj.Volume = nota["volume"]
        obj.Nome = nota["nome"]
        obj.Bairro = nota["bairro"]
        obj.Cidade = nota["cidade"]
        obj.Estado = nota["estado"]
        obj.NotaGuia = nota["notaguia"]
        obj.idMinuta_id = nota["idminuta"]
        obj.ExtraValorAjudante = 0
        obj.save()


def create_data_adiciona_romaneio_minuta(request, id_min):
    data = dict()
    data = html_entrega(request, data, id_min)
    return data


def remove_numero_romaneio_minuta(numero_romaneio, idminuta):
    romaneio = Romaneios.objects.get(
        idMinuta=idminuta, Romaneio=numero_romaneio
    )
    obj = romaneio
    obj.idMinuta_id = None
    obj.save(update_fields=["idMinuta_id"])


def create_contexto_minuta_selecionada(idminuta):
    s_minuta = MinutaSelecionada(idminuta)
    contexto = {
        "s_minuta": s_minuta,
    }
    return contexto


def create_data_entrega_romaneio_minuta(request, contexto):
    data = dict()
    data = html_entrega_nova(request, data, contexto)
    data = html_romaneio(request, data, contexto)
    return JsonResponse(data)


# TODO trocar futuramente html_entrega por está
def html_entrega_nova(request, data, contexto):
    data["html_entrega"] = render_to_string(
        "minutas/entregaminuta.html", contexto, request=request
    )
    return data


def html_romaneio(request, data, contexto):
    data["html_romaneio"] = render_to_string(
        "minutas/html_entregas_romaneio.html", contexto, request=request
    )
    return data


def gera_itens_pagamento_motorista(request):
    if request.POST.get("check-porcentagem-paga"):
        insere_porcentagem_paga(request)
    if request.POST.get("check-hora-paga"):
        insere_hora_paga(request)
    if request.POST.get("check-excede-paga"):
        insere_excedente_paga(request)
    if request.POST.get("check-kilometragem-paga"):
        insere_kilometragem_paga(request)
    if request.POST.get("check-entrega-paga"):
        insere_entrega_paga(request)
    if request.POST.get("check-entrega-kg-paga"):
        insere_entrega_kg_paga(request)
    if request.POST.get("check-entrega-volume-paga"):
        insere_entrega_volume_paga(request)
    if request.POST.get("check-saida-paga"):
        insere_saida_paga(request)
    if request.POST.get("check-capacidade-paga"):
        insere_capacidade_paga(request)
    if request.POST.get("check-perimetro-paga"):
        insere_perimetro_paga(request)
    if request.POST.get("check-pernoite-paga"):
        insere_pernoite_paga(request)
    lista_despesas = []
    for i in request.POST:
        if i[0:18] == "check-despesa-paga":
            lista_despesas.append(i[18:])
    for i in lista_despesas:
        item_tabela = "tabela-despesa-paga" + i
        item_descricao = "descricao-despesa-paga" + i
        insere_despesa_paga(
            request.POST.get(item_tabela),
            request.POST.get(item_descricao),
            request,
        )


def gera_itens_pagamento_ajudantes(request):
    if request.POST.get("check-ajudante-paga"):
        insere_ajudante_paga(request)


def insere_porcentagem_paga(request):
    idminuta = request.POST.get("idminuta")
    hora_zero = timedelta(days=0, hours=0, minutes=0)
    obs = ""
    base = float(
        request.POST.get("minuta-porcentagem-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    porcento = float(
        request.POST.get("tabela-porcentagem-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    valor = base * porcento / 100
    insere_minuta_item(
        "PORCENTAGEM DA NOTA",
        "PAGA",
        "P",
        valor,
        0,
        porcento,
        0.00,
        base,
        hora_zero,
        idminuta,
        obs,
    )


def insere_hora_paga(request):
    idminuta = request.POST.get("idminuta")
    obs = ""
    base = float(
        request.POST.get("tabela-hora-paga").replace(".", "").replace(",", ".")
    )
    tempo = datetime.strptime(
        request.POST.get("minuta-hora-paga"), "%H:%M"
    ).time()
    valor = calcula_valor_hora(100, tempo, base)
    tempo = timedelta(days=0, hours=tempo.hour, minutes=tempo.minute)
    insere_minuta_item(
        "HORAS",
        "PAGA",
        "P",
        valor,
        0,
        0.00,
        0.00,
        base,
        tempo,
        idminuta,
        obs,
    )


def insere_excedente_paga(request):
    idminuta = request.POST.get("idminuta")
    obs = ""
    porcento = float(request.POST.get("tabela-excedente-paga"))
    base = float(request.POST.get("tabela-hora-paga"))
    tempo = datetime.strptime(
        request.POST.get("minuta-excedente-paga"), "%H:%M"
    )
    valor = calcula_valor_hora(porcento, tempo, base)
    tempo = timedelta(days=0, hours=tempo.hour, minutes=tempo.minute)
    insere_minuta_item(
        "HORAS EXCEDENTE",
        "PAGA",
        "P",
        valor,
        0,
        porcento,
        0.00,
        base,
        tempo,
        idminuta,
        obs,
    )


def insere_kilometragem_paga(request):
    idminuta = request.POST.get("idminuta")
    hora_zero = timedelta(days=0, hours=0, minutes=0)
    obs = ""
    base = float(
        request.POST.get("tabela-kilometragem-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    unidade = float(request.POST.get("minuta-kilometragem-paga"))
    valor = base * unidade
    insere_minuta_item(
        "KILOMETRAGEM",
        "PAGA",
        "P",
        valor,
        unidade,
        0.00,
        0.00,
        base,
        hora_zero,
        idminuta,
        obs,
    )


def insere_entrega_paga(request):
    idminuta = request.POST.get("idminuta")
    hora_zero = timedelta(days=0, hours=0, minutes=0)
    obs = ""
    base = float(
        request.POST.get("tabela-entrega-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    unidade = float(request.POST.get("minuta-entrega-paga"))
    valor = base * unidade
    insere_minuta_item(
        "ENTREGAS",
        "PAGA",
        "P",
        valor,
        unidade,
        0.00,
        0.00,
        base,
        hora_zero,
        idminuta,
        obs,
    )


def insere_entrega_kg_paga(request):
    idminuta = request.POST.get("idminuta")
    hora_zero = timedelta(days=0, hours=0, minutes=0)
    obs = ""
    base = float(
        request.POST.get("tabela-entrega-kg-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    peso = float(
        request.POST.get("minuta-entrega-kg-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    valor = base * peso
    insere_minuta_item(
        "ENTREGAS KG",
        "PAGA",
        "P",
        valor,
        0,
        0.00,
        peso,
        base,
        hora_zero,
        idminuta,
        obs,
    )


def insere_entrega_volume_paga(request):
    idminuta = request.POST.get("idminuta")
    hora_zero = timedelta(days=0, hours=0, minutes=0)
    obs = ""
    base = float(
        request.POST.get("tabela-entrega-volume-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    unidade = float(request.POST.get("minuta-entrega-volume-paga"))
    valor = base * unidade
    insere_minuta_item(
        "ENTREGAS VOLUME",
        "PAGA",
        "P",
        valor,
        unidade,
        0.00,
        0.00,
        base,
        hora_zero,
        idminuta,
        obs,
    )


def insere_saida_paga(request):
    idminuta = request.POST.get("idminuta")
    hora_zero = timedelta(days=0, hours=0, minutes=0)
    obs = ""
    base = float(
        request.POST.get("tabela-saida-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    insere_minuta_item(
        "SAIDA",
        "PAGA",
        "P",
        base,
        0,
        0.00,
        0.00,
        base,
        hora_zero,
        idminuta,
        obs,
    )


def insere_capacidade_paga(request):
    idminuta = request.POST.get("idminuta")
    hora_zero = timedelta(days=0, hours=0, minutes=0)
    obs = ""
    base = float(
        request.POST.get("tabela-capacidade-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    insere_minuta_item(
        "CAPACIDADE PESO",
        "PAGA",
        "P",
        base,
        0,
        0.00,
        0.00,
        base,
        hora_zero,
        idminuta,
        obs,
    )


def insere_perimetro_paga(request):
    idminuta = request.POST.get("idminuta")
    hora_zero = timedelta(days=0, hours=0, minutes=0)
    obs = ""
    base = float(
        request.POST.get("minuta-perimetro-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    porcento = float(
        request.POST.get("tabela-perimetro-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    valor = base * porcento / 100
    insere_minuta_item(
        "PERIMETRO",
        "PAGA",
        "P",
        valor,
        0,
        porcento,
        0.00,
        base,
        hora_zero,
        idminuta,
        obs,
    )


def insere_pernoite_paga(request):
    idminuta = request.POST.get("idminuta")
    hora_zero = timedelta(days=0, hours=0, minutes=0)
    obs = ""
    base = float(
        request.POST.get("minuta-pernoite-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    porcento = float(
        request.POST.get("tabela-pernoite-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    valor = base * porcento / 100
    insere_minuta_item(
        "PERNOITE",
        "PAGA",
        "P",
        valor,
        0,
        porcento,
        0.00,
        base,
        hora_zero,
        idminuta,
        obs,
    )


def insere_ajudante_paga(request):
    idminuta = request.POST.get("idminuta")
    hora_zero = timedelta(days=0, hours=0, minutes=0)
    obs = ""
    base = float(
        request.POST.get("tabela-ajudante-paga")
        .replace(".", "")
        .replace(",", ".")
    )
    unidade = float(request.POST.get("minuta-ajudante-paga"))
    valor = base * unidade
    insere_minuta_item(
        "AJUDANTE",
        "PAGA",
        "P",
        valor,
        unidade,
        0.00,
        0.00,
        base,
        hora_zero,
        idminuta,
        obs,
    )


def insere_despesa_paga(item_tabela, item_descricao, request):
    idminuta = request.POST.get("idminuta")
    hora_zero = timedelta(days=0, hours=0, minutes=0)
    obs = ""
    base = float(item_tabela.replace(".", "").replace(",", "."))
    insere_minuta_item(
        item_descricao,
        "PAGA",
        "P",
        base,
        0,
        0.00,
        0.00,
        base,
        hora_zero,
        idminuta,
        obs,
    )


def insere_minuta_item(
    descricao,
    tipoitens,
    recebepaga,
    valor,
    quantidade,
    porcento,
    peso,
    valorbase,
    tempo,
    idminuta,
    obs,
):
    obj = MinutaItens()
    obj.Descricao = descricao
    obj.TipoItens = tipoitens
    obj.RecebePaga = recebepaga
    obj.Valor = valor
    obj.Quantidade = quantidade
    obj.Porcento = porcento
    obj.Peso = peso
    obj.ValorBase = valorbase
    obj.Tempo = tempo
    obj.idMinuta_id = idminuta
    obj.Obs = obs
    obj.save()


def estorna_paga(idminuta):
    pagamentos = MinutaItens.objects.filter(
        TipoItens="PAGA", idMinuta=idminuta
    )
    for i in pagamentos:
        i.delete()


def exclui_pagamentos_ajudantes(idminuta):
    pagamentos = MinutaItens.objects.filter(
        TipoItens="PAGA",
        Descricao="AJUDANTE",
        idMinuta=idminuta,
    )
    pagamentos.delete()


def exclui_pagamentos_motorista(idminuta):
    pagamentos = MinutaItens.objects.filter(
        TipoItens="PAGA",
        idMinuta=idminuta,
    ).exclude(Descricao="AJUDANTE")
    pagamentos.delete()


def create_data_gera_pagamentos_ajudantes(request, contexto):
    data = dict()
    data = html_card_minuta(request, data, contexto)
    data = html_card_checklist(request, data, contexto)
    data = html_card_pagamentos(request, data, contexto)
    return JsonResponse(data)


def html_card_minuta(request, data, contexto):
    data["html_card_minuta"] = render_to_string(
        "minutas/html_card_minuta.html", contexto, request=request
    )
    return data


# TODO Duas funções fazendo a mesma coisa (html_checllist)
def html_card_checklist(request, data, contexto):
    data["html_card_checklist"] = render_to_string(
        "minutas/card_checklist.html", contexto, request=request
    )
    return data


# TODO Duas funções fazendo a mesma coisa (html_checllist)
def html_card_pagamentos(request, data, contexto):
    data["html_card_pagamentos"] = render_to_string(
        "minutas/html_card_pagamentos.html", contexto, request=request
    )
    return data


def create_data_exclui_pagamentos_ajudantes(request, contexto):
    data = dict()
    data = html_card_minuta(request, data, contexto)
    data = html_card_checklist(request, data, contexto)
    data = html_card_pagamentos(request, data, contexto)
    return JsonResponse(data)


def create_data_minuta_checklist_pagamentos(request, contexto):
    data = dict()
    data = html_card_minuta(request, data, contexto)
    data = html_card_checklist(request, data, contexto)
    data = html_card_pagamentos(request, data, contexto)
    return JsonResponse(data)


def define_novo_status_minuta(idminuta, status_novo):
    minuta = Minuta.objects.get(idMinuta=idminuta)
    obj = Minuta(minuta)
    obj.idMinuta = minuta.idMinuta
    obj.StatusMinuta = status_novo
    return True if obj.save(update_fields=["StatusMinuta"]) else False


def create_contexto_minutas_periodo(inicial, final, idcliente):
    reset_queries()
    start = time.time()
    start_queries = len(connection.queries)
    if idcliente == 0:
        minuta = Minuta.objects.filter(DataMinuta__range=[inicial, final])
    else:
        minuta = Minuta.objects.filter(
            idCliente=idcliente, DataMinuta__range=[inicial, final]
        )
    minutas = []
    for x in minuta:
        minutas.append(MinutaSelecionada(x.idMinuta).__dict__)
    end = time.time()
    end_queries = len(connection.queries)
    print(start_queries)
    print("tempo: %.2fs" % (end - start))
    print(end_queries)
    return {"minutas": minutas}


def get_minutas_cliente(idcliente):
    minutas = Minuta.objects.filter(idCliente=idcliente)
    return minutas
def create_html_card_recebe(data, contexto, request):
    data["html-card-recebe"] = render_to_string(
        "minutas/card_recebe.html", contexto, request=request
    )
    return data


def gera_itens_receitas(request):
    idminuta = request.POST.get("idminuta")
    dados = request.POST
    list_registros = []
    item_functions = {
        "check-taxa-recebe": adiciona_item_taxa,
        "check-seguro-recebe": adiciona_item_seguro,
        "check-porcentagem-recebe": adiciona_item_porcentagem,
        "check-extra-porcentagem-recebe": adiciona_item_porcentagem_extra,
        "check-hora-recebe": adiciona_item_horas,
        "check-excedente-recebe": adiciona_item_excedente,
        "check-kilometragem-recebe": adiciona_item_kilometragem,
        "check-extra-kilometragem-recebe": adiciona_item_kilometragem_extra,
        "check-entrega-recebe": adiciona_item_entrega,
        "check-extra-entrega-recebe": adiciona_item_entrega_extra,
        "check-entrega-kg-recebe": adiciona_item_entrega_kg,
        "check-extra-entrega-kg-recebe": adiciona_item_entrega_kg_extra,
        "check-entrega-volume-recebe": adiciona_item_entrega_volume,
        "check-extra-entrega-volume-recebe": adiciona_item_entrega_volume_extra,
        "check-saida-recebe": adiciona_item_saida,
        "check-extra-saida-recebe": adiciona_item_saida_extra,
        "check-capacidade-recebe": adiciona_item_capacidade,
        "check-extra-capacidade-recebe": adiciona_item_capacidade_extra,
        "check-perimetro-recebe": adiciona_item_perimetro,
        "check-extra-perimetro-recebe": adiciona_item_perimetro_extra,
        "check-pernoite-recebe": adiciona_item_pernoite,
        "check-ajudante-recebe": adiciona_item_ajudante,
    }
    for key, func in item_functions.items():
        if key in dados:
            list_registros = func(request, list_registros)
    MinutaItens.objects.bulk_create(list_registros)
    total = 0.00
    for key, value in dados.items():
        if key.startswith("valor"):
            total += float(value.replace(".", "").replace(",", "."))
    minuta_status_fechada(idminuta, total)


def adiciona_item_taxa(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-taxa-recebe"))
    valor = string_to_decimal(request.POST.get("valor-taxa-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="TAXA DE EXPEDIÇÃO",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=0,
                Peso=0,
                ValorBase=tabela,
                Tempo=string_to_timedelta("00:00"),
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_seguro(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-seguro-recebe"))
    minuta = string_to_decimal(request.POST.get("minuta-seguro-recebe"))
    valor = string_to_decimal(request.POST.get("valor-seguro-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="SEGURO",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=minuta,
                Tempo=string_to_timedelta("00:00"),
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_porcentagem(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-porcentagem-recebe"))
    minuta = string_to_decimal(request.POST.get("minuta-porcentagem-recebe"))
    valor = string_to_decimal(request.POST.get("valor-porcentagem-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="PORCENTAGEM",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=minuta,
                Tempo=string_to_timedelta("00:00"),
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_porcentagem_extra(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(
        request.POST.get("tabela-extra-porcentagem-recebe")
    )
    minuta = string_to_timedelta(
        request.POST.get("minuta-extra-porcentagem-recebe")
    )
    valor = string_to_decimal(
        request.POST.get("valor-extra-porcentagem-recebe")
    )
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="PORCENTAGEM HORA EXTRA",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=0,
                Tempo=minuta,
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_horas(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-hora-recebe"))
    minuta = string_to_timedelta(request.POST.get("minuta-hora-recebe"))
    valor = string_to_decimal(request.POST.get("valor-hora-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="HORAS",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=0,
                Peso=0,
                ValorBase=tabela,
                Tempo=minuta,
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_excedente(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-excedente-recebe"))
    minuta = string_to_timedelta(request.POST.get("minuta-excedente-recebe"))
    valor = string_to_decimal(request.POST.get("valor-excedente-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="HORAS EXCEDENTE",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=0,
                Tempo=minuta,
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_kilometragem(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-kilometragem-recebe"))
    minuta = int(request.POST.get("minuta-kilometragem-recebe"))
    valor = string_to_decimal(request.POST.get("valor-kilometragem-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="KILOMETRAGEM",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=minuta,
                Porcento=0,
                Peso=0,
                ValorBase=tabela,
                Tempo=string_to_timedelta("00:00"),
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_kilometragem_extra(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(
        request.POST.get("tabela-extra-kilometragem-recebe")
    )
    minuta = string_to_timedelta(
        request.POST.get("minuta-extra-kilometragem-recebe")
    )
    valor = string_to_decimal(
        request.POST.get("valor-extra-kilometragem-recebe")
    )
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="KILOMETRAGEM HORA EXTRA",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=0,
                Tempo=minuta,
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_entrega(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-entrega-recebe"))
    minuta = int(request.POST.get("minuta-entrega-recebe"))
    valor = string_to_decimal(request.POST.get("valor-entrega-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="ENTREGAS",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=minuta,
                Porcento=0,
                Peso=0,
                ValorBase=tabela,
                Tempo=string_to_timedelta("00:00"),
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_entrega_extra(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-extra-entrega-recebe"))
    minuta = string_to_timedelta(
        request.POST.get("minuta-extra-entrega-recebe")
    )
    valor = string_to_decimal(request.POST.get("valor-extra-entrega-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="ENTREGAS HORA EXTRA",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=0,
                Tempo=minuta,
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_entrega_kg(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-entrega-kg-recebe"))
    minuta = string_to_decimal(request.POST.get("minuta-entrega-kg-recebe"))
    valor = string_to_decimal(request.POST.get("valor-entrega-kg-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="ENTREGAS KG",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=0,
                Peso=minuta,
                ValorBase=tabela,
                Tempo=string_to_timedelta("00:00"),
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_entrega_kg_extra(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(
        request.POST.get("tabela-extra-entrega-kg-recebe")
    )
    minuta = string_to_timedelta(
        request.POST.get("minuta-extra-entrega-kg-recebe")
    )
    valor = string_to_decimal(
        request.POST.get("valor-extra-entrega-kg-recebe")
    )
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="ENTREGAS KG HORA EXTRA",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=0,
                Tempo=minuta,
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_entrega_volume(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(
        request.POST.get("tabela-entrega-volume-recebe")
    )
    minuta = int(request.POST.get("minuta-entrega-volume-recebe"))
    valor = string_to_decimal(request.POST.get("valor-entrega-volume-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="ENTREGAS VOLUME",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=minuta,
                Porcento=0,
                Peso=0,
                ValorBase=tabela,
                Tempo=string_to_timedelta("00:00"),
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_entrega_volume_extra(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(
        request.POST.get("tabela-extra-entrega-volume-recebe")
    )
    minuta = string_to_timedelta(
        request.POST.get("minuta-extra-entrega-volume-recebe")
    )
    valor = string_to_decimal(
        request.POST.get("valor-extra-entrega-volume-recebe")
    )
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="ENTREGAS VOLUME HORA EXTRA",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=0,
                Tempo=minuta,
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_saida(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-saida-recebe"))
    valor = string_to_decimal(request.POST.get("valor-saida-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="SAIDA",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=0,
                Peso=0,
                ValorBase=tabela,
                Tempo=string_to_timedelta("00:00"),
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_saida_extra(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-extra-saida-recebe"))
    minuta = string_to_timedelta(request.POST.get("minuta-extra-saida-recebe"))
    valor = string_to_decimal(request.POST.get("valor-extra-saida-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="SAIDA HORA EXTRA",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=0,
                Tempo=minuta,
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_capacidade(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-capacidade-recebe"))
    valor = string_to_decimal(request.POST.get("valor-capacidade-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="CAPACIDADE PESO",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=0,
                Peso=0,
                ValorBase=tabela,
                Tempo=string_to_timedelta("00:00"),
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_capacidade_extra(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(
        request.POST.get("tabela-extra-capacidade-recebe")
    )
    minuta = string_to_timedelta(
        request.POST.get("minuta-extra-capacidade-recebe")
    )
    valor = string_to_decimal(
        request.POST.get("valor-extra-capacidade-recebe")
    )
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="CAPACIDADE PESO HORA EXTRA",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=0,
                Tempo=minuta,
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_perimetro(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-perimetro-recebe"))
    minuta = string_to_decimal(request.POST.get("minuta-perimetro-recebe"))
    valor = string_to_decimal(request.POST.get("valor-perimetro-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="PERIMETRO",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=minuta,
                Tempo=string_to_timedelta("00:00"),
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_perimetro_extra(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(
        request.POST.get("tabela-extra-perimetro-recebe")
    )
    minuta = string_to_timedelta(
        request.POST.get("minuta-extra-perimetro-recebe")
    )
    valor = string_to_decimal(request.POST.get("valor-extra-perimetro-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="PERIMETRO HORA EXTRA",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=0,
                Tempo=minuta,
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_pernoite(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-pernoite-recebe"))
    minuta = string_to_decimal(request.POST.get("minuta-pernoite-recebe"))
    valor = string_to_decimal(request.POST.get("valor-pernoite-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="PERNOITE",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=0,
                Porcento=tabela,
                Peso=0,
                ValorBase=minuta,
                Tempo=string_to_timedelta("00:00"),
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def adiciona_item_ajudante(request, list_registros):
    idminuta = request.POST.get("idminuta")
    tabela = string_to_decimal(request.POST.get("tabela-ajudante-recebe"))
    minuta = int(request.POST.get("minuta-ajudante-recebe"))
    valor = string_to_decimal(request.POST.get("valor-ajudante-recebe"))
    if valor > 0:
        list_registros.append(
            MinutaItens(
                Descricao="AJUDANTE",
                TipoItens="RECEBE",
                RecebePaga="R",
                Valor=valor,
                Quantidade=minuta,
                Porcento=0,
                Peso=0,
                ValorBase=tabela,
                Tempo=string_to_timedelta("00:00"),
                idMinuta_id=idminuta,
            )
        )
    return list_registros


def minuta_status(idminuta, status):
    registro = []
    registro.append(Minuta(StatusMinuta=status, Valor=0.00, idMinuta=idminuta))
    Minuta.objects.bulk_update(registro, ["StatusMinuta", "Valor"])


def minuta_status_fechada(idminuta, total):
    registro = []
    registro.append(
        Minuta(StatusMinuta="FECHADA", Valor=total, idMinuta=idminuta)
    )
    Minuta.objects.bulk_update(registro, ["StatusMinuta", "Valor"])


def estorna_minutaitens_recebe(idminuta):
    itens = MinutaItens.objects.filter(
        idMinuta_id=idminuta, TipoItens="RECEBE"
    )
    itens.delete()
    minuta_status(idminuta, "ABERTA")


def itens_card_checklist(minuta):
    hora_inicial = minuta.get("hora_inicial")
    hora_final = minuta.get("hora_final")
    entregas = minuta.get("entregas")
    veiculo_solicitado = minuta.get("veiculo_solicitado")
    motorista = minuta.get("motorista")
    print(motorista)
    tipo_pgto = None
    if motorista:
        tipo_pgto = motorista[0]["obj"].TipoPgto
    veiculo = minuta.get("veiculo")
    km_inicial = minuta.get("km_inicial")
    km_final = minuta.get("km_final")
    ajudante_avulso = minuta.get("ajudante_avulso")
    status_minuta = minuta.get("status_minuta")
    itens = [
        {
            "condicao": bool(hora_inicial),
            "descricao": "HORA FINAL",
            "check": bool(hora_final > hora_inicial) if hora_final else False,
        },
        {
            "condicao": bool(entregas),
            "descricao": "VEÍCULO SOLICITADO",
            "check": bool(veiculo_solicitado),
        },
        {
            "condicao": bool(veiculo_solicitado),
            "descricao": "MOTORISTA",
            "check": bool(motorista),
        },
        {
            "condicao": bool(motorista),
            "descricao": "VEÍCULO",
            "check": bool(veiculo),
        },
        {
            "condicao": bool(veiculo),
            "descricao": "KM INICIAL",
            "check": bool(km_inicial),
        },
        {
            "condicao": bool(veiculo),
            "descricao": "KM FINAL",
            "check": bool(km_final > km_inicial) if km_final else False,
        },
        {
            "condicao": bool(ajudante_avulso),
            "descricao": "PAGAMENTO AJUDANTE",
            "check": bool(status_minuta != "ABERTA"),
        },
        {
            "condicao": bool(motorista and tipo_pgto != "MENSALISTA"),
            "descricao": "PAGAMENTO MOTORISTA",
            "check": bool(minuta["status_minuta"] != "ABERTA"),
        },
        {
            "condicao": True,
            "descricao": "CONCLUIR MINUTA",
            "check": bool(minuta["status_minuta"] != "ABERTA"),
        },
    ]
    return itens


def edita_hora_final(request):
    """
    Edita a hora final de uma minuta, garantindo que a hora final seja válida
    e maior que a hora inicial.

    Args:
        request (HttpRequest): Objeto de requisição HTTP contendo o id_minuta
        e a hora_final.

    Returns:
        dict: Dicionário contendo uma mensagem indicando o resultado da
        operação.
    """
    id_minuta = request.GET.get("id_minuta")
    minuta = MinutaSelecionada(id_minuta)
    data = minuta.data
    inicial = minuta.hora_inicial
    final = str_hora(request.GET.get("hora_final"))

    if final == minuta.hora_final:
        return {"mensagem": "VOCÊ ENTROU COM A MESMA HORA"}

    periodo = calcular_diferenca(data, inicial, final)
    if not apos_meia_noite(periodo):
        final = str_hora("00:00")
        mensagem = f"HORA REINICIDA ENTRE COM UMA DATA MAIOR QUE {inicial}HS."
    else:
        mensagem = "A HORA FINAL FOI ATUALIZADA."

    Minuta.objects.filter(idMinuta=id_minuta).update(HoraFinal=final)
    return {"mensagem": mensagem}


def contexto_minuta_alterada(idminuta):
    """
    Gera o contexto atualizado de uma minuta selecionada.

    Args:
        id_minuta (int): ID da minuta a ser atualizada.

    Returns:
        dict: Dicionário contendo o contexto atualizado da minuta.
    """
    minuta = vars(MinutaSelecionada(idminuta))
    contexto = {
        "s_minuta": minuta,
        "itens_minuta": criar_itens_card_minuta(minuta),
        "checklist": itens_card_checklist(minuta),
    }
    return contexto


def data_minuta_alterada(request, contexto):
    """
    Atualiza os dados da minuta com o contexto fornecido e retorna um
    JsonResponse.

    Args:
        request (HttpRequest): Objeto de requisição HTTP.
        contexto (dict): Contexto atualizado da minuta.

    Returns:
        JsonResponse: Objeto JsonResponse contendo os dados atualizados.
    """
    data = {"mensagem": contexto["mensagem"]}
    html_functions = [html_card_minuta, html_checklist]
    for html_func in html_functions:
        data = html_func(request, data, contexto)
    return JsonResponse(data)


def html_card_minuta(request, data, contexto):
    """
    Renderiza o template do card da minuta e o adiciona aos dados fornecidos.

    Args:
        request (HttpRequest): Objeto de requisição HTTP.
        data (dict): Dicionário contendo os dados atuais.
        contexto (dict): Contexto atualizado da minuta.

    Returns:
        dict: Dicionário contendo os dados atualizados com o HTML do card da
        minuta.
    """
    data["html-card-minuta"] = render_to_string(
        "minutas/card_minuta.html", contexto, request=request
    )
    return data


def html_checklist(request, data, contexto):
    """
    Renderiza o template do checklist da minuta e o adiciona aos dados
    fornecidos.

    Args:
        request (HttpRequest): Objeto de requisição HTTP.
        data (dict): Dicionário contendo os dados atuais.
        contexto (dict): Contexto atualizado da minuta.

    Returns:
        dict: Dicionário contendo os dados atualizados com o HTML do checklist.
    """
    data["html_checklist"] = render_to_string(
        "minutas/card_checklist.html", contexto, request=request
    )
    return data


def categorias_veiculo():
    """
    Retorna uma lista de categorias de veículos ordenadas por categoria.

    Returns:
        QuerySet: QuerySet contendo as categorias de veículos.
    """
    return CategoriaVeiculo.objects.values(
        "idCategoria", "Categoria"
    ).order_by("Categoria")


def modal_veiculo_solicitado(id_minuta, request):
    """
    Renderiza o modal para solicitar um veículo para a minuta especificada.

    Args:
        id_minuta (int): ID da minuta.
        request (HttpRequest): Objeto de requisição HTTP.

    Returns:
        JsonResponse: Objeto JsonResponse contendo o HTML do modal.
    """
    categorias = categorias_veiculo()
    modal_html = render_to_string(
        "minutas/modal_veiculo_solicitado.html",
        {"id_minuta": id_minuta, "categorias": categorias},
        request=request,
    )
    return JsonResponse({"modal_html": modal_html})


def update_veiculo_solicitado(request):
    """
    Atualiza a categoria do veículo solicitado para a minuta especificada.

    Args:
        request (HttpRequest): Objeto de requisição HTTP contendo o id_minuta
        e id_categoria.

    Returns:
        dict: Dicionário contendo uma mensagem indicando o resultado da
        operação.
    """
    id_minuta = request.POST.get("id_minuta")
    id_categoria_veiculo = request.POST.get("id_categoria")
    try:
        id_minuta = int(id_minuta)
    except (ValueError, TypeError):
        return {"mensagem": "ID DA MINUTA INVÁLIDO"}

    id_categoria_veiculo = (
        int(id_categoria_veiculo) if id_categoria_veiculo else None
    )

    if not isinstance(id_categoria_veiculo, (int, type(None))):
        return {"mensagem": "ID DA CATEGORIA DO VEÍCULO INVÁLIDO"}

    Minuta.objects.filter(idMinuta=id_minuta).update(
        idCategoriaVeiculo_id=id_categoria_veiculo
    )
    return {"mensagem": "VEÍCULO SOLICITADO FOI ATUALIZADO"}


def motoristas_disponiveis():
    """
    Retorna uma lista de motoristas disponíveis.

    Returns:
        QuerySet: QuerySet contendo os motoristas disponíveis.
    """
    return Pessoal.objects.filter(StatusPessoal=True).exclude(
        Categoria="AJUDANTE"
    )


def modal_motorista_minuta(id_minuta, request):
    """
    Renderiza o modal para selecionar um motorista para a minuta especificada.

    Args:
        id_minuta (int): ID da minuta.
        request (HttpRequest): Objeto de requisição HTTP.

    Returns:
        JsonResponse: Objeto JsonResponse contendo o HTML do modal.
    """
    motoristas = motoristas_disponiveis()
    modal_html = render_to_string(
        "minutas/modal_motorista_minuta.html",
        {"id_minuta": id_minuta, "motoristas": motoristas},
        request=request,
    )
    return JsonResponse({"modal_html": modal_html})


def save_colaborador_minuta(cargo, id_minuta, id_colaborador):
    """
    Salva um colaborador (motorista ou ajudante) na minuta especificada.

    Args:
        cargo (str): Cargo do colaborador (MOTORISTA ou AJUDANTE).
        id_minuta (int): ID da minuta.
        id_colaborador (int): ID do colaborador.

    Returns:
        None
    """
    MinutaColaboradores.objects.create(
        Cargo=cargo,
        idMinuta_id=id_minuta,
        idPessoal_id=id_colaborador,
    )


def get_kilometragem_atual(id_veiculo):
    """
    Obtém a quilometragem atual do veículo especificado.

    Args:
        id_veiculo (int): ID do veículo.

    Returns:
        int: Quilometragem atual do veículo.
    """
    km_final = Minuta.objects.filter(idVeiculo=id_veiculo).aggregate(
        Max("KMFinal")
    )
    return km_final.get("KMFinal__max", 0) or 0


def save_veiculo_minuta(id_minuta, veiculo):
    """
    Salva um veículo na minuta especificada e atualiza a quilometragem
    inicial.

    Args:
        id_minuta (int): ID da minuta.
        veiculo (Veiculo): Objeto do veículo.

    Returns:
        None
    """
    km_inicial = get_kilometragem_atual(veiculo.idVeiculo)
    Minuta.objects.filter(idMinuta=id_minuta).update(
        idVeiculo_id=veiculo.idVeiculo,
        KMInicial=km_inicial,
    )


def update_motorista_minuta(request):
    """
    Atualiza o motorista da minuta especificada e salva o veículo associado,
    se existir.

    Args:
        request (HttpRequest): Objeto de requisição HTTP contendo o id_minuta
        e id_motorista.

    Returns:
        dict: Dicionário contendo uma mensagem indicando o resultado da
        operação.
    """
    id_minuta = request.POST.get("id_minuta")
    id_motorista = request.POST.get("id_motorista")

    try:
        id_minuta = int(id_minuta)
        id_motorista = int(id_motorista)
    except (ValueError, TypeError):
        return {"mensagem": "ID INVÁLIDO"}

    save_colaborador_minuta("MOTORISTA", id_minuta, id_motorista)
    veiculo = Veiculo.objects.filter(Motorista=id_motorista).first()

    if veiculo:
        save_veiculo_minuta(id_minuta, veiculo)

    return {"mensagem": "MOTORISTA ADICIONADO COM SUCESSO"}


def modal_veiculo_minuta(id_minuta, request):
    """
    Renderiza o modal para selecionar um veículo para a minuta especificada.

    Args:
        id_minuta (int): ID da minuta.
        request (HttpRequest): Objeto de requisição HTTP.

    Returns:
        JsonResponse: Objeto JsonResponse contendo o HTML do modal.
    """
    modal_html = render_to_string(
        "minutas/modal_veiculo_minuta.html",
        {"id_minuta": id_minuta},
        request=request,
    )
    return JsonResponse({"modal_html": modal_html})


def update_veiculo_minuta(request):
    """
    Atualiza o veículo da minuta especificada.

    Args:
        request (HttpRequest): Objeto de requisição HTTP contendo o id_minuta
        e id_veiculo.

    Returns:
        dict: Dicionário contendo uma mensagem indicando o resultado da
        operação.
    """
    id_minuta = request.POST.get("id_minuta")
    id_veiculo = request.POST.get("id_veiculo")

    try:
        id_minuta = int(id_minuta)
        id_veiculo = int(id_veiculo)
    except (ValueError, TypeError):
        return {"mensagem": "ID INVÁLIDO"}

    veiculo = Veiculo.objects.filter(idVeiculo=id_veiculo).first()

    if veiculo:
        save_veiculo_minuta(id_minuta, veiculo)

    return {"mensagem": "VEÍCULO ADICIONADO COM SUCESSO"}


def filtra_veiculo(idpessoal, opcao):
    """
    Filtra veículos com base na opção fornecida e no ID do pessoal.

    Args:
        idpessoal (int): ID do pessoal (motorista) para filtrar veículos
        próprios.
        opcao (str): Opção de filtro ('PROPRIO', 'TRANSPORTADORA',
        'CADASTRADOS').

    Returns:
        list: Lista de dicionários contendo o ID e a descrição dos veículos
        filtrados.
    """
    filtro_opcoes = {
        "PROPRIO": {"Motorista": idpessoal},
        "TRANSPORTADORA": {"Proprietario": 17},
        "CADASTRADOS": {},
    }
    filtros = filtro_opcoes.get(opcao, {})
    veiculos = Veiculo.objects.filter(**filtros).order_by(
        "Marca", "Modelo", "Placa"
    )
    return [
        {
            "id_veiculo": veiculo.idVeiculo,
            "descricao": f"{veiculo.Marca} {veiculo.Modelo} - {veiculo.Placa}",
        }
        for veiculo in veiculos
    ]
