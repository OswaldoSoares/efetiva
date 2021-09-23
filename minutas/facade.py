from datetime import datetime, timedelta

from clientes.models import TabelaPerimetro, TabelaVeiculo, TabelaCapacidade, Tabela
from minutas.models import MinutaColaboradores, Minuta, MinutaItens, MinutaNotas


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
        self.total_horas = self.total_horas()
        self.total_kms = self.total_kms()

    def total_kms(self):
        minuta_selecionada = self.km_final - self.km_inicial
        return minuta_selecionada

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
        total_horas = self.total_horas()
        dezhoras = timedelta(days=0, hours=10, minutes=0)
        fator = 0.00
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

    def total_horas(self):
        periodo = timedelta(hours=0, minutes=0)
        if self.hora_final:
            inicial = datetime.combine(self.data, self.hora_inicial)
            final = datetime.combine(self.data, self.hora_final)
            if inicial < final:
                periodo = final - inicial
        return periodo

    def horas_excede(self):
        excede = timedelta(hours=0, minutes=0)
        minimo = timedelta(hours=0, minutes=0)
        periodo = self.total_horas()
        filtro_tabela_veiculo = self.filtro_tabela_veiculo()
        if filtro_tabela_veiculo:
            minimo = timedelta(days=0, hours=filtro_tabela_veiculo['HoraMinimo'].hour,
                               minutes=filtro_tabela_veiculo['HoraMinimo'].minute)
        if periodo > minimo:
            excede = periodo - minimo
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

    def carrega_valores_paga(self):
        hora_zero_timedelta = timedelta(hours=0, minutes=0)
        hora_zero_time = datetime.strptime('00:00', '%H:%M').time()
        tabela_veiculo = self.filtro_tabela_veiculo()
        valores_paga = dict({'valor_porcentagem': 0.00, 'minuta_porcentagem': 0.00, 'valor_hora': 0.00,
                             'minuta_hora': hora_zero_time, 'valor_horaexcede': 100.00,
                             'minuta_horaexcede': hora_zero_timedelta,
                             'valor_kilometragem': 0.00, 'minuta_kilometragem': 0.00, 'valor_entregas': 0.00,
                             'minuta_entregas': 0.00, 'valor_entregaskg': 0.00, 'minuta_entregaskg': 0.00,
                             'valor_entregasvolume': 0.00, 'minuta_entregasvolume': 0.00, 'valor_saida': 0.00,
                             'valor_capacidade': 0.00, 'valor_perimetro': 0.00, 'valor_ajudante': 0.00,
                             'minuta_ajudante': 0.00})
        if tabela_veiculo:
            valores_paga['valor_porcentagem'] = tabela_veiculo['PorcentagemPaga']
            valores_paga['minuta_porcentagem'] = self.total_notas()[0]
            valores_paga['valor_hora'] = self.filtro_tabela_veiculo()['HoraPaga']
            valores_paga['minuta_hora'] = self.filtro_tabela_veiculo()['HoraMinimo']
            valores_paga['valor_horaexcede'] = 100
            valores_paga['minuta_horaexcede'] = self.horas_excede()
            valores_paga['valor_kilometragem'] = self.filtro_tabela_veiculo()['KMPaga']
            valores_paga['minuta_kilometragem'] = self.total_kms()
            valores_paga['valor_entregas'] = self.filtro_tabela_veiculo()['EntregaPaga']
            valores_paga['minuta_entregas'] = self.total_notas()[3]
            valores_paga['valor_entregaskg'] = self.filtro_tabela_veiculo()['EntregaKGPaga']
            valores_paga['minuta_entregaskg'] = self.total_notas()[2]
            valores_paga['valor_entregasvolume'] = self.filtro_tabela_veiculo()['EntregaVolumePaga']
            valores_paga['minuta_entregasvolume'] = self.total_notas()[1]
            valores_paga['valor_saida'] = self.filtro_tabela_veiculo()['SaidaPaga']
            capacidade = [itens['CapacidadePaga'] for itens in self.tabela_capacidade if itens['CapacidadeInicial'] <=
                          self.total_kms() <= itens['CapacidadeFinal']]
            if capacidade:
                valores_paga['valor_capacidade'] = capacidade[0]
            else:
                valores_paga['valor_capacidade'] = 0.00
            perimetro = [itens['PerimetroPaga'] for itens in self.tabela_perimetro if itens['PerimetroInicial'] <=
                         self.total_kms() <= itens['PerimetroFinal']]
            if perimetro:
                valores_paga['valor_perimetro'] = perimetro[0]
            else:
                valores_paga['valor_perimetro'] = 0.00
            valores_paga['valor_ajudante'] = self.tabela[0]['AjudantePaga']
            if self.total_ajudantes() > 0 and self.saidas_ajudante() > 0:
                valores_paga['valor_ajudante'] = float(self.tabela[0]['AjudantePaga']) + 10.00
            valores_paga['minuta_ajudante'] = self.total_ajudantes_avulso()
        return valores_paga

    def lista_pagamentos(self):
        paga = self.carrega_valores_paga()
        porcentagem_paga = MinutaFinanceiro('PORCENTAGEM DA NOTA', 'porcentagem', '%', paga['valor_porcentagem'],
                                            'R$', paga['minuta_porcentagem'])
        horas_paga = MinutaFinanceiro('HORAS', 'horas', 'R$', paga['valor_hora'], 'HS', paga['minuta_hora'])
        horasexcede_paga = MinutaFinanceiro('HORAS EXCEDENTE', 'horasexcede', '%', paga['valor_horaexcede'], 'HS',
                                            paga['minuta_horaexcede'])
        kilometragem_paga = MinutaFinanceiro('KILOMETRAGEM', 'kilometragem', 'R$', paga['valor_kilometragem'], 'UN',
                                             paga['minuta_kilometragem'])
        entregas_paga = MinutaFinanceiro('ENTREGAS', 'entregas', 'R$', paga['valor_entregas'], 'UN',
                                         paga['minuta_entregas'])
        entregaskg_paga = MinutaFinanceiro('ENTREGAS KG', 'entregaskg', 'R$', paga['valor_entregaskg'], 'KG',
                                           paga['minuta_entregaskg'])
        entregasvolume_paga = MinutaFinanceiro('ENTREGAS VOLUME', 'entregasvolume', 'R$',
                                               paga['valor_entregasvolume'], 'UN', paga['minuta_entregasvolume'])
        saida_paga = MinutaFinanceiro('SAIDA', 'saida', 'R$', paga['valor_saida'], '', '')
        capacidade_paga = MinutaFinanceiro('CAPACIDADE PESO', 'capacidade', 'R$', paga['valor_capacidade'], '', '')
        perimetro_paga = MinutaFinanceiro('PERIMETRO', 'perimetro', '%', paga['valor_perimetro'], 'R$', 0.00)
        pernoite_paga = MinutaFinanceiro('PERNOITE', 'pernoite', '%', 0.00, 'R$', 0.00)
        ajudante_paga = MinutaFinanceiro('AJUDANTE', 'ajudante', 'R$', paga['valor_ajudante'], 'UN',
                                         paga['minuta_ajudante'])
        itens_paga = list()
        itens_paga.append(porcentagem_paga.__dict__)
        itens_paga.append(horas_paga.__dict__)
        itens_paga.append(horasexcede_paga.__dict__)
        itens_paga.append(kilometragem_paga.__dict__)
        itens_paga.append(entregas_paga.__dict__)
        itens_paga.append(entregaskg_paga.__dict__)
        itens_paga.append(entregasvolume_paga.__dict__)
        itens_paga.append(saida_paga.__dict__)
        itens_paga.append(capacidade_paga.__dict__)
        itens_paga.append(perimetro_paga.__dict__)
        itens_paga.append(pernoite_paga.__dict__)
        itens_paga.append(ajudante_paga.__dict__)
        return itens_paga

    def saldo_paga_phkesc(self):
        lista_itens_paga = self.lista_pagamentos()
        valor_minuto = 0.00
        for itens in lista_itens_paga:
            if itens['descricao'] == 'PORCENTAGEM DA NOTA':
                itens['saldo'] = float(itens['valor_tabela']) * float(itens['valor_minuta']) / 100
            elif itens['descricao'] == 'HORAS':
                valor_minuto = float(itens['valor_tabela']) / 60
                minutos_hora = itens['valor_minuta'].strftime('%H:%M').split(':')
                minutos_hora = int(minutos_hora[0]) * 60 + int(minutos_hora[1])
                itens['saldo'] = valor_minuto * minutos_hora
            elif itens['descricao'] == 'HORAS EXCEDENTE':
                valor_minuto = valor_minuto * itens['valor_tabela'] / 100
                segundos = itens['valor_minuta'].total_seconds()
                minutos_hora_excede = segundos / 60
                itens['saldo'] = valor_minuto * minutos_hora_excede
            elif itens['descricao'] == 'KILOMETRAGEM' or itens['descricao'] == 'ENTREGAS' or itens['descricao'] \
                    == 'ENTREGAS VOLUME':
                itens['saldo'] = float(itens['valor_tabela']) * itens['valor_minuta']
            elif itens['descricao'] == 'ENTREGAS KG':
                itens['saldo'] = float(itens['valor_tabela'] * itens['valor_minuta'])
            elif itens['descricao'] == 'SAIDA' or itens['descricao'] == 'CAPACIDADE':
                itens['saldo'] = float(itens['valor_tabela'])
        saldo_paga = 0.00
        for itens in lista_itens_paga:
            saldo_paga += itens['saldo']
        return lista_itens_paga, saldo_paga

    def saldos_paga(self):
        lista_itens_paga, saldo_paga = self.saldo_paga_phkesc()
        saldo_paga_adiciona = 0.00
        for itens in lista_itens_paga:
            if itens['descricao'] == 'PERIMETRO' or itens['descricao'] == 'PERNOITE':
                itens['valor_minuta'] = float(saldo_paga)
                itens['saldo'] = (float(itens['valor_tabela']) * float(saldo_paga)) / 100
                saldo_paga_adiciona += itens['saldo']
            elif itens['descricao'] == 'AJUDANTE':
                itens['saldo'] = float(itens['valor_tabela']) * itens['valor_minuta']
                saldo_paga_adiciona += itens['saldo']
        saldo_paga += saldo_paga_adiciona
        return lista_itens_paga, saldo_paga

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
            valores_recebe['minuta_kilometragem'] = self.total_kms()
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
                         self.total_kms() <= itens['PerimetroFinal']]
            if perimetro:
                valores_recebe['valor_perimetro'] = perimetro[0]
            else:
                valores_recebe['valor_perimetro'] = 0.00
            valores_recebe['valor_ajudante'] = self.extra_ajudante_cobra()
            valores_recebe['minuta_ajudante'] = self.total_ajudantes()
        return valores_recebe

    def lista_recebimentos(self):
        recebe = self.carrega_valores_recebe()
        taxa_expedicao_recebe = MinutaFinanceiro('TAXA DE EXPEDIÇÃO', 'taxaexpedicao', 'R$',
                                                 recebe['valor_taxaexpedicao'], '', '')
        seguro_recebe = MinutaFinanceiro('SEGURO', 'seguro', '%', recebe['valor_seguro'], 'R$', recebe['minuta_seguro'])
        porcentagem_recebe = MinutaFinanceiro('PORCENTAGEM DA NOTA', 'porcentagem', '%', recebe['valor_porcentagem'],
                                              'R$', recebe['minuta_porcentagem'])
        horas_recebe = MinutaFinanceiro('HORAS', 'horas', 'R$', recebe['valor_hora'], 'HS', recebe['minuta_hora'])
        horasexcede_recebe = MinutaFinanceiro('HORAS EXCEDENTE', 'horasexcede', '%', recebe['valor_horaexcede'], 'HS',
                                              recebe['minuta_horaexcede'])
        kilometragem_recebe = MinutaFinanceiro('KILOMETRAGEM', 'kilometragem', 'R$', recebe['valor_kilometragem'], 'UN',
                                               recebe['minuta_kilometragem'])
        entregas_recebe = MinutaFinanceiro('ENTREGAS', 'entregas', 'R$', recebe['valor_entregas'], 'UN',
                                           recebe['minuta_entregas'])
        entregaskg_recebe = MinutaFinanceiro('ENTREGAS KG', 'entregaskg', 'R$', recebe['valor_entregaskg'], 'KG',
                                             recebe['minuta_entregaskg'])
        entregasvolume_recebe = MinutaFinanceiro('ENTREGAS VOLUME', 'entregasvolume', 'R$',
                                                 recebe['valor_entregasvolume'], 'UN', recebe['minuta_entregasvolume'])
        saida_recebe = MinutaFinanceiro('SAIDA', 'saida', 'R$', recebe['valor_saida'], '', '')
        capacidade_recebe = MinutaFinanceiro('CAPACIDADE PESO', 'capacidade', 'R$', recebe['valor_capacidade'], '', '')
        perimetro_recebe = MinutaFinanceiro('PERIMETRO', 'perimetro', '%', recebe['valor_perimetro'], 'R$', 0.00)
        pernoite_recebe = MinutaFinanceiro('PERNOITE', 'pernoite', '%', 0.00, 'R$', 0.00)
        ajudante_recebe = MinutaFinanceiro('AJUDANTE', 'ajudante', 'R$', recebe['valor_ajudante'], 'UN',
                                           recebe['minuta_ajudante'])
        itens_recebe = list()
        itens_recebe.append(taxa_expedicao_recebe.__dict__)
        itens_recebe.append(seguro_recebe.__dict__)
        itens_recebe.append(porcentagem_recebe.__dict__)
        itens_recebe.append(horas_recebe.__dict__)
        itens_recebe.append(horasexcede_recebe.__dict__)
        itens_recebe.append(kilometragem_recebe.__dict__)
        itens_recebe.append(entregas_recebe.__dict__)
        itens_recebe.append(entregaskg_recebe.__dict__)
        itens_recebe.append(entregasvolume_recebe.__dict__)
        itens_recebe.append(saida_recebe.__dict__)
        itens_recebe.append(capacidade_recebe.__dict__)
        itens_recebe.append(perimetro_recebe.__dict__)
        itens_recebe.append(pernoite_recebe.__dict__)
        itens_recebe.append(ajudante_recebe.__dict__)
        return itens_recebe

    def saldo_recebe_phkesc(self):
        lista_itens_recebe = self.lista_recebimentos()
        valor_minuto = 0.00
        for itens in lista_itens_recebe:
            if itens['descricao'] == 'PORCENTAGEM DA NOTA':
                itens['saldo'] = float(itens['valor_tabela']) * float(itens['valor_minuta']) / 100
            elif itens['descricao'] == 'HORAS':
                valor_minuto = float(itens['valor_tabela']) / 60
                minutos_hora = itens['valor_minuta'].strftime('%H:%M').split(':')
                minutos_hora = int(minutos_hora[0]) * 60 + int(minutos_hora[1])
                itens['saldo'] = valor_minuto * minutos_hora
            elif itens['descricao'] == 'HORAS EXCEDENTE':
                valor_minuto = valor_minuto * itens['valor_tabela'] / 100
                segundos = itens['valor_minuta'].total_seconds()
                minutos_hora_excede = segundos / 60
                itens['saldo'] = valor_minuto * minutos_hora_excede
            elif itens['descricao'] == 'KILOMETRAGEM' or itens['descricao'] == 'ENTREGAS' or itens['descricao'] \
                    == 'ENTREGAS VOLUME':
                itens['saldo'] = float(itens['valor_tabela']) * itens['valor_minuta']
            elif itens['descricao'] == 'ENTREGAS KG':
                itens['saldo'] = float(itens['valor_tabela'] * itens['valor_minuta'])
            elif itens['descricao'] == 'SAIDA' or itens['descricao'] \
                    == 'CAPACIDADE':
                itens['saldo'] = float(itens['valor_tabela'])
        saldo_recebe = 0.00
        for itens in lista_itens_recebe:
            saldo_recebe += itens['saldo']
        return lista_itens_recebe, saldo_recebe

    def saldos_recebe(self):
        lista_itens_recebe, saldo_recebe = self.saldo_recebe_phkesc()
        saldo_recebe_adiciona = 0.00
        for itens in lista_itens_recebe:
            if itens['descricao'] == 'PERIMETRO' or itens['descricao'] == 'PERNOITE':
                itens['valor_minuta'] = float(saldo_recebe)
                itens['saldo'] = (float(itens['valor_tabela']) * float(saldo_recebe)) / 100
                saldo_recebe_adiciona += itens['saldo']
            elif itens['descricao'] == 'TAXA DE EXPEDIÇÃO':
                itens['saldo'] = float(itens['valor_tabela'])
                saldo_recebe_adiciona += itens['saldo']
            elif itens['descricao'] == 'SEGURO':
                itens['saldo'] = float(itens['valor_tabela']) * float(itens['valor_minuta']) / 100
                itens['saldo'] = round(itens['saldo'], 2)
                saldo_recebe_adiciona += itens['saldo']
            elif itens['descricao'] == 'AJUDANTE':
                itens['saldo'] = float(itens['valor_tabela']) * itens['valor_minuta']
                saldo_recebe_adiciona += itens['saldo']
        saldo_recebe += saldo_recebe_adiciona
        return lista_itens_recebe, saldo_recebe


class MinutaMotorista:
    def __init__(self, idminuta):
        self.nome = self.get_motorista(idminuta)

    @staticmethod
    def get_motorista(idminuta):
        motorista = MinutaColaboradores.objects.filter(idMinuta=idminuta, Cargo='MOTORISTA')
        lista = [{'idMinutaColaboradores': itens.idMinutaColaboradores, 'nome': itens.idPessoal.Nome}
                 for itens in motorista]
        if lista:
            lista[0]['apelido'] = nome_curto(lista[0]['nome'])
        return lista


class MinutaAjudantes:
    def __init__(self, idminuta):
        self.nome = self.get_ajudantes(idminuta)

    @staticmethod
    def get_ajudantes(idminuta):
        ajudantes = MinutaColaboradores.objects.filter(idMinuta=idminuta, Cargo='AJUDANTE')
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
