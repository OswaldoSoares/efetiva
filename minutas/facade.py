from datetime import datetime, timedelta

from clientes.models import TabelaPerimetro, TabelaVeiculo, TabelaCapacidade, Tabela
from minutas.models import MinutaColaboradores, Minuta, MinutaItens, MinutaNotas


class MinutaSelecionada:
    def __init__(self, idminuta):
        minuta = Minuta.objects.get(idMinuta=idminuta)
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
        self.despesas = MinutaDespesa(idminuta)
        self.entregas = MinutaEntrega(idminuta).nota
        self.tabela = ClienteTabela(minuta.idCliente).tabela
        self.tabela_veiculo = ClienteTabelaVeiculo(minuta.idCliente).tabela
        self.tabela_perimetro = ClienteTabelaPerimetro(minuta.idCliente).tabela
        self.tabela_capacidade = ClienteTabelaCapacidade(minuta.idCliente).tabela

    def total_kms(self):
        minuta_selecionada = self.km_final - self.km_inicial
        return minuta_selecionada

    def saidas_ajudante(self):
        if self.ajudantes:
            saidas = len(self.entregas)
            return saidas

    def total_horas(self):
        if self.hora_final:
            inicial = datetime.combine(self.data, self.hora_inicial)
            final = datetime.combine(self.data, self.hora_final)
            if inicial < final:
                periodo = final - inicial
                return periodo

    def horas_excede(self):
        periodo = self.total_horas()
        filtro_tabela_veiculo = [itens for itens in self.tabela_veiculo if itens['idCategoriaVeiculo'] ==
                                 self.veiculo_solicitado]
        minimo = timedelta(days=0, hours=filtro_tabela_veiculo[0]['HoraMinimo'].hour,
                           minutes=filtro_tabela_veiculo[0]['HoraMinimo'].minute)
        if periodo > minimo:
            excede = periodo - minimo
            return excede

    def total_notas(self):
       valor_entregas = sum([itens['ValorNota'] for itens in self.entregas])
       volume_entregas = sum([itens['Volume'] for itens in self.entregas])
       peso_entregas = sum([itens['Peso'] for itens in self.entregas])
       return valor_entregas, volume_entregas, peso_entregas


class MinutaMotorista:
    def __init__(self, idminuta):
        self.nome = self.get_motorista(idminuta)

    @staticmethod
    def get_motorista(idminuta):
        motorista = MinutaColaboradores.objects.filter(idMinuta=idminuta, Cargo='MOTORISTA')
        lista = [{'idMinutaColaboradores': itens.idMinutaColaboradores, 'nome': itens.idPessoal.Nome}
                 for itens in motorista]
        return lista


class MinutaAjudantes:
    def __init__(self, idminuta):
        self.nome = self.get_ajudantes(idminuta)

    @staticmethod
    def get_ajudantes(idminuta):
        ajudantes = MinutaColaboradores.objects.filter(idMinuta=idminuta, Cargo='AJUDANTE')
        lista = [{'idMinutaColaboradores': itens.idMinutaColaboradores, 'nome': itens.idPessoal.Nome}
                 for itens in ajudantes]
        return lista


class MinutaDespesa:
    def __init__(self, idminuta):
        self.descricao = self.get_despesas(idminuta)

    @staticmethod
    def get_despesas(idminuta):
        despesas = MinutaItens.objects.filter(idMinuta=idminuta, TipoItens='DESPESA')
        lista = [{'idMinutaItens': itens.idMinutaItens, 'Descricao': itens.Descricao, 'Valor': itens.Valor}
                 for itens in despesas]
        return lista


class MinutaEntrega:
    def __init__(self, idminuta):
        self.nota = self.get_entregas(idminuta)

    @staticmethod
    def get_entregas(idminuta):
        entregas = MinutaNotas.objects.filter(idMinuta=idminuta)
        lista = [{'idMinutaNotas': itens.idMinutaNotas, 'Nota': itens.Nota, 'ValorNota': itens.ValorNota,
                  'Peso': itens.Peso, 'Volume': itens.Volume} for itens in entregas]
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
        self.valor_tabela = valor_tabela
        self.tipo_valor_tabela = tipo_valor_tabela
        self.valor_minuta = valor_minuta
        self.tipo_valor_minuta = tipo_valor_minuta
        self.saldo = 0.00
        self.checked = False

    def checked_on(self):
        self.checked = True

    def checked_off(self):
        self.checked = False


def get_total_ajudantes(idminuta):
    return MinutaColaboradores.objects.filter(idMinuta=idminuta, Cargo='AJUDANTE').count()


def cria_pagamentos():
    porcentagem_paga = MinutaFinanceiro('PORCENTAGEM DA NOTA', 'porcentagem', '%', 0.00, 'R$', 0.00)
    horas_paga = MinutaFinanceiro('HORAS', 'horas', 'R$', 0.00, 'HS', '00:00')
    horasexcede_paga = MinutaFinanceiro('HORAS EXCEDENTE', 'horasexcede', '%', 0.00, 'HS', '00:00')
    kilometragem_paga = MinutaFinanceiro('KILOMETRAGEM', 'kilometragem', 'R$', 0.00, 'UN', 0)
    entregas_paga = MinutaFinanceiro('ENTREGAS', 'entregas', 'R$', 0.00, 'UN', 0)
    entregaskg_paga = MinutaFinanceiro('ENTREGAS KG', 'entregaskg', 'R$', 0.00, 'KG', 0.00)
    entregasvolume_paga = MinutaFinanceiro('ENTREGAS VOLUME', 'entregasvolume', 'R$', 0.00, 'UN', 0)
    saida_paga = MinutaFinanceiro('SAIDA', 'saida', 'R$', 0.00, '', '')
    capacidade_paga = MinutaFinanceiro('CAPACIDADE PESO', 'capacidade', 'R$', 0.00, '', '')
    perimetro_paga = MinutaFinanceiro('PERIMETRO', 'perimetro', '%', 0.00, 'R$', 0.00)
    pernoite_paga = MinutaFinanceiro('PERNOITE', 'pernoite', '%', 0.00, 'R$', 0.00)
    ajudante_paga = MinutaFinanceiro('AJUDANTE', 'ajudante', 'R$', 0.00, 'UN', 0)

    itens_paga = list()
    itens_paga.append(porcentagem_paga)
    itens_paga.append(horas_paga)
    itens_paga.append(horasexcede_paga)
    itens_paga.append(kilometragem_paga)
    itens_paga.append(entregas_paga)
    itens_paga.append(entregaskg_paga)
    itens_paga.append(entregasvolume_paga)
    itens_paga.append(saida_paga)
    itens_paga.append(capacidade_paga)
    itens_paga.append(perimetro_paga)
    itens_paga.append(pernoite_paga)
    itens_paga.append(ajudante_paga)
