import decimal
from decimal import Decimal, ROUND_HALF_UP
import time
from django.db import connection, reset_queries


from datetime import date, datetime, timedelta, time

from core.constants import (
    SETUP_CALCULO_MINUTA,
    TIPOS_CALCULO,
    FUNCOES_CALCULO,
)
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
from core.tools import str_hoje


def edita_km_final(request):
    pass


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
        self.peso_capacidade = self.get_peso_capacidade()
        self.tabela = ClienteTabela(minuta.idCliente).tabela
        self.tabela_veiculo = ClienteTabelaVeiculo(minuta.idCliente).tabela
        self.total_kms = self.get_total_kms()
        self.tabela_perimetro = ClienteTabelaPerimetro(minuta.idCliente).tabela
        self.km_acima_tabela = self.get_km_acima_tabela()
        self.destaque_tabela_perimetro = self.get_destaque_tabela_perimetro()
        self.tabela_capacidade = ClienteTabelaCapacidade(
            minuta.idCliente
        ).tabela
        self.peso_acima_tabela = self.get_peso_acima_tabela()
        self.destaque_tabela_capacidade = self.get_destaque_tabela_capacidade()
        self.total_horas = self.get_total_horas()
        self.total_horas_str = self.get_total_horas_str()
        self.CategoriaDespesa = MinutaCategoriaDespesas().Categoria
        self.proxima_saida = self.entrega_saida()
        self.status_minuta = minuta.StatusMinuta
        self.paga_realizada_motorista = self.verifica_pagamento_motorista()
        self.paga_realizada_ajudantes = self.verifica_pagamento_ajudantes()
        self.recebe_realizada = self.verifica_recebimentos()
        self.fatura = minuta.idFatura
        self.valor_minuta = minuta.Valor
        self.hora_inicio_extras = self.tabela[0]["HoraInicialExtras"]
        self.horas_extras = calcula_horas_extras(
            self.data, self.hora_final, self.hora_inicio_extras
        )

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

    def get_peso_capacidade(self):
        return (
            max(self.romaneio_pesos, key=lambda x: x["peso"])["peso"]
            if self.romaneio_pesos
            else self.t_entregas["peso_entregas"]
        )

    def get_peso_acima_tabela(self):
        for peso in self.tabela_capacidade:
            if (
                peso["CapacidadeInicial"]
                <= self.peso_capacidade
                <= peso["CapacidadeFinal"]
            ):
                return self.peso_capacidade - (peso["CapacidadeInicial"] - 1)
        return None

    def get_destaque_tabela_capacidade(self):
        destaque = None
        for tabela in self.tabela_capacidade:
            if tabela["CapacidadeFinal"] < self.peso_capacidade:
                destaque = tabela
        return destaque

    def get_km_acima_tabela(self):
        for km in self.tabela_perimetro:
            if (
                km["PerimetroInicial"]
                <= self.total_kms
                <= km["PerimetroFinal"]
            ):
                return self.total_kms - (km["PerimetroInicial"] - 1)
        return None

    def get_destaque_tabela_perimetro(self):
        destaque = None
        for tabela in self.tabela_perimetro:
            if tabela["PerimetroFinal"] < self.total_kms:
                destaque = tabela
        return destaque

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
                "Peso": itens.Peso.quantize(
                    Decimal("0.001"), rounding=ROUND_HALF_UP
                ),
                "Volume": itens.Volume,
                "Nome": itens.Nome,
                "NotaGuia": itens.NotaGuia,
                "Bairro": itens.Bairro,
                "Cidade": itens.Cidade,
                "Estado": itens.Estado,
                "id_romaneio": itens.id_romaneio,
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
                "HoraInicialExtras": itens.HoraInicialExtras,
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


def veiculo_selecionado(idpessoal, idminuta):
    veiculo = Veiculo.objects.filter(Motorista=idpessoal)
    if len(veiculo) == 1:
        km_inicial = km_atual(veiculo[0])
        obj = get_minuta(idminuta)
        obj.idVeiculo = veiculo[0]
        obj.KMInicial = km_inicial["KMFinal__max"]
        obj.save(update_fields=["idVeiculo", "KMInicial"])


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
    minuta = vars(MinutaSelecionada(idminuta))
    contexto = {"s-minuta": minuta}
    checklist = itens_card_checklist(minuta)
    contexto.update({"checklist": checklist})
    data = html_recebimento(request, data, idminuta)
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, contexto)
    return data


def remove_despessa(request, idminutaitens, idminuta):
    despesa = MinutaItens.objects.get(idMinutaItens=idminutaitens)
    despesa.delete()
    minuta = vars(MinutaSelecionada(idminuta))
    contexto = {"s-minuta": minuta}
    checklist = itens_card_checklist(minuta)
    contexto.update({"checklist": checklist})
    data = dict()
    data = html_despesa(request, data, idminuta)
    data = html_recebimento(request, data, idminuta)
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, contexto)
    return data


def remove_entrega(request, idminutanota, idminuta):
    entrega = MinutaNotas.objects.get(idMinutaNotas=idminutanota)
    entrega.delete()
    minuta = vars(MinutaSelecionada(idminuta))
    contexto = {"s-minuta": minuta}
    checklist = itens_card_checklist(minuta)
    contexto.update({"checklist": checklist})
    data = dict()
    data = html_entrega(request, data, idminuta)
    data = html_recebimento(request, data, idminuta)
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, contexto)
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


def html_filtro_veiculo(request, veiculos):
    data = dict()
    contexto = {"veiculos": veiculos}
    data["html_filtro"] = render_to_string(
        "minutas/modal_veiculo_minuta.html", contexto, request=request
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
        "minutas/card_despesas.html", contexto, request=request
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


def retorna_json(data):
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
            "motorista": nome_curto(x.idMotorista.Nome)
            if x.idMotorista
            else "",
            "veiculo": x.idVeiculo,
            "data_romaneio": x.DataRomaneio,
            "idminuta": x.idMinuta_id,
        }
        for x in romaneios
    ]
    return lista


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


def registro_padrao_minuta_itens():
    return {
        "descricao": "",
        "tipo_itens": "",
        "recebe_paga": "",
        "valor": Decimal(0),
        "quantidade": 0,
        "porcento": Decimal(0),
        "peso": Decimal(0),
        "base": Decimal(0),
        "tempo": string_to_timedelta("00:00"),
        "idMinuta_id": None,
    }


def converter_valores_request(valor, tipo):
    CONVERSAO_FUNCOES = {
        "valor": string_to_decimal,
        "quantidade": int,
        "porcento": string_to_decimal,
        "peso": string_to_decimal,
        "base": string_to_decimal,
        "tempo": string_to_timedelta,
    }
    funcao_conversao = CONVERSAO_FUNCOES.get(tipo)

    if funcao_conversao:
        try:
            return funcao_conversao(valor)
        except (ValueError, TypeError):
            # Retorne um valor padrão ou lance um erro específico
            # conforme necessário
            return None

    return None


def gerar_minuta_itens(request):
    id_minuta = request.POST.get("idminuta")
    total_minuta = request.POST.get("total-minuta")
    registros_para_salvar_db = []

    for tipo, item in SETUP_CALCULO_MINUTA.items():
        checkbox_name = f"chk-{tipo}-recebe"

        if request.POST.get(checkbox_name):
            tabela = request.POST.get(f"tabela-{tipo}-recebe")
            tabela = converter_valores_request(tabela, item["field_tabela"])

            minuta = request.POST.get(f"minuta-{tipo}-recebe")
            minuta = converter_valores_request(minuta, item["field_minuta"])

            total = request.POST.get(f"total-{tipo}-recebe")
            total = converter_valores_request(total, item["field_total"])

            registro = registro_padrao_minuta_itens()

            dict_itens = {
                "descricao": item["descricao"],
                "tipo_itens": "RECEBE",
                "recebe_paga": "R",
                item["field_tabela"]: tabela,
                item["field_minuta"]: minuta,
                item["field_total"]: total,
            }

            registro.update(dict_itens)

            registros_para_salvar_db.append(
                MinutaItens(
                    Descricao=registro["descricao"],
                    TipoItens=registro["tipo_itens"],
                    RecebePaga=registro["recebe_paga"],
                    Valor=registro["valor"],
                    Quantidade=registro["quantidade"],
                    Porcento=registro["porcento"],
                    Peso=registro["peso"],
                    ValorBase=registro["base"],
                    Tempo=registro["tempo"],
                    idMinuta_id=id_minuta,
                )
            )

    MinutaItens.objects.bulk_create(registros_para_salvar_db)
    minuta_status_fechada(id_minuta, total_minuta)

    return {"mensagem": "MINUTA FECHADA"}


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
    return {"mensagem": "MINUTA ESTORNADA"}


def itens_card_checklist(minuta):
    hora_inicial = minuta.get("hora_inicial")
    hora_final = minuta.get("hora_final")
    entregas = minuta.get("entregas")
    veiculo_solicitado = minuta.get("veiculo_solicitado")
    motorista = minuta.get("motorista")
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
        #  {
        #  "condicao": bool(ajudante_avulso),
        #  "descricao": "PAGAMENTO AJUDANTE",
        #  "check": bool(status_minuta != "ABERTA"),
        #  },
        #  {
        #  "condicao": bool(motorista and tipo_pgto != "MENSALISTA"),
        #  "descricao": "PAGAMENTO MOTORISTA",
        #  "check": bool(minuta["status_minuta"] != "ABERTA"),
        #  },
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
    s_minuta = MinutaSelecionada(idminuta)
    minuta = vars(MinutaSelecionada(idminuta))
    contexto = {
        "s_minuta": minuta,
        "itens_minuta": criar_itens_card_minuta(minuta),
        "checklist": itens_card_checklist(minuta),
        "despesas": minuta["despesas"],
        "minuta": minuta,
        "teste": s_minuta,
    }
    romaneios = create_contexto_romaneios(minuta["idcliente"])
    contexto.update({"romaneios": romaneios})
    contexto.update(contexto_dados_pagamento(s_minuta))
    contexto.update(contexto_dados_cobranca(s_minuta))
    contexto.update(contexto_dados_cobrado(s_minuta))
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
    html_functions = [
        html_card_minuta,
        html_checklist,
        html_card_despesas,
        html_card_romaneios,
        html_card_entregas,
        html_card_receitas,
        html_card_perimetro,
        html_card_capacidade,
    ]
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
    data["html-card-checklist"] = render_to_string(
        "minutas/card_checklist.html", contexto, request=request
    )
    return data


def html_card_despesas(request, data, contexto):
    """
    Renderiza o template do card despesas da minuta e o adiciona aos dados
    fornecidos.

    Args:
        request (HttpRequest): Objeto de requisição HTTP.
        data (dict): Dicionário contendo os dados atuais.
        contexto (dict): Contexto atualizado da minuta.

    Returns:
        dict: Dicionário contendo os dados atualizados com o HTML do checklist.
    """
    data["html-card-despesas"] = render_to_string(
        "minutas/card_despesas.html", contexto, request=request
    )
    return data


def html_card_romaneios(request, data, contexto):
    """
    Renderiza o template do card romaneios da minuta e o adiciona aos dados
    fornecidos.

    Args:
        request (HttpRequest): Objeto de requisição HTTP.
        data (dict): Dicionário contendo os dados atuais.
        contexto (dict): Contexto atualizado da minuta.

    Returns:
        dict: Dicionário contendo os dados atualizados com o HTML do checklist.
    """
    data["html-card-romaneios"] = render_to_string(
        "minutas/card_romaneios.html", contexto, request=request
    )
    return data


def html_card_entregas(request, data, contexto):
    """
    Renderiza o template do card entregas da minuta e o adiciona aos dados
    fornecidos.

    Args:
        request (HttpRequest): Objeto de requisição HTTP.
        data (dict): Dicionário contendo os dados atuais.
        contexto (dict): Contexto atualizado da minuta.

    Returns:
        dict: Dicionário contendo os dados atualizados com o HTML do checklist.
    """
    data["html-card-entregas"] = render_to_string(
        "minutas/card_entregas.html", contexto, request=request
    )
    return data


def html_card_receitas(request, data, contexto):
    """
    Renderiza o template do card receitas da minuta e o adiciona aos dados
    fornecidos.

    Args:
        request (HttpRequest): Objeto de requisição HTTP.
        data (dict): Dicionário contendo os dados atuais.
        contexto (dict): Contexto atualizado da minuta.

    Returns:
        dict: Dicionário contendo os dados atualizados com o HTML do checklist.
    """
    data["html-card-receitas"] = render_to_string(
        "minutas/card_receitas.html", contexto, request=request
    )
    return data


def html_card_perimetro(request, data, contexto):
    data["html-card-perimetro"] = render_to_string(
        "minutas/card_perimetro.html", contexto, request=request
    )
    return data


def html_card_capacidade(request, data, contexto):
    data["html-card-capacidade"] = render_to_string(
        "minutas/card_capacidade.html", contexto, request=request
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


def excluir_colaborador(request):
    """
    Exclui um colaborador (motorista ou ajudante) de uma minuta.

    Args:
        request (HttpRequest): Objeto de requisição HTTP contendo
        o id_minuta_colaborador.

    Returns:
        dict: Dicionário contendo uma mensagem indicando o resultado
        da operação.
    """
    MinutaColaboradores.objects.get(
        idMinutaColaboradores=request.GET.get("id_minuta_colaborador")
    ).delete()
    return {"mensagem": "MOTORISTA EXCLUIDO COM SUCESSO"}


def excluir_veiculo_minuta(id_minuta):
    """
    Exclui o veículo associado a uma minuta, zerando a quilometragem
    inicial e final.

    Args:
        id_minuta (int): ID da minuta.

    Returns:
        None
    """
    Minuta.objects.filter(idMinuta=id_minuta).update(
        idVeiculo_id=None,
        KMInicial=0,
        KMFinal=0,
    )


def editar_km_inicial(request):
    """
    Edita a quilometragem inicial de uma minuta e zera a quilometragem final.

    Args:
        request (HttpRequest): Objeto de requisição HTTP contendo o
        id_minuta e km_inicial.

    Returns:
        dict: Dicionário contendo uma mensagem indicando o resultado da
        operação.
    """
    Minuta.objects.filter(idMinuta=request.GET.get("id_minuta")).update(
        KMInicial=int(request.GET.get("km_inicial")), KMFinal=0
    )
    return {"mensagem": "QUILOMETRAGEM INICIAL ATUALIZADA, FINAL ZERADA"}


def editar_km_final(request):
    """
    Edita a quilometragem final de uma minuta, garantindo que seja maior que
    a quilometragem inicial.

    Args:
        request (HttpRequest): Objeto de requisição HTTP contendo o
        id_minuta, km_inicial e km_final.

    Returns:
        dict: Dicionário contendo uma mensagem indicando o resultado da
        operação.
    """

    km_inicial = int(request.GET.get("km_inicial"))
    km_final = int(request.GET.get("km_final"))

    if km_final <= km_inicial:
        km_final = 0

    Minuta.objects.filter(idMinuta=request.GET.get("id_minuta")).update(
        KMInicial=km_inicial, KMFinal=km_final
    )

    mensagem = (
        f"QUILOMETRAGEM TEM QUE SER MAIOR QUE {km_inicial}"
        if km_final == 0
        else "QUILOMETRAGEM FINAL ATUALIZADA"
    )

    return {"mensagem": mensagem}


def modal_ajudante_minuta(id_minuta, request):
    """
    Renderiza o modal para selecionar um ajudante para a minuta especificada.

    Args:
        id_minuta (int): ID da minuta.
        request (HttpRequest): Objeto de requisição HTTP.

    Returns:
        JsonResponse: Objeto JsonResponse contendo o HTML do modal.
    """
    ajudantes = ajudantes_disponiveis(id_minuta)
    modal_html = render_to_string(
        "minutas/modal_ajudante_minuta.html",
        {"id_minuta": id_minuta, "ajudantes": ajudantes},
        request=request,
    )
    return JsonResponse({"modal_html": modal_html})


def update_ajudante_minuta(request):
    """
    Atualiza o ajudante da minuta especificada.

    Args:
        request (HttpRequest): Objeto de requisição HTTP contendo o
        id_minuta e id_ajudante.

    Returns:
        dict: Dicionário contendo uma mensagem indicando o resultado
        da operação.
    """
    id_minuta = request.POST.get("id_minuta")
    id_ajudante = request.POST.get("id_ajudante")

    try:
        id_minuta = int(id_minuta)
        id_ajudante = int(id_ajudante)
    except (ValueError, TypeError):
        return {"mensagem": "ID INVÁLIDO"}

    save_colaborador_minuta("AJUDANTE", id_minuta, id_ajudante)
    return {"mensagem": "AJUDANTE ADICIONADO COM SUCESSO"}


def modal_informacoes_minuta(id_minuta, request):
    """
    Renderiza o modal para exibir informações detalhadas da minuta
    especificada.

    Args:
        id_minuta (int): ID da minuta.
        request (HttpRequest): Objeto de requisição HTTP.

    Returns:
        JsonResponse: Objeto JsonResponse contendo o HTML do modal.
    """
    minuta = Minuta.objects.get(idMinuta=id_minuta)
    modal_html = render_to_string(
        "minutas/modal_informacoes_minuta.html",
        {"minuta": minuta},
        request=request,
    )
    return JsonResponse({"modal_html": modal_html})


def save_informacoes_minuta(id_minuta, coleta, entrega, observacao):
    """
    Salva as informações de coleta, entrega e observação na minuta
    especificada.

    Args:
        id_minuta (int): ID da minuta.
        coleta (str): Informações de coleta.
        entrega (str): Informações de entrega.
        observacao (str): Observações adicionais.

    Returns:
        None
    """
    Minuta.objects.filter(idMinuta=id_minuta).update(
        Coleta=coleta,
        Entrega=entrega,
        Obs=observacao,
    )


def update_informacoes_minuta(request):
    """
    Atualiza as informações de coleta, entrega e observação de uma minuta.

    Args:
        request (HttpRequest): Objeto de requisição HTTP contendo o
        id_minuta, coleta, entrega e observacao.

    Returns:
        dict: Dicionário contendo uma mensagem indicando o resultado da
        operação.
    """
    id_minuta = request.POST.get("id_minuta")

    try:
        id_minuta = int(id_minuta)
    except (ValueError, TypeError):
        return {"mensagem": "ID INVÁLIDO"}

    save_informacoes_minuta(
        id_minuta,
        request.POST.get("coleta"),
        request.POST.get("entrega"),
        request.POST.get("observacao"),
    )
    return {"mensagem": "INFORMAÇÕES ATUALIZADAS"}


def clientes_disponiveis():
    """
    Retorna uma queryset com todos os clientes disponíveis.
    """
    return Cliente.objects.all()


def modal_minuta(id_minuta, request):
    """
    Renderiza e retorna o HTML do modal de minuta.

    Args:
        request (HttpRequest): O objeto HttpRequest contendo os dados da
        requisição.

    Returns:
        JsonResponse: Um JsonResponse contendo o HTML renderizado do modal.
    """
    minuta = Minuta.objects.get(idMinuta=id_minuta) if id_minuta else None

    # Definindo valores padrão para uma minuta nova
    data_minuta = str_hoje()
    hora_minuta = "07:00"

    clientes = clientes_disponiveis()
    modal_html = render_to_string(
        "minutas/modal_minuta.html",
        {
            "clientes": clientes,
            "id_minuta": id_minuta,
            "data_minuta": data_minuta,
            "hora_minuta": hora_minuta,
            "minuta": minuta,
        },
        request=request,
    )
    return JsonResponse({"modal_html": modal_html})


def proxima_minuta():
    """
    Calcula e retorna o próximo número de minuta disponível.

    Returns:
        int: O próximo número de minuta.
    """
    numero_minuta = Minuta.objects.aggregate(Max("Minuta"))
    return (numero_minuta["Minuta__max"] or 0) + 1


def salvar_minuta(request):
    """
    Cria e salva uma nova minuta com base nos dados do request.

    Args:
        request (HttpRequest): O objeto HttpRequest contendo os dados da
        requisição.

    Returns:
        JsonResponse: Um JsonResponse contendo o link para a minuta criada.
    """
    minuta_numero = proxima_minuta()
    minuta = Minuta.objects.create(
        Minuta=minuta_numero,
        DataMinuta=request.POST.get("data"),
        HoraInicial=request.POST.get("hora"),
        idCliente_id=request.POST.get("cliente"),
    )
    id_minuta = minuta.idMinuta
    return JsonResponse({"link": f"/minutas/minuta/{id_minuta}"})


def atualizar_minuta(request):
    """
    Atualiza as informações de uma minuta existente com base nos dados do
    request POST.

    Args:
        request (HttpRequest): Objeto de requisição HTTP com os dados do POST.

    Returns:
        dict: Dicionário contendo uma mensagem de sucesso.
    """
    Minuta.objects.filter(idMinuta=request.POST.get("id_minuta")).update(
        DataMinuta=request.POST.get("data"),
        HoraInicial=request.POST.get("hora"),
        idCliente_id=request.POST.get("cliente"),
    )
    return {"mensagem": "MINUTA ATUALIZADA"}


def renderizar_modal_despesas_minuta(id_minuta, request):
    """
    Gera o conteúdo HTML do modal de despesas para uma minuta específica.

    Filtra as despesas já existentes e renderiza um template HTML com a lista
    de despesas e uma despesa específica, caso fornecido o ID.

    Args:
        id_minuta (int): ID da minuta para a qual o modal é gerado.
        request (HttpRequest): Objeto de requisição HTTP com os dados do GET.

    Returns:
        JsonResponse: Resposta JSON contendo o HTML renderizado do modal.
    """
    lista_despesas = (
        MinutaItens.objects.filter(TipoItens="DESPESA")
        .values_list("Descricao", flat=True)
        .distinct()
        .order_by("Descricao")
    )

    id_minuta_itens = request.GET.get("id_minuta_itens")
    despesa = (
        MinutaItens.objects.filter(idMinutaItens=id_minuta_itens).first()
        if id_minuta_itens
        else None
    )

    modal_html = render_to_string(
        "minutas/modal_despesas_minuta.html",
        {
            "id_minuta": id_minuta,
            "lista_despesas": lista_despesas,
            "despesa": despesa,
        },
        request=request,
    )

    return JsonResponse({"modal_html": modal_html})


def salvar_ou_atualizar_despesa_minuta(request):
    """
    Salva ou atualiza uma despesa em uma minuta.

    Se o campo "id_minuta_itens" estiver presente no POST, atualiza a despesa
    correspondente.
    Caso contrário, cria uma nova despesa na minuta especificada.

    Args:
        request (HttpRequest): Objeto de requisição HTTP com os dados do POST.

    Returns:
        dict: Dicionário contendo uma mensagem de sucesso.
    """
    id_minuta_itens = request.POST.get("id_minuta_itens")
    descricao = (request.POST.get("descricao") or "").upper()
    valor = request.POST.get("valor")
    obs = (request.POST.get("obs") or "").upper()
    if id_minuta_itens:
        MinutaItens.objects.filter(idMinutaItens=id_minuta_itens).update(
            Descricao=descricao,
            Valor=valor,
            Obs=obs,
        )
        return {"mensagem": "DESPESA ATUALIZADA"}

    MinutaItens.objects.create(
        Descricao=descricao,
        TipoItens="DESPESA",
        RecebePaga="R",
        Valor=valor,
        Tempo=timedelta(hours=0, minutes=0),
        idMinuta_id=request.POST.get("id_minuta"),
        Obs=obs,
    )
    return {"mensagem": "DESPESA ADICIONADA"}


def deletar_despesa_minuta(id_minuta_itens):
    """
    Exclui uma despesa específica associada a uma minuta.

    Args:
        id_minuta_itens (int): ID da despesa a ser excluída.

    Returns:
        dict: Dicionário contendo uma mensagem de sucesso.
    """
    MinutaItens.objects.filter(idMinutaItens=id_minuta_itens).delete()
    return {"mensagem": "DESPESA EXCLUÍDA"}


def renderizar_modal_entregas_minuta(id_minuta, request):
    """
    Renderiza o modal de entregas para uma minuta específica.

    Esta função gera o conteúdo HTML do modal de entregas de uma minuta,
    baseado no ID da minuta e, opcionalmente, no ID de uma nota específica
    passada no request GET.

    Args:
        id_minuta (int): O ID da minuta para a qual o modal será gerado.
        request (HttpRequest): O objeto de requisição HTTP contendo os
        dados do GET.

    Returns:
        JsonResponse: Um dicionário JSON contendo o HTML renderizado do
        modal.
    """
    id_minuta_nota = request.GET.get("id_minuta_nota")
    minuta = MinutaSelecionada(id_minuta)

    nota = (
        MinutaNotas.objects.filter(idMinutaNotas=id_minuta_nota).first()
        if id_minuta_nota
        else None
    )

    modal_html = render_to_string(
        "minutas/modal_entregas_minuta.html",
        {"minuta": minuta, "nota": nota},
        request,
    )

    return JsonResponse({"modal_html": modal_html})


def salvar_ou_atualizar_entrega_minuta(request):
    """
    Salva ou atualiza uma nota de entrega associada a uma minuta.

    Esta função verifica se uma nota de entrega já existe, com base no
    ID da nota (`id_minuta_nota`). Se o ID estiver presente, a função
    atualiza o registro existente. Caso contrário, ela cria um novo registro
    de nota de entrega para a minuta.
    Os campos de texto são convertidos para maiúsculas antes de serem salvos.

    Args:
        request (HttpRequest): O objeto de requisição HTTP contendo os dados
        do POST.

    Returns:
        dict: Um dicionário com uma mensagem indicando se a nota de entrega
        foi adicionada ou atualizada.
    """
    id_minuta = request.POST.get("id_minuta")
    nota = (request.POST.get("nota") or "").upper()
    valor_nota = request.POST.get("valor_nota")
    peso = request.POST.get("peso")
    volume = request.POST.get("volume")
    nota_guia = (request.POST.get("nota_guia") or "").upper()
    nome = (request.POST.get("nome") or "").upper()
    bairro = (request.POST.get("bairro") or "").upper()
    cidade = (request.POST.get("cidade") or "").upper()
    estado = (request.POST.get("estado") or "").upper()
    id_minuta_nota = request.POST.get("id_minuta_nota")

    if id_minuta_nota:
        MinutaNotas.objects.filter(idMinutaNotas=id_minuta_nota).update(
            Nota=nota,
            ValorNota=valor_nota,
            Peso=peso,
            Volume=volume,
            NotaGuia=nota_guia,
            Nome=nome,
            Bairro=bairro,
            Cidade=cidade,
            Estado=estado,
            idMinuta_id=id_minuta,
        )
        return {"mensagem": "NOTA DE ENTREGA ATUALIZADA"}

    MinutaNotas.objects.create(
        Nota=nota,
        ValorNota=valor_nota,
        Peso=peso,
        Volume=volume,
        NotaGuia=nota_guia,
        Nome=nome,
        Bairro=bairro,
        Cidade=cidade,
        Estado=estado,
        idMinuta_id=id_minuta,
    )

    return {"mensagem": "NOTA DE ENTREGA ADICIONADA"}


def deletar_nota_de_entrega_da_minuta(id_minuta_notas):
    """
    Deleta uma nota de entrega associada a uma minuta.

    Esta função remove o registro de uma nota de entrega específica da
    tabela `MinutaNotas`, com base no ID fornecido.

    Args:
        id_minuta_notas (int): O ID da nota de entrega a ser removida.

    Returns:
        dict: Um dicionário com uma mensagem indicando que a entrega foi
        removida.
    """
    MinutaNotas.objects.filter(idMinutaNotas=id_minuta_notas).delete()
    return {"mensagem": "ENTREGA REMOVIDA"}


def novo_status_minuta(id_minuta, novo_status):
    """
    Atualiza o status de uma minuta e retorna uma mensagem indicativa
    do novo estado.

    Args:
        id_minuta (int): ID da minuta a ser atualizada.
        novo_status (str): Novo status a ser aplicado à minuta.

    Returns:
        dict: Dicionário contendo uma mensagem que indica se a minuta
        foi concluída ou reaberta.
    """
    Minuta.objects.filter(idMinuta=id_minuta).update(StatusMinuta=novo_status)
    mensagem = (
        "MINUTA CONCLUÍDA" if novo_status == "CONCLUIDA" else "MINUTA REABERTA"
    )
    return {"mensagem": mensagem}


def adicionar_romaneio_na_minuta(id_minuta, id_romaneio):
    """
    Adiciona as notas associadas a um romaneio a uma minuta.

    Esta função recupera todas as notas associadas ao romaneio especificado,
    organiza-as de acordo com o endereço de destino e as insere na minuta.
    Se o romaneio não possuir notas, uma mensagem de erro é retornada.

    Parâmetros:
    - id_romaneio (int): ID do romaneio cujas notas serão adicionadas.
    - id_minuta (int): ID da minuta onde as notas serão adicionadas.

    Retorno:
    - dict: Um dicionário contendo uma mensagem indicando o sucesso ou falha
            da operação.
    """
    romaneio_notas = list(
        RomaneioNotas.objects.filter(idRomaneio=id_romaneio).select_related(
            "idNotasClientes"
        )
    )

    if not romaneio_notas:
        return {
            "mensagem": "ROMANEIO NÃO POSSUI NOTAS, IMPOSSÍVEL ADICIONÁ-LO"
        }

    notas_lista = []
    for romaneio_nota in romaneio_notas:
        nota_cliente = romaneio_nota.idNotasClientes
        nota = {
            "numero": nota_cliente.NumeroNota,
            "valor": nota_cliente.Valor,
            "peso": nota_cliente.Peso,
            "volume": nota_cliente.Volume,
        }
        if nota_cliente.LocalColeta == "DESTINATÁRIO":
            nota.update(
                {
                    "nome": nota_cliente.Emitente,
                    "endereco": nota_cliente.Endereco_emi,
                    "bairro": nota_cliente.Bairro_emi,
                    "cidade": nota_cliente.Cidade_emi,
                    "estado": nota_cliente.Estado_emi,
                    "notaguia": 0,
                }
            )
        else:
            nota.update(
                {
                    "nome": nota_cliente.Destinatario,
                    "endereco": nota_cliente.Endereco,
                    "bairro": nota_cliente.Bairro,
                    "cidade": nota_cliente.Cidade,
                    "estado": nota_cliente.Estado,
                    "notaguia": 0,
                }
            )
        notas_lista.append(nota)

    notas_ordenadas = sorted(notas_lista, key=lambda nota: nota["endereco"])

    atual = -1
    for itens in notas_ordenadas:
        proximo = next(
            (
                i
                for i, x in enumerate(notas_ordenadas)
                if x["endereco"] == itens["endereco"]
            ),
            None,
        )
        if atual == proximo:
            itens["notaguia"] = nota
        else:
            nota = itens["numero"]
        atual = proximo

    #  for i, nota in enumerate(notas_ordenadas):
    #  if i > 0 and nota["endereco"] == notas_ordenadas[i - 1]["endereco"]:
    #  nota["notaguia"] = notas_ordenadas[i - 1]["numero"]
    #  else:
    #  nota["notaguia"] = nota["numero"]

    registros_minuta = [
        MinutaNotas(
            Nota=nota["numero"],
            ValorNota=nota["valor"],
            Peso=nota["peso"],
            Volume=nota["volume"],
            Nome=nota["nome"],
            Bairro=nota["bairro"],
            Cidade=nota["cidade"],
            Estado=nota["estado"],
            NotaGuia=nota["notaguia"],
            ExtraValorAjudante=0,
            idMinuta_id=id_minuta,
            id_romaneio=id_romaneio,
        )
        for nota in notas_ordenadas
    ]

    MinutaNotas.objects.bulk_create(registros_minuta)
    Romaneios.objects.filter(idRomaneio=id_romaneio).update(
        idMinuta_id=id_minuta
    )

    return {"mensagem": "NOTAS DO ROMANEIO ADICIONADAS NA MINUTA"}


def remover_romaneio_da_minuta(id_minuta, id_romaneio):
    """
    Remove todas as notas associadas a um romaneio de uma minuta específica.

    Args:
        id_minuta (int): O ID da minuta de onde as notas serão removidas.
        id_romaneio (int): O ID do romaneio cujas notas serão removidas
        da minuta.

    Returns:
        dict: Mensagem indicando que as notas do romaneio foram removidas
        da minuta.
    """
    MinutaNotas.objects.filter(
        idMinuta_id=id_minuta, id_romaneio=id_romaneio
    ).delete()
    Romaneios.objects.filter(idRomaneio=id_romaneio).update(idMinuta_id=None)
    return {"mensagem": "NOTAS DO ROMANEIO REMOVIDAS DA MINUUTA"}


def filtra_tabela_veiculo(minuta):
    """
    Filtra a tabela de veículos para encontrar o veículo solicitado com
    base no idCategoriaVeiculo.

    Args:
        minuta (Minuta): Objeto da minuta que contém a tabela de veículos
                         e o veículo solicitado.

    Returns:
        dict: Dicionário do veículo solicitado ou None se não encontrado.
    """
    tabela_veiculos = minuta.tabela_veiculo
    solicitado = minuta.veiculo_solicitado

    return next(
        (
            veiculo
            for veiculo in tabela_veiculos
            if veiculo["idCategoriaVeiculo"] == solicitado
        ),
        None,
    )


def filtra_tabela_generico(minuta, tabela, valor_chave):
    """
    Filtra uma tabela específica para encontrar o valor baseado em uma chave
    fornecida.

    Args:
        minuta (Minuta): Objeto da minuta que contém as tabelas e os valores.
        tabela (list): A tabela que será filtrada (pode ser de capacidade ou
                       perímetro).
        valor_chave (str): A chave específica do valor que se deseja obter
                           (exemplo, "CapacidadeCobra" ou "CapacidadePaga").

    Returns:
        Decimal: O valor filtrado com base na chave fornecida.
    """
    if "Capacidade" in valor_chave:
        peso_recebe = (
            max(minuta.romaneio_pesos, key=lambda x: x["peso"])["peso"]
            if minuta.romaneio_pesos
            else minuta.t_entregas["peso_entregas"]
        )

        return next(
            (
                itens[valor_chave]
                for itens in tabela
                if itens["CapacidadeInicial"]
                <= peso_recebe
                <= itens["CapacidadeFinal"]
            ),
            Decimal(0.00),
        )

    if "Perimetro" in valor_chave:
        return next(
            (
                itens[valor_chave]
                for itens in tabela
                if itens["PerimetroInicial"]
                <= minuta.get_total_kms()
                <= itens["PerimetroFinal"]
            ),
            Decimal(0.00),
        )


def filtra_tabela_capacidade_cobra(minuta):
    """
    Filtra a tabela de capacidades para encontrar a capacidade de cobrança
    com base no peso recebido.

    Args:
        minuta: Objeto da minuta que contém a tabela de capacidades e os peso

    Returns:
        Decimal: O valor da capacidade de cobrança.
    """
    return filtra_tabela_generico(
        minuta, minuta.tabela_capacidade, "CapacidadeCobra"
    )


def filtra_tabela_perimetro_cobra(minuta):
    """
    Filtra a tabela de perímetros para encontrar o valor de cobrança baseado
    na quilometragem total.

    Args:
        minuta (Minuta): Objeto da minuta que contém a tabela de perímetros
                         e a quilometragem total.

    Returns:
        Decimal: O valor do perímetro de cobrança.
    """
    return filtra_tabela_generico(
        minuta, minuta.tabela_perimetro, "PerimetroCobra"
    )


def filtra_tabela_capacidade_paga(minuta):
    """
    Filtra a tabela de capacidades para encontrar a capacidade paga
    com base no peso recebido.

    Args:
        minuta: Objeto da minuta que contém a tabela de capacidades e os
                peso

    Returns:
        Decimal: O valor da capacidade paga.
    """
    return filtra_tabela_generico(
        minuta, minuta.tabela_capacidade, "CapacidadePaga"
    )


def filtra_tabela_perimetro_paga(minuta):
    """
    Filtra a tabela de perímetros para encontrar o valor pago baseado
    na quilometragem total.

    Args:
        minuta (Minuta): Objeto da minuta que contém a tabela de perímetros
                         e a quilometragem total.

    Returns:
        Decimal: O valor do perímetro pago.
    """
    return filtra_tabela_generico(
        minuta, minuta.tabela_perimetro, "PerimetroPaga"
    )


def calcula_horas_extras(data, hora_final, hora_limite):
    """
    Calcula a quantidade de horas extras trabalhadas além da hora limite.

    Args:
        data: Data da minuta.
        hora_final: Hora final do trabalho.
        hora_limite: Hora limite para o cálculo das horas extras.

    Returns:
        timedelta: Tempo total de horas extras.
    """
    datetime_final = datetime.combine(data, hora_final)
    datetime_limite = datetime.combine(data, hora_limite)
    diferenca = datetime_final - datetime_limite
    return diferenca if diferenca > timedelta(0) else timedelta(0)


def calcula_cobranca(total_timedelta, valor_por_hora):
    """
    Calcula o valor total a ser cobrado com base nas horas e minutos extras.

    Args:
        total_timedelta (timedelta): Tempo total de horas e minutos extras.
        valor_por_hora (Decimal): Valor cobrado por hora.

    Returns:
        Decimal: O valor total de cobrança.
    """
    total_horas = total_timedelta.total_seconds() / 3600
    horas = int(total_horas)
    minutos = (total_horas - horas) * 60

    cobranca_horas = Decimal(horas) * valor_por_hora

    intervalos = [
        (1, 15, Decimal("0.25")),
        (16, 30, Decimal("0.50")),
        (31, 45, Decimal("0.75")),
        (46, 60, Decimal("1.00")),
    ]

    porcentagem_minutos = next(
        (
            valor
            for inicio, fim, valor in intervalos
            if inicio <= minutos <= fim
        ),
        Decimal(0),
    )

    cobranca_minutos = porcentagem_minutos * valor_por_hora

    return cobranca_horas + cobranca_minutos


def dict_dados_tabela(minuta):
    """
    Cria um dicionário com os dados da tebale com base na minuta fornecida.

    Args:
        minuta (Minuta): Objeto da minuta com os dados da tabela.

    Returns:
        dict: Dicionário contendo os dados da tabela atualizados.
    """
    tabela = minuta.tabela[0]

    return {
        "taxa_expedicao": tabela["TaxaExpedicao"],
        "seguro": tabela["Seguro"],
        "porcentagem_nota": Decimal(0.00),
        "porcentagem_nota_extra": Decimal(100.00),
        "hora": Decimal(0.00),
        "hora_extra": Decimal(100.00),
        "quilometragem": Decimal(0.00),
        "quilometragem_extra": Decimal(100.00),
        "entregas": Decimal(0.00),
        "entregas_extra": Decimal(100.00),
        "saida": Decimal(0.00),
        "saida_extra": Decimal(100.00),
        "capacidade_peso": Decimal(0.00),
        "capacidade_peso_extra": Decimal(100.00),
        "entregas_quilos": Decimal(0.00),
        "entregas_quilos_extra": Decimal(100.00),
        "entregas_volume": Decimal(0.00),
        "entregas_volume_extra": decimal.Decimal(100.00),
        "perimetro": Decimal(0.00),
        "perimetro_extra": Decimal(100.00),
        "pernoite": Decimal(50.00),
        "ajudante": tabela["AjudanteCobra"],
    }


def atualizar_dados_tabela_cobranca(minuta):
    """
    Atualiza os dados da tabela de cobrança com base na minuta fornecida,
    incluindo cálculos adicionais para horas extras.

    Args:
        minuta (Minuta): Objeto da minuta contendo as informações
                         necessárias.

    Returns:
        dict: Dicionário com os dados atualizados da tabela de cobrança.
    """
    dados_a_cobrar = dict_dados_tabela(minuta)

    dados_a_cobrar["capacidade_peso"] = filtra_tabela_capacidade_cobra(minuta)
    dados_a_cobrar["perimetro"] = (
        filtra_tabela_perimetro_cobra(minuta)
        if minuta.perimetro
        else Decimal(0.00)
    )
    if minuta.veiculo:
        veiculo = filtra_tabela_veiculo(minuta)
        if veiculo:
            dados_a_cobrar.update(
                {
                    "porcentagem_nota": veiculo["PorcentagemCobra"],
                    "hora": veiculo["HoraCobra"],
                    "quilometragem": veiculo["KMCobra"],
                    "entregas": veiculo["EntregaCobra"],
                    "saida": veiculo["SaidaCobra"],
                    "entregas_quilos": veiculo["EntregaKGCobra"],
                    "entregas_volume": veiculo["EntregaVolumeCobra"],
                }
            )

    horas_extras = calcula_horas_extras(
        minuta.data, minuta.hora_final, minuta.hora_inicio_extras
    )
    if horas_extras:
        valor_hora_extra = minuta.tabela[0]["AjudanteCobraHoraExtra"]
        cobrar_por_horas_extras = calcula_cobranca(
            horas_extras, valor_hora_extra
        )
        dados_a_cobrar["ajudante"] = (
            minuta.tabela[0]["AjudanteCobra"] + cobrar_por_horas_extras
        )
    return dados_a_cobrar


def atualizar_dados_tabela_pagamento(minuta):
    """
    Atualiza os dados da tabela de pagamento com base na minuta fornecida,
    incluindo cálculos adicionais para horas extras.

    Args:
        minuta (Minuta): Objeto da minuta contendo as informações
                         necessárias.

    Returns:
        dict: Dicionário com os dados atualizados da tabela de pagamento.
    """
    dados_a_pagar = dict_dados_tabela(minuta)

    dados_a_pagar["capacidade_peso"] = filtra_tabela_capacidade_paga(minuta)
    dados_a_pagar["perimetro"] = (
        filtra_tabela_perimetro_paga(minuta)
        if minuta.perimetro
        else Decimal(0.00)
    )
    if minuta.veiculo:
        veiculo = filtra_tabela_veiculo(minuta)
        if veiculo:
            dados_a_pagar.update(
                {
                    "porcentagem_nota": veiculo["PorcentagemPaga"],
                    "hora": veiculo["HoraPaga"],
                    "quilometragem": veiculo["KMPaga"],
                    "entregas": veiculo["EntregaPaga"],
                    "saida": veiculo["SaidaPaga"],
                    "entregas_quilos": veiculo["EntregaKGPaga"],
                    "entregas_volume": veiculo["EntregaVolumePaga"],
                }
            )
    horas_extras = calcula_horas_extras(
        minuta.data, minuta.hora_final, minuta.hora_inicio_extras
    )
    if horas_extras:
        # TODO Criar campo AjudantePagaHoraExtra no db
        valor_hora_extra = minuta.tabela[0]["AjudanteCobraHoraExtra"]
        cobrar_por_horas_extras = calcula_cobranca(
            horas_extras, valor_hora_extra
        )
        dados_a_pagar["ajudante"] = (
            minuta.tabela[0]["AjudantePaga"] + cobrar_por_horas_extras
        )
    return dados_a_pagar


def dict_dados_minuta(minuta):
    """
    Cria um dicionário com os dados da minuta atualizados com base nas
    informações fornecidas.

    Args:
        minuta (Minuta): Objeto da minuta contendo os dados necessários.

    Returns:
        dict: Dicionário contendo os dados da minuta atualizados.
    """
    return {
        "taxa_expedicao": 1,
        "seguro": minuta.t_entregas["valor_entregas"],
        "porcentagem_nota": minuta.t_entregas["valor_entregas"],
        "porcentagem_nota_extra": time(0, 0),
        "hora": time(0, 0),
        "hora_extra": time(0, 0),
        "quilometragem": 0,
        "quilometragem_extra": time(0, 0),
        "entregas": minuta.t_entregas["total_entregas"],
        "entregas_extra": time(0, 0),
        "saida": 1,
        "saida_extra": time(0, 0),
        "capacidade_peso": 1,
        "capacidade_peso_extra": time(0, 0),
        "entregas_quilos": minuta.t_entregas["peso_entregas"],
        "entregas_quilos_extra": time(0, 0),
        "entregas_volume": minuta.t_entregas["volume_entregas"],
        "entregas_volume_extra": time(0, 0),
        "perimetro": Decimal(0.00),
        "perimetro_extra": time(0, 0),
        "pernoite": Decimal(0.00),
        "ajudante": 0,
    }


def atualizar_dados_minuta(minuta):
    dados_minuta = dict_dados_minuta(minuta)

    if minuta.romaneio:
        dados_minuta["taxa_expedicao"] = len(minuta.romaneio)

        if minuta.romaneio_pesos:
            maior_peso = max(minuta.romaneio_pesos, key=lambda x: x["peso"])
            dados_minuta["entregas_quilos"] = maior_peso["peso"]

    veiculo = filtra_tabela_veiculo(minuta)

    if minuta.veiculo and veiculo:
        dados_minuta["hora"] = veiculo["HoraMinimo"]
        dados_minuta["quilometragem"] = (
            minuta.total_kms
            if minuta.total_kms > veiculo["KMMinimo"]
            else veiculo["KMMinimo"]
        )

    if minuta.entregas and veiculo:
        dados_minuta["entregas"] = (
            minuta.quantidade_entregas
            if minuta.quantidade_entregas > veiculo["EntregaMinimo"]
            else veiculo["EntregaMinimo"]
        )

    dados_minuta["ajudante"] = len(minuta.ajudantes) if minuta.ajudantes else 0

    horas_extras = calcula_horas_extras(
        minuta.data, minuta.hora_final, minuta.hora_inicio_extras
    )
    if horas_extras:
        total_segundos = int(horas_extras.total_seconds())
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        tempo_extra = time(horas, minutos)
        dados_minuta["porcentagem_nota_extra"] = tempo_extra
        dados_minuta["hora_extra"] = tempo_extra
        dados_minuta["quilometragem_extra"] = tempo_extra
        dados_minuta["entregas_extra"] = tempo_extra
        dados_minuta["saida_extra"] = tempo_extra
        dados_minuta["capacidade_peso_extra"] = tempo_extra
        dados_minuta["entregas_quilos_extra"] = tempo_extra
        dados_minuta["entregas_volume_extra"] = tempo_extra
        # [INFO] Desabilitada cobrnaça do perimetro extra
        #  dados_minuta["perimetro_extra"] = tempo_extra
    return dados_minuta


def dict_dados_base_calculo(minuta):
    return {
        "taxa_expedicao": None,
        "seguro": None,
        "porcentagem_nota": None,
        "porcentagem_nota_extra": Decimal(0.00),
        "hora": None,
        "hora_extra": Decimal(0.00),
        "quilometragem": None,
        "quilometragem_extra": Decimal(0.00),
        "entregas": None,
        "entregas_extra": Decimal(0.00),
        "saida": None,
        "saida_extra": Decimal(0.00),
        "capacidade_peso": None,
        "capacidade_peso_extra": Decimal(0.00),
        "entregas_quilos": None,
        "entregas_quilos_extra": Decimal(0.00),
        "entregas_volume": None,
        "entregas_volume_extra": Decimal(0.00),
        "perimetro": None,
        "perimetro_extra": Decimal(0.00),
        "pernoite": None,
        "ajudante": None,
    }


def calcular_valor_por_unidade(**kwargs):
    valor_por_unidade = Decimal(kwargs.get("tabela", 0))
    quantidade = int(kwargs.get("minuta", 0))
    total = quantidade * valor_por_unidade
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_percentual_valor(**kwargs):
    percentual = Decimal(kwargs.get("tabela", 0))
    valor_base = Decimal(kwargs.get("minuta", 0))
    total = valor_base * (percentual / 100)
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_valor_por_tempo(**kwargs):
    valor_hora = Decimal(kwargs.get("tabela", 0))
    tempo = kwargs.get("minuta")
    horas = tempo.hour
    minutos = tempo.minute
    valor_horas = valor_hora * horas
    valor_minutos = (valor_hora / 60) * minutos
    total = valor_horas + valor_minutos
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_percentual_horas(**kwargs):
    percentual = Decimal(kwargs.get("tabela", 0))
    tempo = kwargs.get("minuta")
    valor_hora = Decimal(kwargs.get("valor_base", 0)) / 10
    horas = tempo.hour
    minutos = tempo.minute
    valor_hora_percentual = valor_hora * (percentual / 100)
    valor_horas = valor_hora_percentual * horas
    valor_minutos = (valor_hora_percentual / 60) * minutos
    total = valor_horas + valor_minutos
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_valor_por_quilos(**kwargs):
    valor_por_quilo = Decimal(kwargs.get("tabela", 0))
    quilos = Decimal(kwargs.get("minuta", 0))
    total = quilos * valor_por_quilo
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def executar_funcao_calculo(
    nome_funcao, parametros_comuns, parametros_extras=None
):
    """
    Executa a função correspondente ao nome fornecido com parâmetros comuns e
    extras.
    """
    funcao = globals().get(nome_funcao)
    if funcao:
        if parametros_extras:
            return funcao(**parametros_comuns, **parametros_extras)
        return funcao(**parametros_comuns)
    raise ValueError(f"Função {nome_funcao} não encontrada.")


def criar_lista_dados_formulario(tabela_cliente, dados_minuta, valor_base):
    def calcular_total(tipo, forma_calculo):
        funcao_info = FUNCOES_CALCULO[forma_calculo]
        nome_funcao = funcao_info["funcao"]

        parametros_comuns = {
            "tabela": tabela_cliente.get(tipo, Decimal("0.00")),
            "minuta": dados_minuta.get(tipo, Decimal("0.00")),
        }

        parametros_extras = {
            extra: valor_base.get(tipo, Decimal("0.00"))
            for extra in funcao_info.get("parametros_extras", [])
        }

        return executar_funcao_calculo(
            nome_funcao, parametros_comuns, parametros_extras
        )

    lista_dados = []

    for tipo, valores in SETUP_CALCULO_MINUTA.items():
        if tipo in TIPOS_CALCULO:
            total = calcular_total(tipo, valores["forma_calculo"])
            forma_calculo_a, forma_calculo_b = valores["forma_calculo"].split(
                "_", maxsplit=1
            )
            lista_dados.append(
                {
                    "tipo": tipo,
                    "rotulo": tipo.replace("_", " ").upper(),
                    "forma_calculo_a": forma_calculo_a,
                    "forma_calculo_b": forma_calculo_b,
                    "tabela": tabela_cliente.get(tipo, Decimal("0.00")),
                    "minuta": dados_minuta.get(tipo, Decimal("0.00")),
                    "total": total,
                    "ativo": valores["ativo"],
                    "input_type": valores["input_type"],
                    "indice": valores["indice"],
                }
            )
            valor_base[f"{tipo}_extra"] = total

    for tipo, valores in SETUP_CALCULO_MINUTA.items():
        tipo_sem_extra = tipo.replace("_extra", "")
        if "_extra" in tipo and tipo_sem_extra in TIPOS_CALCULO:
            total = calcular_total(tipo, valores["forma_calculo"])
            forma_calculo_a, forma_calculo_b = valores["forma_calculo"].split(
                "_", maxsplit=1
            )
            lista_dados.append(
                {
                    "tipo": tipo,
                    "rotulo": tipo.replace("_", " ").upper(),
                    "forma_calculo_a": forma_calculo_a,
                    "forma_calculo_b": forma_calculo_b,
                    "tabela": tabela_cliente.get(tipo, Decimal("0.00")),
                    "minuta": dados_minuta.get(tipo, Decimal("0.00")),
                    "total": total,
                    "ativo": valores["ativo"],
                    "input_type": valores["input_type"],
                    "indice": valores["indice"],
                }
            )

    for tipo, valores in SETUP_CALCULO_MINUTA.items():
        if tipo in ["taxa_expedicao", "seguro", "ajudante"]:
            total = calcular_total(tipo, valores["forma_calculo"])
            forma_calculo_a, forma_calculo_b = valores["forma_calculo"].split(
                "_", maxsplit=1
            )
            lista_dados.append(
                {
                    "tipo": tipo,
                    "rotulo": tipo.replace("_", " ").upper(),
                    "forma_calculo_a": forma_calculo_a,
                    "forma_calculo_b": forma_calculo_b,
                    "tabela": tabela_cliente.get(tipo, Decimal("0.00")),
                    "minuta": dados_minuta.get(tipo, Decimal("0.00")),
                    "total": total,
                    "ativo": valores["ativo"],
                    "input_type": valores["input_type"],
                    "indice": valores["indice"],
                }
            )

    for tipo, valores in SETUP_CALCULO_MINUTA.items():
        if tipo in ["perimetro", "perimetro_extra", "pernoite"]:
            forma_calculo_a, forma_calculo_b = valores["forma_calculo"].split(
                "_", maxsplit=1
            )
            lista_dados.append(
                {
                    "tipo": tipo,
                    "rotulo": tipo.replace("_", " ").upper(),
                    "forma_calculo_a": forma_calculo_a,
                    "forma_calculo_b": forma_calculo_b,
                    "tabela": tabela_cliente.get(tipo, Decimal("0.00")),
                    "minuta": dados_minuta.get(tipo, Decimal("0.00")),
                    "total": Decimal(0.00),
                    "ativo": valores["ativo"],
                    "input_type": valores["input_type"],
                    "indice": valores["indice"],
                }
            )

    lista_dados = sorted(lista_dados, key=lambda x: x["indice"])
    return lista_dados


def atualizar_perimetro_pernoite(dados):
    def processar_item(itens, total_phkesk=None, total_perimetro=None):
        tipo_funcao_map = {
            "perimetro": {"minuta": total_phkesk, "parametros_extras": None},
            "perimetro_extra": {
                "minuta": itens["minuta"],
                "parametros_extras": {"valor_base": total_perimetro},
            },
            "pernoite": {"minuta": total_phkesk, "parametros_extras": None},
        }

        if itens["tipo"] in tipo_funcao_map:
            forma_calculo = (
                f'{itens["forma_calculo_a"]}_{itens["forma_calculo_b"]}'
            )
            funcao_info = FUNCOES_CALCULO[forma_calculo]
            nome_funcao = funcao_info["funcao"]

            parametros_comuns = {
                "tabela": itens["tabela"],
                "minuta": tipo_funcao_map[itens["tipo"]]["minuta"],
            }
            parametros_extras = tipo_funcao_map[itens["tipo"]][
                "parametros_extras"
            ]

            total = executar_funcao_calculo(
                nome_funcao, parametros_comuns, parametros_extras
            )

        itens["total"] = total

    total_phkesk = sum(
        itens["total"]
        for itens in dados
        if itens["tipo"].replace("_extra", "") in TIPOS_CALCULO
        and itens["ativo"]
    )
    total_perimetro = Decimal(0.00)

    for itens in dados:
        if itens["tipo"] in {"perimetro", "pernoite"}:
            itens["minuta"] = total_phkesk
            processar_item(itens, total_phkesk=total_phkesk)
            total_perimetro = itens["total"]

        elif itens["tipo"] == "perimetro_extra":
            processar_item(itens, total_perimetro=total_perimetro)

    return dados


def obter_lista_calculos_ativo(phkesc):
    calculos_ativos = []
    for i, digito in enumerate(phkesc):
        if digito == "1":
            calculos_ativos.append(TIPOS_CALCULO[i])
    return calculos_ativos


def ativa_dados_cobranca(minuta, dados_cobranca):
    tabela = minuta.tabela[0]
    phkesc = tabela["phkescCobra"]
    calculos_ativos = obter_lista_calculos_ativo(phkesc)
    for itens in dados_cobranca:
        tipo = itens["tipo"]
        tipo_sem_extra = tipo.replace("_extra", "")
        if tipo_sem_extra in calculos_ativos:
            itens["ativo"] = True
        if tipo_sem_extra == "taxa_expedicao":
            itens["ativo"] = True
        if tabela["Seguro"] and tipo_sem_extra == "seguro":
            itens["ativo"] = True
        if minuta.perimetro and tipo_sem_extra == "perimetro":
            itens["ativo"] = True
        if minuta.ajudantes and tipo_sem_extra == "ajudante":
            itens["ativo"] = True
    return dados_cobranca


def ativa_dados_pagamento(minuta, dados_pagamento):
    tabela = minuta.tabela[0]
    phkesc = tabela["phkescPaga"]
    calculos_ativos = obter_lista_calculos_ativo(phkesc)
    for itens in dados_pagamento:
        tipo = itens["tipo"]
        tipo_sem_extra = tipo.replace("_extra", "")
        if tipo_sem_extra in calculos_ativos:
            itens["ativo"] = True
        if minuta.perimetro and tipo_sem_extra == "perimetro":
            itens["ativo"] = True
        if minuta.ajudantes and tipo_sem_extra == "ajudante":
            itens["ativo"] = True
    return dados_pagamento


def adicionar_item_class(minuta, dados, transacao):
    tabela = minuta.tabela[0]
    phkesc = (
        tabela["phkescCobra"]
        if transacao == "recebe"
        else tabela["phkescPaga"]
    )
    calculos_ativos = obter_lista_calculos_ativo(phkesc)
    for itens in dados:
        tipo = itens["tipo"]
        tipo_sem_extra = tipo.replace("_extra", "")
        itens["class_total"] = (
            f"total-{transacao} total-phkesc-{transacao}"
            if tipo_sem_extra in calculos_ativos
            else f"total-{transacao}"
        )
        itens["transacao"] = transacao

    mapa_class_tabela = {
        "R$": "js-decimal",
        "%": "js-decimal",
        "UN": "js-inteiro",
    }

    mapa_class_minuta = {
        "R$": "js-decimal",
        "%": "js-decimal",
        "UN": "js-inteiro",
        "KG": "js-decimal",
    }
    for itens in dados:
        # Atribui a classe para forma_calculo_a se houver correspondência
        if itens["forma_calculo_a"] in mapa_class_tabela:
            itens["class_tabela"] = mapa_class_tabela[itens["forma_calculo_a"]]

        # Atribui a classe para forma_calculo_b se houver correspondência
        if itens["forma_calculo_b"] in mapa_class_minuta:
            itens["class_minuta"] = mapa_class_minuta[itens["forma_calculo_b"]]

    return dados


def contexto_dados_cobranca(minuta):
    dados_tabela = atualizar_dados_tabela_cobranca(minuta)
    dados_minuta = atualizar_dados_minuta(minuta)
    dados_base = dict_dados_base_calculo(minuta)
    dados_cobranca = criar_lista_dados_formulario(
        dados_tabela, dados_minuta, dados_base
    )
    dados_cobranca = ativa_dados_cobranca(minuta, dados_cobranca)
    dados_cobranca = atualizar_perimetro_pernoite(dados_cobranca)
    dados_cobranca = adicionar_item_class(minuta, dados_cobranca, "recebe")
    return {"dados_cobranca": dados_cobranca}


def contexto_dados_pagamento(minuta):
    dados_tabela = atualizar_dados_tabela_pagamento(minuta)
    dados_minuta = atualizar_dados_minuta(minuta)
    dados_base = dict_dados_base_calculo(minuta)
    dados_pagamento = criar_lista_dados_formulario(
        dados_tabela, dados_minuta, dados_base
    )
    dados_pagamento = ativa_dados_pagamento(minuta, dados_pagamento)
    dados_pagamento = atualizar_perimetro_pernoite(dados_pagamento)
    dados_pagamento = adicionar_item_class(minuta, dados_pagamento, "paga")
    return {"dados_pagamento": dados_pagamento}


def contexto_dados_cobrado(minuta):
    itens_cobrado = MinutaItens.objects.filter(
        idMinuta=minuta.idminuta, RecebePaga="R"
    ).order_by("-TipoItens")
    return {"itens_cobrado": itens_cobrado}
