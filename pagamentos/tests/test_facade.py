import datetime
import decimal

import pytest
from dateutil.relativedelta import relativedelta


@pytest.mark.django_db()
class TestFolhaCartaoPonto:
    @pytest.fixture
    def cartao_de_ponto(self):
        from pagamentos.facade import FolhaCartaoPonto

        folha_cartao_de_ponto = FolhaCartaoPonto("OSWALDO")
        return folha_cartao_de_ponto

    def test_cartao_ponto_atributo_alteracao(self, cartao_de_ponto):
        v_cartao_ponto = cartao_de_ponto
        assert v_cartao_ponto.alteracao

    def test_cartao_ponto_atributo_ausencia(self, cartao_de_ponto):
        v_cartao_ponto = cartao_de_ponto
        assert v_cartao_ponto.ausencia

    def test_cartao_ponto_atributo_dia(self, cartao_de_ponto):
        v_cartao_ponto = cartao_de_ponto
        assert v_cartao_ponto.dia

    def test_cartao_ponto_atributo_hora_entrada(self, cartao_de_ponto):
        v_cartao_ponto = cartao_de_ponto
        assert v_cartao_ponto.hora_entrada

    def test_cartao_ponto_atributo_hora_saida(self, cartao_de_ponto):
        v_cartao_ponto = cartao_de_ponto
        assert v_cartao_ponto.hora_saida

    def test_cartao_ponto_atributo_nome(self, cartao_de_ponto):
        v_cartao_ponto = cartao_de_ponto
        assert v_cartao_ponto.nome


class TestFolhaConttaCheque:
    @pytest.fixture
    def contra_cheque(self):
        from pagamentos.facade import FolhaContraCheque

        folha_contra_cheque = FolhaContraCheque(5, "1969")
        return folha_contra_cheque

    def test_contra_cheque_atributo_ano(self, contra_cheque):
        v_contra_cheque = contra_cheque
        assert v_contra_cheque.ano

    def test_contra_cheque_atributo_mes(self, contra_cheque):
        v_contra_cheque = contra_cheque
        assert v_contra_cheque.mes

    def test_contra_cheque_atributo_funcionarios(self, contra_cheque):
        v_contra_cheque = contra_cheque
        assert v_contra_cheque.funcionarios

    def test_contra_cheque_atributo_paga(self, contra_cheque):
        v_contra_cheque = contra_cheque
        assert v_contra_cheque.paga == False

    def test_contra_cheque_atributo_total(self, contra_cheque):
        v_contra_cheque = contra_cheque
        assert v_contra_cheque.total


class TestFolhaItens:
    @pytest.fixture
    def itens(self):
        from pagamentos.facade import FolhaItens

        folha_contra_cheque_itens = FolhaItens("OSWALDO")
        return folha_contra_cheque_itens

    def test_itens_atributo_descricao(self, itens):
        v_contra_cheque_itens = itens
        assert v_contra_cheque_itens.descricao

    def test_itens_atributo_referencia(self, itens):
        v_contra_cheque_itens = itens
        assert v_contra_cheque_itens.referencia

    def test_itens_atributo_registro(self, itens):
        v_contra_cheque_itens = itens
        assert v_contra_cheque_itens.registro

    def test_itens_atributo_nome(self, itens):
        v_contra_cheque_itens = itens
        assert v_contra_cheque_itens.nome

    def test_itens_atributo_valor(self, itens):
        v_contra_cheque_itens = itens
        assert v_contra_cheque_itens.valor


class TestFolhaFuncionarios:
    @pytest.fixture
    def funcionarios(self):
        from pagamentos.facade import FolhaFuncionarios

        folha_funcionario = FolhaFuncionarios("OSWALDO")
        return folha_funcionario

    def test_funcionario_atributo_admissao(self, funcionarios):
        v_funcionario = funcionarios
        assert v_funcionario.admissao

    def test_funcionario_atributo_cartao_de_ponto(self, funcionarios):
        v_funcionario = funcionarios
        assert v_funcionario.cartao_ponto

    def test_funcionario_atributo_contra_cheque_itens(self, funcionarios):
        v_funcionario = funcionarios
        assert v_funcionario.contra_cheque_itens

    def test_funcionario_atributo_demissao(self, funcionarios):
        v_funcionario = funcionarios
        assert v_funcionario.demissao

    def test_funcionario_atributo_nome(self, funcionarios):
        v_funcionario = funcionarios
        assert v_funcionario.nome

    def test_funcionario_atributo_nome_curto(self, funcionarios):
        v_funcionario = funcionarios
        assert v_funcionario.nome_curto

    def test_funcionario_atributo_pago(self, funcionarios):
        v_funcionario = funcionarios
        assert v_funcionario.pago == False

    def test_funcionario_atributo_salario(self, funcionarios):
        v_funcionario = funcionarios
        assert v_funcionario.salario

    def test_funcionario_atributo_vales(self, funcionarios):
        v_funcionario = funcionarios
        assert v_funcionario.vales

    def test_funcionario_atributo_valor(self, funcionarios):
        v_funcionario = funcionarios
        assert v_funcionario.valor


class TestFolhaVale:
    @pytest.fixture
    def vales(self):
        from pagamentos.facade import FolhaVale

        folha_vale = FolhaVale("OSWALDO")
        return folha_vale

    def test_vale_atributo_data(self, vales):
        v_vales = vales
        assert v_vales.data

    def test_vale_atributo_descricao(self, vales):
        v_vales = vales
        assert v_vales.descricao

    def test_vale_atributo_nome(self, vales):
        v_vales = vales
        assert v_vales.nome

    def test_vale_atributo_valor(self, vales):
        v_vales = vales
        assert v_vales.valor


class TestAdmitido:
    def test_data_admissao_esta_antes_mes_ano_da_folha_pagamento(self):
        from pagamentos.facade import folha_admissao

        admitido = folha_admissao("28-02-2022", "03", "2022")
        assert admitido

    def test_data_admissao_esta_no_mes_ano_da_folha_pagamento(self):
        from pagamentos.facade import folha_admissao

        admitido = folha_admissao("15-03-2022", "03", "2022")
        assert admitido

    def test_data_admissao_esta_depois_mes_ano_da_folha_pagamento(self):
        from pagamentos.facade import folha_admissao

        admitido = folha_admissao("01-04-2022", "03", "2022")
        assert not admitido


class TestDemitido:
    def test_data_demissao_esta_antes_mes_ano_da_folha_pagamento(self):
        from pagamentos.facade import folha_demissao

        demitido = folha_demissao("28-02-2022", "03", "2022")
        assert demitido

    def test_data_demissao_esta_no_mes_ano_da_folha_pagamento(self):
        from pagamentos.facade import folha_demissao

        demitido = folha_demissao("15-03-2022", "03", "2022")
        assert not demitido

    def test_data_demissao_esta_depois_mes_ano_da_folha_pagamento(self):
        from pagamentos.facade import folha_demissao

        demitido = folha_demissao("01-04-2022", "03", "2022")
        assert not demitido
