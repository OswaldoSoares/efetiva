from datetime import datetime, timedelta

# from django.db.models import Max
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from clientes.models import TabelaPerimetro, TabelaVeiculo, TabelaCapacidade, Tabela, Cliente
from minutas.forms import CadastraMinutaKMInicial, CadastraMinutaKMFinal
from minutas.models import MinutaColaboradores, Minuta, MinutaItens, MinutaNotas
from pessoas.models import Pessoal
from veiculos.models import CategoriaVeiculo, Veiculo


def nome_curto(nome):
    apelido = nome
    if nome:
        apelido = nome.split()
    if len(apelido) > 2:
        del apelido[2:]
        apelido = ' '.join(apelido)
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
        self.cliente = minuta.idCliente.Fantasia
        self.motorista = MinutaMotorista(idminuta).nome
        self.ajudantes = MinutaAjudantes(idminuta).nome
        self.veiculo_solicitado = minuta.idCategoriaVeiculo
        self.veiculo = minuta.idVeiculo
        self.km_inicial = minuta.KMInicial
        self.km_final = minuta.KMFinal
        self.despesas = MinutaDespesa(idminuta).descricao
        self.entregas = MinutaEntrega(idminuta).nota
        self.tabela = ClienteTabela(minuta.idCliente).tabela
        self.tabela_veiculo = ClienteTabelaVeiculo(minuta.idCliente).tabela
        self.tabela_perimetro = ClienteTabelaPerimetro(minuta.idCliente).tabela
        self.tabela_capacidade = ClienteTabelaCapacidade(minuta.idCliente).tabela
        self.valores_recebe = self.carrega_valores_recebe()
        self.valores_paga = self.carrega_valores_paga()
        self.total_horas = self.get_total_horas()
        self.total_horas_str = self.total_horas_str()
        self.total_kms = self.get_total_kms()
        self.CategoriaDespesa = MinutaCategoriaDespesas().Categoria
        self.proxima_saida = self.entrega_saida()
        self.status_minuta = minuta.StatusMinuta
        self.paga = self.carrega_valores_paga()
        self.paga_motorista = self.valor_total_motorista()
        self.paga_minuta = self.valor_total_minuta()

    def get_total_kms(self):
        calculo_kms = self.km_final - self.km_inicial
        if calculo_kms < 1:
            calculo_kms = 0
        return calculo_kms

    def total_ajudantes(self):
        self.total_ajudantes_avulso()
        total_ajudantes = len(self.ajudantes)
        return total_ajudantes

    def total_ajudantes_avulso(self):
        total_ajudantes_avulso = len(self.ajudantes)
        for itens in self.ajudantes:
            if itens['tipo'] == 'MENSALISTA':
                total_ajudantes_avulso += -1
        return total_ajudantes_avulso

    def extra_ajudante_cobra(self):
        total_horas = self.get_total_horas()
        dezhoras = timedelta(days=0, hours=10, minutes=0)
        fator = 0.00
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
        recebe_extra_ajudante = float(self.tabela[0]['AjudanteCobraHoraExtra']) * fator
        recebe_extra_ajudante += float(self.tabela[0]['AjudanteCobraHoraExtra']) * (int(horas) - 10)
        recebe_extra_ajudante += float(self.tabela[0]['AjudanteCobra'])
        return recebe_extra_ajudante

    def saidas_ajudante(self):
        if self.ajudantes:
            saidas = len(self.entregas)
            return saidas

    def get_total_horas(self):
        periodo = timedelta(hours=0, minutes=0)
        if self.hora_final:
            inicial = datetime.combine(self.data, self.hora_inicial)
            final = datetime.combine(self.data, self.hora_final)
            if inicial < final:
                periodo = final - inicial
        return periodo

    def total_horas_str(self):
        total_horas_str = str(self.total_horas)
        if total_horas_str.__len__() == 7:
            total_horas_str = f'0{total_horas_str}'
        total_horas_str = total_horas_str[0:5]
        return total_horas_str

    def horas_excede(self):
        excede = timedelta(hours=0, minutes=0)
        minimo = timedelta(hours=0, minutes=0)
        periodo = self.get_total_horas()
        filtro_tabela_veiculo = self.filtro_tabela_veiculo()
        if filtro_tabela_veiculo:
            minimo = timedelta(days=0, hours=filtro_tabela_veiculo['HoraMinimo'].hour,
                               minutes=filtro_tabela_veiculo['HoraMinimo'].minute)
        if periodo > minimo:
            excede = periodo - minimo
        excede_str = str(excede)
        excede = datetime.strptime(excede_str, '%H:%M:%S')
        return excede

    def total_notas(self):
        valor_entregas = sum([itens['ValorNota'] for itens in self.entregas])
        volume_entregas = sum([itens['Volume'] for itens in self.entregas])
        peso_entregas = sum([itens['Peso'] for itens in self.entregas])
        total_entregas = len(self.entregas)
        return valor_entregas, volume_entregas, peso_entregas, total_entregas

    @staticmethod
    def saldo_porcentagem_nota(porcento, valor):
        porcentagem = porcento
        total_notas = valor
        saldo = total_notas * porcentagem / 100
        return saldo

    def filtro_tabela_veiculo(self):
        filtro_tabela_veiculo = [itens for itens in self.tabela_veiculo if itens['idCategoriaVeiculo'] ==
                                 self.veiculo_solicitado]
        if filtro_tabela_veiculo:
            return filtro_tabela_veiculo[0]

    def entrega_saida(self):
        lista_notas = [itens['Nota'] for itens in self.entregas]
        lista_saida = list(filter(lambda itens: 'SAIDA' in itens, lista_notas))
        numero_saidas = len(lista_saida)
        proxima_saida = f'{numero_saidas + 1}ª SAIDA'
        return proxima_saida

    def carrega_valores_paga(self):
        v_paga = cria_dict_paga()
        tabela_veiculo = self.filtro_tabela_veiculo()
        capacidade = [itens['CapacidadePaga'] for itens in self.tabela_capacidade if itens['CapacidadeInicial'] <=
                      self.total_kms() <= itens['CapacidadeFinal']]
        perimetro = [itens['PerimetroPaga'] for itens in self.tabela_perimetro if itens['PerimetroInicial'] <=
                     self.get_total_kms() <= itens['PerimetroFinal']]
        phkesc = self.tabela[0]['phkescPaga']
        if tabela_veiculo:
            if self.motorista:
                if self.motorista[0]['obj'].TipoPgto != 'MENSALISTA':
                    v_paga['v_porc'] = tabela_veiculo['PorcentagemPaga']
                    v_paga['m_porc'] = self.total_notas()[0]
                    v_paga['t_porc'] = tabela_veiculo['PorcentagemPaga'] / 100 * self.total_notas()[0]
                    v_paga['c_porc'] = True if int(phkesc[0:1]) else False
                    v_paga['v_hora'] = self.filtro_tabela_veiculo()['HoraPaga']
                    v_paga['m_hora'] = self.filtro_tabela_veiculo()['HoraMinimo']
                    v_paga['t_hora'] = calcula_valor_hora(100, v_paga['m_hora'], v_paga['v_hora'])
                    v_paga['c_hora'] = True if int(phkesc[1:2]) else False
                    v_paga['v_exce'] = 100
                    v_paga['m_exce'] = self.horas_excede().time()
                    v_paga['t_exce'] = calcula_valor_hora(100, v_paga['m_exce'], v_paga['v_hora'])
                    v_paga['c_exce'] = True if int(phkesc[1:2]) else False
                    v_paga['v_kilm'] = self.filtro_tabela_veiculo()['KMPaga']
                    v_paga['m_kilm'] = self.get_total_kms()
                    v_paga['t_kilm'] = self.filtro_tabela_veiculo()['KMPaga'] * self.get_total_kms()
                    v_paga['c_kilm'] = True if int(phkesc[2:3]) else False
                    v_paga['v_entr'] = self.filtro_tabela_veiculo()['EntregaPaga']
                    v_paga['m_entr'] = self.total_notas()[3]
                    v_paga['t_entr'] = self.filtro_tabela_veiculo()['EntregaPaga'] * self.total_notas()[3]
                    v_paga['c_entr'] = True if int(phkesc[3:4]) else False
                    v_paga['v_enkg'] = self.filtro_tabela_veiculo()['EntregaKGPaga']
                    v_paga['m_enkg'] = self.total_notas()[2]
                    v_paga['t_enkg'] = self.filtro_tabela_veiculo()['EntregaKGPaga'] * self.total_notas()[2]
                    v_paga['c_enkg'] = True if int(phkesc[4:5]) else False
                    v_paga['v_evol'] = self.filtro_tabela_veiculo()['EntregaVolumePaga']
                    v_paga['m_evol'] = self.total_notas()[1]
                    v_paga['t_evol'] = self.filtro_tabela_veiculo()['EntregaVolumePaga'] * self.total_notas()[1]
                    v_paga['c_evol'] = True if int(phkesc[5:6]) else False
                    v_paga['v_said'] = self.filtro_tabela_veiculo()['SaidaPaga']
                    v_paga['c_said'] = True if int(phkesc[6:7]) else False
                    if capacidade:
                        v_paga['v_capa'] = capacidade[0]
                    v_paga['c_capa'] = True if int(phkesc[7:8]) else False
                    if perimetro:
                        v_paga['v_peri'] = perimetro[0]
                        v_paga['c_peri'] = True
                    v_paga = self.base_valor_perimetro(v_paga)
                    v_paga['t_peri'] = float(v_paga['v_peri']) / 100 * float(v_paga['m_peri'])
                    v_paga['m_pnoi'] = v_paga['m_peri']
            if self.total_ajudantes_avulso() > 0:
                v_paga['v_ajud'] = float(self.tabela[0]['AjudantePaga'])
                if int(self.entrega_saida()[0:1]) > 2:
                    v_paga['v_ajud'] = float(self.tabela[0]['AjudantePaga']) + 10.00
                v_paga['m_ajud'] = self.total_ajudantes_avulso()
                v_paga['t_ajud'] = v_paga['v_ajud'] * self.total_ajudantes_avulso()
                v_paga['c_ajud'] = True
        return v_paga

    @staticmethod
    def base_valor_perimetro(v_paga):
        total = 0
        total += float(v_paga['t_porc'])
        total += float(v_paga['t_hora'])
        total += float(v_paga['t_exce'])
        total += float(v_paga['t_kilm'])
        total += float(v_paga['t_entr'])
        total += float(v_paga['t_enkg'])
        total += float(v_paga['t_evol'])
        total += float(v_paga['v_said'])
        total += float(v_paga['v_capa'])
        v_paga['m_peri'] = total
        v_paga['m_pmoi'] = total
        return v_paga

    def valor_total_motorista(self):
        v_paga = self.paga
        total = 0
        total += float(v_paga['m_peri'])
        total += float(v_paga['t_peri'])
        total += float(v_paga['t_pnoi'])
        return total

    def valor_total_minuta(self):
        v_paga = self.paga
        total = 0
        total += float(v_paga['m_peri'])
        total += float(v_paga['t_peri'])
        total += float(v_paga['t_pnoi'])
        total += float(v_paga['t_ajud'])
        return total

    def carrega_valores_recebe(self):
        hora_zero_timedelta = timedelta(hours=0, minutes=0)
        hora_zero_time = datetime.strptime('00:00', '%H:%M').time()
        tabela_veiculo = self.filtro_tabela_veiculo()
        valores_recebe = dict({'valor_taxaexpedicao': 0.00, 'valor_seguro': 0.00, 'minuta_seguro': 0.00,
                               'valor_porcentagem': 0.00, 'minuta_porcentagem': 0.00, 'valor_hora': 0.00,
                               'minuta_hora': hora_zero_time, 'valor_horaexcede': 100.00,
                               'minuta_horaexcede': hora_zero_timedelta, 'valor_kilometragem': 0.00,
                               'minuta_kilometragem': 0.00, 'valor_entregas': 0.00, 'minuta_entregas': 0.00,
                               'valor_entregaskg': 0.00, 'minuta_entregaskg': 0.00, 'valor_entregasvolume': 0.00,
                               'minuta_entregasvolume': 0.00, 'valor_saida': 0.00, 'valor_capacidade': 0.00,
                               'valor_perimetro': 0.00, 'valor_ajudante': 0.00, 'minuta_ajudante': 0.00})
        if tabela_veiculo:
            valores_recebe = dict()
            valores_recebe['valor_taxaexpedicao'] = self.tabela[0]['TaxaExpedicao']
            valores_recebe['valor_seguro'] = 0.23
            valores_recebe['minuta_seguro'] = self.total_notas()[0]
            if self.filtro_tabela_veiculo():
                valores_recebe['valor_porcentagem'] = self.filtro_tabela_veiculo()['PorcentagemCobra']
            else:
                valores_recebe['valor_porcentagem'] = 0.00
            valores_recebe['minuta_porcentagem'] = self.total_notas()[0]
            valores_recebe['valor_hora'] = self.filtro_tabela_veiculo()['HoraCobra']
            valores_recebe['minuta_hora'] = self.filtro_tabela_veiculo()['HoraMinimo']
            valores_recebe['valor_horaexcede'] = 100
            valores_recebe['minuta_horaexcede'] = self.horas_excede()
            valores_recebe['valor_kilometragem'] = self.filtro_tabela_veiculo()['KMCobra']
            valores_recebe['minuta_kilometragem'] = self.get_total_kms()
            valores_recebe['valor_entregas'] = self.filtro_tabela_veiculo()['EntregaCobra']
            valores_recebe['minuta_entregas'] = self.total_notas()[3]
            valores_recebe['valor_entregaskg'] = self.filtro_tabela_veiculo()['EntregaKGCobra']
            valores_recebe['minuta_entregaskg'] = self.total_notas()[2]
            valores_recebe['valor_entregasvolume'] = self.filtro_tabela_veiculo()['EntregaVolumeCobra']
            valores_recebe['minuta_entregasvolume'] = self.total_notas()[1]
            valores_recebe['valor_saida'] = self.filtro_tabela_veiculo()['SaidaCobra']
            capacidade = [itens['CapacidadeCobra'] for itens in self.tabela_capacidade if itens['CapacidadeInicial'] <=
                          self.total_kms() <= itens['CapacidadeFinal']]
            if capacidade:
                valores_recebe['valor_capacidade'] = capacidade[0]
            else:
                valores_recebe['valor_capacidade'] = 0.00
            perimetro = [itens['PerimetroCobra'] for itens in self.tabela_perimetro if itens['PerimetroInicial'] <=
                         self.get_total_kms() <= itens['PerimetroFinal']]
            if perimetro:
                valores_recebe['valor_perimetro'] = perimetro[0]
            else:
                valores_recebe['valor_perimetro'] = 0.00
            valores_recebe['valor_ajudante'] = self.extra_ajudante_cobra()
            valores_recebe['minuta_ajudante'] = self.total_ajudantes()
        return valores_recebe


class MinutaMotorista:
    def __init__(self, idminuta):
        self.nome = self.get_motorista(idminuta)

    @staticmethod
    def get_motorista(idminuta):
        motorista = MinutaColaboradores.objects.filter(idMinuta=idminuta, Cargo='MOTORISTA')
        lista = [{'idMinutaColaboradores': itens.idMinutaColaboradores, 'nome': itens.idPessoal.Nome,
                  'obj': itens.idPessoal} for itens in motorista]
        if lista:
            lista[0]['apelido'] = nome_curto(lista[0]['nome'])
        return lista


class MinutaAjudantes:
    def __init__(self, idminuta):
        self.nome = self.get_ajudantes(idminuta)

    @staticmethod
    def get_ajudantes(idminuta):
        ajudantes = MinutaColaboradores.objects.filter(idMinuta=idminuta, Cargo='AJUDANTE').order_by(
            'idPessoal')
        lista = [{'idMinutaColaboradores': itens.idMinutaColaboradores, 'nome': itens.idPessoal.Nome,
                  'tipo': itens.idPessoal.TipoPgto} for itens in ajudantes]
        if lista:
            for index, itens in enumerate(lista):
                lista[index]['apelido'] = nome_curto(lista[index]['nome'])
        return lista


class MinutaDespesa:
    def __init__(self, idminuta):
        self.descricao = self.get_despesas(idminuta)

    @staticmethod
    def get_despesas(idminuta):
        despesas = MinutaItens.objects.filter(idMinuta=idminuta, TipoItens='DESPESA')
        lista = [{'idMinutaItens': itens.idMinutaItens, 'Descricao': itens.Descricao, 'Valor': itens.Valor,
                  'Obs': itens.Obs} for itens in despesas]
        return lista


class MinutaCategoriaDespesas:
    def __init__(self):
        self.Categoria = self.get_despesas_descricao()

    @staticmethod
    def get_despesas_descricao():
        categoria = MinutaItens.objects.filter(TipoItens='DESPESA').values('Descricao').distinct().order_by('Descricao')
        return categoria


class MinutaEntrega:
    def __init__(self, idminuta):
        self.nota = self.get_entregas(idminuta)

    @staticmethod
    def get_entregas(idminuta):
        entregas = MinutaNotas.objects.filter(idMinuta=idminuta)
        lista = [{'idMinutaNotas': itens.idMinutaNotas, 'Nota': itens.Nota, 'ValorNota': itens.ValorNota,
                  'Peso': itens.Peso, 'Volume': itens.Volume, 'Nome': itens.Nome, 'Bairro': itens.Bairro,
                  'Cidade': itens.Cidade, 'Estado': itens.Estado} for itens in entregas]
        return lista


class ClienteTabela:
    def __init__(self, idcliente):
        self.tabela = self.get_tabela(idcliente)

    @staticmethod
    def get_tabela(idcliente):
        tabelas = Tabela.objects.filter(idCliente=idcliente)
        lista = [{'idTabela': itens.idTabela, 'Comissao': itens.Comissao, 'TaxaExpedicao': itens.TaxaExpedicao,
                  'AjudanteCobra': itens.AjudanteCobra, 'AjudanteCobraHoraExtra': itens.AjudanteCobraHoraExtra,
                  'AjudantePaga': itens.AjudantePaga, 'phkescCobra': itens.phkescCobra, 'phkescPaga': itens.phkescPaga,
                  'idFormaPagamento': itens.idFormaPagamento} for itens in tabelas]
        return lista


class ClienteTabelaVeiculo:
    def __init__(self, idcliente):
        self.tabela = self.get_tabela_veiculo(idcliente)

    @staticmethod
    def get_tabela_veiculo(idcliente):
        veiculos = TabelaVeiculo.objects.filter(idCliente=idcliente)
        lista = [{'idTabelaVeiculo': itens.idTabelaVeiculo, 'idCategoriaVeiculo': itens.idCategoriaVeiculo,
                  'PorcentagemCobra': itens.PorcentagemCobra, 'PorcentagemPaga': itens.PorcentagemPaga,
                  'HoraCobra': itens.HoraCobra, 'HoraPaga': itens.HoraPaga, 'HoraMinimo': itens.HoraMinimo,
                  'KMCobra': itens.KMCobra, 'KMPaga': itens.KMPaga, 'KMMinimo': itens.KMMinimo,
                  'EntregaCobra': itens.EntregaCobra, 'EntregaPaga': itens.EntregaPaga,
                  'EntregaKGCobra': itens.EntregaKGCobra, 'EntregaKGPaga': itens.EntregaKGPaga,
                  'EntregaVolumeCobra': itens.EntregaVolumeCobra, 'EntregaVolumePaga': itens.EntregaVolumePaga,
                  'EntregaMinimo': itens.EntregaMinimo, 'SaidaCobra': itens.SaidaCobra, 'SaidaPaga': itens.SaidaPaga}
                 for itens in veiculos]
        return lista


class ClienteTabelaPerimetro:
    def __init__(self, idcliente):
        self.tabela = self.get_tabela_perimetro(idcliente)

    @staticmethod
    def get_tabela_perimetro(idcliente):
        perimetros = TabelaPerimetro.objects.filter(idCliente=idcliente)
        lista = [{'idTabelaPerimetro': itens.idTabelaPerimetro, 'PerimetroInicial': itens.PerimetroInicial,
                  'PerimetroFinal': itens.PerimetroFinal, 'PerimetroCobra': itens.PerimetroCobra,
                  'PerimetroPaga': itens.PerimetroPaga} for itens in perimetros]
        return lista


class ClienteTabelaCapacidade:
    def __init__(self, idcliente):
        self.tabela = self.get_tabela_capacidade(idcliente)

    @staticmethod
    def get_tabela_capacidade(idcliente):
        capacidades = TabelaCapacidade.objects.filter(idCliente=idcliente)
        lista = [{'idTabelaCapacidade': itens.idTabelaCapacidade, 'CapacidadeInicial': itens.CapacidadeInicial,
                  'CapacidadeFinal': itens.CapacidadeFinal, 'CapacidadeCobra': itens.CapacidadeCobra,
                  'CapacidadePaga': itens.CapacidadePaga} for itens in capacidades]
        return lista


class MinutaFinanceiro:
    def __init__(self, descricao, chave_descricao, tipo_valor_tabela, valor_tabela, tipo_valor_minuta, valor_minuta):
        self.descricao = descricao
        self.chave_descricao = chave_descricao
        self.tipo_valor_tabela = tipo_valor_tabela
        self.valor_tabela = valor_tabela
        self.tipo_valor_minuta = tipo_valor_minuta
        self.valor_minuta = valor_minuta
        self.saldo = 0.00
        self.checked = False

    def checked_on(self):
        self.checked = True

    def checked_off(self):
        self.checked = False


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
    hora_zero_time = datetime.strptime('00:00', '%H:%M').time()
    v_paga = dict({'v_porc': 0.00, 'm_porc': 0.00, 't_porc': 0.00, 'v_hora': 0.00, 'm_hora': hora_zero_time,
                   't_hora': 0.00, 'v_exce': 0.00, 'm_exce': hora_zero_time, 't_exce': 0.00,
                   'v_kilm': 0.00, 'm_kilm': 0.00, 't_kilm': 0.00, 'v_entr': 0.00, 'm_entr': 0.00, 't_entr': 0.00,
                   'v_enkg': 0.00, 'm_enkg': 0.00, 't_enkg': 0.00, 'v_evol': 0.00, 'm_evol': 0.00, 't_evol': 0.00,
                   'v_said': 0.00, 'v_capa': 0.00, 'v_peri': 0.00, 'm_peri': 0.00, 't_peri': 0.00,
                   'v_pnoi': 0.00, 'm_pnoi': 0.00, 't_pnoi': 0.00, 'v_ajud': 0.00, 'm_ajud': 0.00, 't_ajud': 0.00,
                   'c_porc': False, 'c_hora': False, 'c_exce': False, 'c_kilm': False, 'c_entr': False,
                   'c_enkg': False, 'c_evol': False, 'c_said': False, 'c_capa': False, 'c_peri': False, 
                   'c_pnoi': False, 'c_ajud': False})
    return v_paga


def calcula_valor_hora(porcentagem, horas, valor):
    novo_valor = valor * porcentagem / 100
    valor_hora = float(round(novo_valor, 2))
    valor_minuto = float(round(novo_valor / 60, 2))
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
    numero_minuta = Minuta.objects.all().aggregate(Max('Minuta'))
    return int(numero_minuta['Minuta__max']) + 1


def km_atual(idveiculo):
    km_final = Minuta.objects.filter(idVeiculo=idveiculo).aggregate(Max('KMFinal'))
    return km_final


def edita_veiculo_solicitado(request, idminuta, idcategoriaveiculo):
    obj = get_minuta(idminuta)
    categoria = get_categoria(idcategoriaveiculo)
    mensagem = None
    tipo_mensagem = None
    if categoria != obj.idCategoriaVeiculo:
        obj.idCategoriaVeiculo = categoria
        if obj.save(update_fields=['idCategoriaVeiculo']):
            mensagem = 'O VEICULO SOLICITADO FOI ATUALIZADA.'
            tipo_mensagem = 'SUCESSO'
    contexto = cria_contexto(idminuta)
    data = dict()
    data['html_mensagem'] = mensagem
    data['html_tipo_mensagem'] = tipo_mensagem
    data['html_veiculo'] = render_to_string('minutas/veiculominuta.html', contexto, request=request)
    c_return = JsonResponse(data)
    return c_return


def cria_contexto(idminuta):
    s_minuta = MinutaSelecionada(idminuta)
    minuta = Minuta.objects.filter(idMinuta=idminuta)
    minutaform = get_object_or_404(minuta, idMinuta=idminuta)
    form_km_inicial = CadastraMinutaKMInicial(instance=minutaform)
    form_km_final = CadastraMinutaKMFinal(instance=minutaform)
    contexto = {'s_minuta': s_minuta, 'form_km_inicial': form_km_inicial, 'form_km_final': form_km_final}
    return contexto


def edita_hora_final(request, idminuta, hora_final):
    obj = get_minuta(idminuta)
    hora_final = datetime.strptime(hora_final, '%H:%M').time()
    if hora_final <= obj.HoraInicial:
        obj.HoraFinal = '00:00'
        mensagem = f'VOCÊ DIGITOU {hora_final}, MAS A HORA FINAL TEM QUE SER MAIOR QUE {obj.HoraInicial}.'
        tipo_mensagem = 'ERROR'
    else:
        obj.HoraFinal = hora_final
        mensagem = 'A HORA FINAL FOI ATUALIZADA.'
        tipo_mensagem = 'SUCESSO'
    obj.save(update_fields=['HoraFinal'])
    s_minuta = MinutaSelecionada(idminuta)
    total_horas_str = s_minuta.total_horas_str
    data = dict()
    data['html_mensagem'] = mensagem
    data['html_tipo_mensagem'] = tipo_mensagem
    data['html_total_horas'] = f'{total_horas_str} Hs'
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
        mensagem = 'A KILOMETRAGEM INICIAL FOi ATUALIZADA, A KILOMETRAGEM FINAL FOI ZERADA'
        tipo_mensagem = 'SUCESSO'
        obj.save(update_fields=['KMInicial', 'KMFinal'])
    else:
        obj.KMInicial = km_inicial
        mensagem = 'A KILOMETRAGEM INICIAL FOi ATUALIZADA.'
        tipo_mensagem = 'SUCESSO'
        obj.save(update_fields=['KMInicial'])
    s_minuta = MinutaSelecionada(idminuta)
    total_kms = s_minuta.total_kms
    data = dict()
    data['html_mensagem'] = mensagem
    data['html_tipo_mensagem'] = tipo_mensagem
    data['html_total_kms'] = f'{total_kms} KMs'
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, idminuta)
    c_return = JsonResponse(data)
    return c_return


def edita_km_final(request, idminuta, km_final):
    obj = get_minuta(idminuta)
    km_final = int(km_final)
    if km_final <= obj.KMInicial:
        obj.KMFinal = 0
        mensagem = f'VOCÊ DIGITOU {km_final}, MAS A KILOMETRAGEM FINAL TEM QUE SER MAIOR QUE {obj.KMInicial}.'
        tipo_mensagem = 'ERROR'
    else:
        obj.KMFinal = km_final
        mensagem = 'A KILOMETRAGEM FINAL FOI ATUALIZADA.'
        tipo_mensagem = 'SUCESSO'
    obj.save(update_fields=['KMFinal'])
    s_minuta = MinutaSelecionada(idminuta)
    total_kms = s_minuta.total_kms
    data = dict()
    data['html_mensagem'] = mensagem
    data['html_tipo_mensagem'] = tipo_mensagem
    data['html_total_kms'] = f'{total_kms} KMs'
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, idminuta)
    c_return = JsonResponse(data)
    return c_return


def ajudantes_disponiveis(idminuta):
    ajudantes_minuta = MinutaColaboradores.objects.filter(idMinuta=idminuta, Cargo='AJUDANTE').values('idPessoal')
    pessoas = Pessoal.objects.filter(StatusPessoal=True).exclude(idPessoal__in=ajudantes_minuta)
    return pessoas


def motoristas_disponiveis():
    pessoas = Pessoal.objects.filter(StatusPessoal=True).exclude(Categoria='AJUDANTE')
    return pessoas


def veiculo_selecionado(idpessoal, idminuta):
    veiculo = Veiculo.objects.filter(Motorista=idpessoal)
    if len(veiculo) == 1:
        km_inicial = km_atual(veiculo[0])
        obj = get_minuta(idminuta)
        obj.idVeiculo = veiculo[0]
        obj.KMInicial = km_inicial['KMFinal__max']
        obj.save(update_fields=['idVeiculo', 'KMInicial'])


def filtra_veiculo(idpessoal, opcao):
    veiculos = []
    if opcao == 'PROPRIO':
        veiculos = Veiculo.objects.filter(Motorista=idpessoal).order_by('Marca', 'Modelo', 'Placa')
    elif opcao == 'TRANSPORTADORA':
        veiculos = Veiculo.objects.filter(Proprietario=17).order_by('Marca', 'Modelo', 'Placa')
    elif opcao == 'CADASTRADOS':
        veiculos = Veiculo.objects.all().order_by('Marca', 'Modelo', 'Placa')
    lista_veiculos = []
    for veiculo in veiculos:
        descricao_veiculo = f'{veiculo.Marca} - {veiculo.Modelo} - {veiculo.Placa}'
        lista_veiculos.append({'idVeiculo': veiculo.idVeiculo, 'Veiculo': descricao_veiculo})
    return lista_veiculos


def remove_colaborador(request, idminutacolaborador, idminuta, cargo):
    colaborador = MinutaColaboradores.objects.get(idMinutaColaboradores=idminutacolaborador)
    colaborador.delete()
    obj = get_minuta(idminuta)
    obj.idVeiculo = None
    obj.KMInicial = 0
    obj.KMFinal = 0
    obj.save(update_fields=['idVeiculo', 'KMInicial', 'KMFinal'])
    data = dict()
    if cargo == 'AJUDANTE':
        data = html_ajudantes(request, data, idminuta)
    elif cargo == 'MOTORISTA':
        data = html_motorista(request, data, idminuta)
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, idminuta)
    return data


def remove_despessa(request, idminutaitens, idminuta):
    despesa = MinutaItens.objects.get(idMinutaItens=idminutaitens)
    despesa.delete()
    data = dict()
    data = html_despesa(request, data, idminuta)
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, idminuta)
    return data


def remove_entrega(request, idminutanota, idminuta):
    entrega = MinutaNotas.objects.get(idMinutaNotas=idminutanota)
    entrega.delete()
    data = dict()
    data = html_entrega(request, data, idminuta)
    data = html_pagamento(request, data, idminuta)
    data = html_checklist(request, data, idminuta)
    return data


def html_cliente_data(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data['html_cliente_data'] = render_to_string('minutas/clientedataminuta.html', contexto, request=request)
    return data


def html_motorista(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data['html_veiculo'] = render_to_string('minutas/veiculominuta.html', contexto, request=request)
    return data


def html_ajudantes(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data['html_ajudante'] = render_to_string('minutas/ajudantesminuta.html', contexto, request=request)
    return data


def html_categoria(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data['html_categoria'] = render_to_string('minutas/categoriaminuta.html', contexto, request=request)
    data['html_veiculo'] = render_to_string('minutas/veiculominuta.html', contexto, request=request)
    return data


def html_veiculo(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data['html_veiculo'] = render_to_string('minutas/veiculominuta.html', contexto, request=request)
    return data


def html_filtro_veiculo(request, lista_veiculos):
    data = dict()
    contexto = {'lista_veiculos': lista_veiculos}
    data['html_filtro'] = render_to_string('minutas/listaveiculosminuta.html', contexto, request=request)
    c_return = JsonResponse(data)
    return c_return


def html_coleta_entrega_obs(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data['html_coleta_entrega_obs'] = render_to_string('minutas/coletaentregaobsminuta.html', contexto, request=request)
    return data


def html_despesa(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data['html_despesa'] = render_to_string('minutas/despesaminuta.html', contexto, request=request)
    return data


def html_entrega(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data['html_entrega'] = render_to_string('minutas/entregaminuta.html', contexto, request=request)
    return data


def html_pagamento(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data['html_pagamento'] = render_to_string('minutas/formpagamento.html', contexto, request=request)
    return data


def html_checklist(request, data, idminuta):
    contexto = cria_contexto(idminuta)
    data['html_checklist'] = render_to_string('minutas/checklistminuta.html', contexto, request=request)
    return data


def retorna_json(data):
    c_return = JsonResponse(data)
    return c_return


def forn_minuta(request, c_form, c_idobj, c_url, c_view):
    print(c_form, c_idobj, c_url, c_view)
    data = dict()
    c_instance = None
    mensagem = None
    tipo_mensagem = None
    if request.method == 'POST':
        form = c_form(request.POST)
        if form.is_valid():
            if c_view == 'adiciona_minuta':
                minuta_salva = form.save()
                id_minuta_salva = minuta_salva.idMinuta
                data['id_minuta_salva'] = id_minuta_salva
            else:
                if c_view == 'edita_minuta':
                    cliente = get_cliente(request.POST.get('idCliente'))
                    obj = get_minuta(c_idobj)
                    obj.idCliente = cliente
                    obj.DataMinuta = request.POST.get('DataMinuta')
                    obj.HoraInicial = request.POST.get('HoraInicial')
                    obj.save(update_fields=['idCliente', 'DataMinuta', 'HoraInicial'])
                    mensagem = 'OS ITENS CLIENTE, DATA E HORA INICIAL DA MINUTA FORAM ATUALIZADOS.'
                    tipo_mensagem = 'SUCESSO'
                    data = html_cliente_data(request, data, c_idobj)
                if c_view == 'insere_ajudante':
                    form.save()
                    data = html_ajudantes(request, data, c_idobj)
                if c_view == 'insere_motorista':
                    form.save()
                    idpessoal = request.POST.get('idPessoal')
                    veiculo_selecionado(idpessoal, c_idobj)
                    data = html_motorista(request, data, c_idobj)
                elif c_view == 'edita_minuta_veiculo_solicitado':
                    obj = get_minuta(c_idobj)
                    if request.POST.get('idCategoriaVeiculo'):
                        categoria = get_categoria(request.POST.get('idCategoriaVeiculo'))
                        obj.idCategoriaVeiculo = categoria
                        mensagem = 'O VEICULO SOLICITADO FOI ATUALIZADO.'
                    else:
                        obj.idCategoriaVeiculo = None
                        mensagem = 'O VEICULO SOLICITADO FOI REMOVIDO.'
                    obj.save(update_fields=['idCategoriaVeiculo'])
                    tipo_mensagem = 'SUCESSO'
                    data = html_categoria(request, data, c_idobj)
                elif c_view == 'edita_minuta_veiculo_escolhido':
                    idveiculo = request.POST.get('idVeiculo')
                    if request.POST.get('idVeiculo'):
                        veiculo = Veiculo.objects.filter(idVeiculo=idveiculo)
                        km_inicial = km_atual(veiculo[0])
                        if len(veiculo) == 1:
                            obj = get_minuta(c_idobj)
                            obj.idVeiculo = veiculo[0]
                            obj.KMInicial = km_inicial['KMFinal__max']
                            obj.save(update_fields=['idVeiculo', 'KMInicial'])
                        mensagem = 'O VEICULO ESCOLHIDO FOI ATUALIZADO.'
                        tipo_mensagem = 'SUCESSO'
                        data = html_veiculo(request, data, c_idobj)
                elif c_view == 'edita_minuta_coleta_entrega_obs':
                    obj = get_minuta(c_idobj)
                    obj.Entrega = request.POST.get('Entrega')
                    obj.Coleta = request.POST.get('Coleta')
                    obj.Obs = request.POST.get('Obs')
                    obj.save(update_fields=['Coleta', 'Entrega', 'Obs'])
                    mensagem = 'AS INFORMAÇÕES DE COLETA, ENTREGA E OBSERVAÇÕES FORAM ATUALIZADAS.'
                    tipo_mensagem = 'SUCESSO'
                    data = html_coleta_entrega_obs(request, data, c_idobj)
                elif c_view == 'insere_minuta_despesa':
                    form.save()
                    mensagem = 'DESPESA INSERIDA.'
                    tipo_mensagem = 'SUCESSO'
                    data = html_despesa(request, data, c_idobj)
                elif c_view == 'insere_minuta_entrega':
                    form.save()
                    mensagem = 'ENTREGA INSERIDA.'
                    tipo_mensagem = 'SUCESSO'
                    data = html_entrega(request, data, c_idobj)
                data = html_pagamento(request, data, c_idobj)
                data = html_checklist(request, data, c_idobj)
        else:
            print('Form não é valido')
    else:
        if c_view == 'edita_minuta':
            c_instance = get_minuta(c_idobj)
        if c_view == 'edita_minuta_coleta_entrega_obs':
            c_instance = get_minuta(c_idobj)
        if c_view == 'edita_minuta_insere_despesa':
            c_instance = get_minuta(c_idobj)
        form = c_form(instance=c_instance)
    if c_idobj:
        ajudantes = ajudantes_disponiveis(c_idobj)
        motoristas = motoristas_disponiveis()
        idpessoal = request.GET.get('idPessoal')
        s_minuta = MinutaSelecionada(c_idobj)
        despesas = MinutaItens.objects.filter(TipoItens='DESPESA').values('Descricao').distinct().order_by('Descricao')
        lista_veiculos = []
        minuta = s_minuta.numero
        contexto = {'form': form, 'c_idobj': c_idobj, 'c_url': c_url, 'c_view': c_view, 'ajudantes': ajudantes,
                    'motoristas': motoristas, 'lista_veiculos': lista_veiculos, 'idpessoal': idpessoal,
                    's_minuta': s_minuta, 'despesas': despesas, 'minuta': minuta}
    else:
        minuta = proxima_minuta()
        contexto = {'form': form, 'c_idobj': c_idobj, 'c_url': c_url, 'c_view': c_view, 'minuta': minuta}
    data['html_form'] = render_to_string('minutas/formminuta.html', contexto, request=request)
    data['c_view'] = c_view
    data['html_mensagem'] = mensagem
    data['html_tipo_mensagem'] = tipo_mensagem
    # if request.method == 'POST':
    #     print(data['html_form'])
    #     print(data['c_view'])
    #     print(data['html_mensagem'])
    #     print(data['html_tipo_mensagem'])
    #     print(data['html_veiculo'])
    c_return = JsonResponse(data)
    return c_return
