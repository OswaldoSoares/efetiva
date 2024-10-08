"""
Módulo para gerenciamento de informações de colaboradores, incluindo
documentos, telefones, contas bancárias e dados salariais.
"""

import datetime
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from core.tools import nome_curto
from .models import (
    Pessoal,
    DocPessoal,
    FonePessoal,
    ContaPessoal,
    Salario,
    CartaoPonto,
    Aquisitivo,
    Ferias,
    DecimoTerceiro,
    ParcelasDecimoTerceiro,
)


class Colaborador:
    # pylint: disable=too-many-instance-attributes
    """
    Classe que representa um colaborador e suas informações.

    Esta classe fornece acesso aos dados pessoais, documentos, telefones,
    contas bancárias, informações salariais e outros detalhes relevantes
    sobre um colaborador.

    Attributes:
        id_pessoal (int): ID do colaborador.
        nome (str): Nome completo do colaborador.
        nome_curto (str): Nome abreviado do colaborador.
        endereco (str): Endereço do colaborador.
        bairro (str): Bairro do colaborador.
        cep (str): CEP do colaborador.
        cidade (str): Cidade do colaborador.
        estado (str): Estado do colaborador.
        data_nascimento (datetime): Data de nascimento do colaborador.
        mae (str): Nome da mãe do colaborador.
        pai (str): Nome do pai do colaborador.
        categoria (str): Categoria do colaborador.
        tipo_pgto (str): Tipo de pagamento do colaborador.
        status_pessoal (str): Status do colaborador.
        data_admissao (datetime): Data de admissão do colaborador.
        data_demissao (datetime): Data de demissão do colaborador, se
                                  aplicável.
        documentos (ColaboradorDocumentos): Instância da classe que gerencia
                                            os documentos.
        telefones (ColaboradorTelefones): Instância da classe que gerencia
                                          os telefones.
        bancos (ColaboradorBancos): Instância da classe que gerencia as
                                    contas bancárias.
        salario (Decimal): Salário do colaborador.
        decimo_terceiro (list): Informações sobre o décimo terceiro
                                salário do colaborador.
        ferias (list): Informações sobre as férias do colaborador.
        aquisitivo (list): Informações sobre os períodos aquisitivos do
                           colaborador.
        faltas (list): Faltas registradas durante o período aquisitivo.
        salario_ferias (Decimal): Salário calculado para as férias do
                                  colaborador.
    """

    def __init__(self, id_pessoal):
        """
        Inicializa a classe Colaborador com as informações do colaborador.

        Args:
            id_pessoal (int): O ID do colaborador para buscar informações.
        """
        colaborador = Pessoal.objects.get(idPessoal=id_pessoal)
        self.id_pessoal = colaborador.idPessoal
        self.nome = colaborador.Nome
        self.nome_curto = nome_curto(colaborador.Nome)
        self.endereco = colaborador.Endereco or ""
        self.bairro = colaborador.Bairro or ""
        self.cep = colaborador.CEP or ""
        self.cidade = colaborador.Cidade or ""
        self.estado = colaborador.Estado or ""
        self.data_nascimento = colaborador.DataNascimento
        self.mae = colaborador.Mae
        self.pai = colaborador.Pai
        self.categoria = colaborador.Categoria
        self.tipo_pgto = colaborador.TipoPgto
        self.status_pessoal = colaborador.StatusPessoal
        self.data_admissao = colaborador.DataAdmissao
        self.data_completa_ano = self.data_admissao + relativedelta(
            years=+1, days=-1
        )
        self.data_demissao = colaborador.DataDemissao
        self.foto = colaborador.Foto
        self.documentos = ColaboradorDocumentos(id_pessoal)
        self.telefones = ColaboradorTelefones(id_pessoal)
        self.bancos = ColaboradorBancos(id_pessoal)
        self.salario = ColaboradorSalario(id_pessoal).salario
        self.decimo_terceiro = self._get_decimo_terceiro()
        self.ferias = self._get_ferias()
        self.aquisitivo = self._get_aquisitivo()
        self.faltas = self._get_faltas_aquisitivo()
        self.salario_ferias = self._get_salario_ferias()

    @property
    def endereco_completo(self) -> str:
        """
        Retorna o endereço completo do colaborador.

        Returns:
            str: Endereço completo do colaborador, incluindo bairro.
        """
        parts = [self.endereco, self.bairro]
        return " - ".join([p for p in parts if p])

    @property
    def cidade_estado(self) -> str:
        """
        Retorna a cidade e estado do colaborador, incluindo o CEP.

        Returns:
            str: Cidade e estado do colaborador, incluindo CEP se disponível.
        """
        parts = [self.cidade, self.estado]
        cidade_estado = " - ".join([p for p in parts if p])
        if self.cep:
            cidade_estado += (
                f" - CEP: {self.cep}" if cidade_estado else f"CEP: {self.cep}"
            )
        return cidade_estado

    def _get_decimo_terceiro(self) -> list:
        """
        Obtém informações sobre o décimo terceiro salário do colaborador.

        Returns:
            list: Lista de dicionários com informações sobre o décimo terceiro
                  salário.
        """
        if self.tipo_pgto == "MENSALISTA":
            hoje = datetime.datetime.today()
            decimos = DecimoTerceiro.objects.filter(
                idPessoal=self.id_pessoal, Ano=hoje.year
            )
            return [
                {
                    "id_decimo_terceiro": item.idDecimoTerceiro,
                    "ano": item.Ano,
                    "dozeavos": item.Dozeavos,
                    "valor_base": item.ValorBase,
                    "valor": item.Valor,
                    "pago": item.Pago,
                    "parcelas": ParcelasDecimoTerceiro.objects.filter(
                        idDecimoTerceiro=decimos[0].idDecimoTerceiro
                    ),
                }
                for item in decimos
            ]
        return []

    def _get_ferias(self):
        """
        Obtém informações sobre as férias do colaborador.

        Returns:
            list: Lista de dicionários com informações sobre as férias.
        """
        if self.tipo_pgto == "MENSALISTA":
            ferias = Ferias.objects.filter(idPessoal=self.id_pessoal)
            return [
                {
                    "data_inicial": item.DataInicial,
                    "data_final": item.DataFinal,
                    "id_ferias": item.idFerias,
                    "idaquisitivo": item.idAquisitivo_id,
                    "dias": (item.DataFinal - item.DataInicial).days + 1,
                }
                for item in ferias
            ]
        return []

    def _get_aquisitivo(self) -> list:
        """
        Obtém os períodos aquisitivos do colaborador.

        Returns:
            list: Lista de dicionários com informações sobre os períodos
                  aquisitivos.
        """
        aquisitivos = Aquisitivo.objects.filter(
            idPessoal=self.id_pessoal
        ).order_by("-DataInicial")
        if self.tipo_pgto == "MENSALISTA" and not self.data_demissao:
            if (
                not aquisitivos
                or aquisitivos[0].DataFinal < datetime.datetime.today().date()
            ):
                aquisitivo_inicial = self.data_admissao + relativedelta(
                    years=len(aquisitivos)
                )
                aquisitivo_final = aquisitivo_inicial + relativedelta(
                    years=1, days=-1
                )
                Aquisitivo.objects.create(
                    DataInicial=aquisitivo_inicial,
                    DataFinal=aquisitivo_final,
                    idPessoal=self.id_pessoal,
                )
            aquisitivos = Aquisitivo.objects.filter(
                idPessoal=self.id_pessoal
            ).order_by("-DataInicial")
        return [
            {
                "aquisitivo_inicial": item.DataInicial,
                "aquisitivo_final": item.DataFinal,
                "idaquisitivo": item.idAquisitivo,
            }
            for item in aquisitivos
        ]

    def _get_faltas_aquisitivo(self):
        """
        Obtém as faltas registradas no período aquisitivo do colaborador.

        Returns:
            list: Lista de datas das faltas no formato "dd/mm/yyyy".
        """
        if self.tipo_pgto == "MENSALISTA":
            aquisitivo = self.aquisitivo[0]
            cartao_ponto = CartaoPonto.objects.filter(
                idPessoal=self.id_pessoal,
                Dia__range=[
                    aquisitivo["aquisitivo_inicial"],
                    aquisitivo["aquisitivo_final"],
                ],
                Ausencia="FALTA",
                Remunerado=False,
            )
            return [item.Dia.strftime("%d/%m/%Y") for item in cartao_ponto]
        return []

    def _get_salario_ferias(self):
        """
        Calcula o salário do colaborador durante as férias,
        considerando as faltas.

        Returns:
            Decimal: Salário calculado para as férias.
        """
        salario = Decimal(self.salario[0]["salario"])
        salario_dia = salario / 30
        faltas = len(self.faltas)
        if faltas < 6:
            return salario
        if faltas < 15:
            return round(salario_dia * 24, 2)
        if faltas < 24:
            return round(salario_dia * 18, 2)
        if faltas < 33:
            return round(salario_dia * 12, 2)
        return Decimal(0)


class ColaboradorDocumentos:
    """
    Classe para gerenciar documentos pessoais de um colaborador.

    Attributes:
        id_pessoal (int): ID do colaborador.
        documentos (list): Lista de documentos do colaborador.
    """

    def __init__(self, id_pessoal):
        """
        Inicializa a classe ColaboradorDocumentos.

        Args:
            id_pessoal (int): O ID do colaborador para buscar documentos.
        """
        self.docs = self._get_docpessoal(id_pessoal)

    def _get_docpessoal(self, id_pessoal):
        """
        Obtém os documentos pessoais do colaborador.

        Args:
            id_pessoal (int): O ID do colaborador para buscar documentos.

        Returns:
            list: Lista de dicionários com informações sobre os documentos,
                  onde cada dicionário contém:
                  - "iddoc": ID do documento pessoal.
                  - "tipo": Tipo do documento.
                  - "documento": Número do documento.
                  - "data_doc": Data de emissão do documento.
        """
        documentos = DocPessoal.objects.filter(idPessoal=id_pessoal)
        return [
            {
                "iddoc": item.idDocPessoal,
                "tipo": item.TipoDocumento,
                "documento": item.Documento,
                "data_doc": item.Data,
            }
            for item in documentos
        ]

    def count_documentos(self) -> int:
        """
        Conta o número de documentos pessoais do colaborador.

        Returns:
            int: Número total de documentos pessoais.
        """
        return len(self.docs)

    def display_documentos_info(self) -> list:
        """
        Gera uma lista formatada com as informações dos documentos.

        Returns:
            list: Lista de dicionários formatados com informações sobre cada
                  documento, contendo uma string com o formato:
                  "Documento: [tipo] - Número: [documento] -
                   Data Documento: [data_doc]".
        """
        return [
            {
                "display": f"Documento: {doc['tipo']} - "
                f"Número: {doc['documento']} - "
                f"Data Documento: {doc['data_doc'].strftime('%d/%m/%Y')}"
            }
            for doc in self.docs
        ]


class ColaboradorTelefones:
    """
    Classe para gerenciar os telefones de um colaborador.

    Attributes:
        id_pessoal (int): ID do colaborador.
        telefones (list): Lista de telefones do colaborador.
    """

    def __init__(self, id_pessoal):
        """
        Inicializa a classe ColaboradorTelefones.

        Args:
            id_pessoal (int): O ID do colaborador para buscar telefones.
        """
        self.fones = self._get_telefones(id_pessoal)

    def _get_telefones(self, id_pessoal):
        """
        Obtém os telefones do colaborador.

        Args:
            id_pessoal (int): O ID do colaborador para buscar telefones.

        Returns:
            list: Lista de dicionários com informações sobre os telefones,
                  onde cada dicionário contém:
                  - "idfone": ID do telefone.
                  - "tipo": Tipo do telefone.
                  - "fone": Número do telefone.
                  - "contato": Nome do contato associado ao telefone.
        """
        telefones = FonePessoal.objects.filter(idPessoal=id_pessoal)
        return [
            {
                "idfone": item.idFonePessoal,
                "tipo": item.TipoFone,
                "fone": item.Fone,
                "contato": item.Contato,
            }
            for item in telefones
        ]

    def count_telefones(self) -> int:
        """
        Conta o número de telefones do colaborador.

        Returns:
            int: Número total de telefones.
        """
        return len(self.fones)

    def display_telefones_info(self) -> list:
        """
        Gera uma lista formatada com as informações dos telefones.

        Returns:
            list: Lista de dicionários formatados com informações sobre cada
                  telefone, contendo uma string com o formato:
                  "Telefone: [tipo] - Número: [fone] - Contato: [contato]".
        """
        return [
            {
                f"Telefone: {fone['tipo']} - Número: {fone['fone']} - "
                f"Contato: {fone['contato']}"
            }
            for fone in self.fones
        ]


class ColaboradorBancos:
    """
    Classe para gerenciar as contas bancárias de um colaborador.

    Attributes:
        id_pessoal (int): ID do colaborador.
        bancos (list): Lista de contas bancárias do colaborador.
    """

    def __init__(self, id_pessoal):
        """
        Inicializa a classe ColaboradorBancos.

        Args:
            id_pessoal (int): O ID do colaborador para buscar contas
                              bancárias.
        """
        self.contas = self._get_bancos(id_pessoal)

    def _get_bancos(self, id_pessoal):
        """
        Obtém as contas bancárias do colaborador.

        Args:
            id_pessoal (int): O ID do colaborador para buscar contas
                              bancárias.

        Returns:
            list: Lista de dicionários com informações sobre as contas
                  bancárias, onde cada dicionário contém:
                  - "idconta": ID da conta bancária.
                  - "banco": Nome do banco.
                  - "agencia": Número da agência.
                  - "conta": Número da conta.
                  - "tipo": Tipo da conta (corrente, poupança, etc.).
                  - "titular": Nome do titular da conta.
                  - "documento": Documento do titular.
                  - "pix": Chave PIX associada à conta.
        """
        bancos = ContaPessoal.objects.filter(idPessoal=id_pessoal)
        return [
            {
                "idconta": item.idContaPessoal,
                "banco": item.Banco,
                "agencia": item.Agencia,
                "conta": item.Conta,
                "tipo": item.TipoConta,
                "titular": item.Titular,
                "documento": item.Documento,
                "pix": item.PIX,
            }
            for item in bancos
        ]

    def count_contas(self) -> int:
        """
        Conta o número de contas bancárias do colaborador.

        Returns:
            int: Número total de contas bancárias.
        """
        return len(self.contas)

    def display_contas_info(self) -> list:
        """
        Gera uma lista formatada com as informações das contas bancárias.

        Returns:
            list: Lista de dicionários formatados com informações sobre cada
                  conta bancária, contendo uma string com o formato:
                  "Banco: [banco] - Agência: [agencia] - Conta: [conta] -
                   Tipo: [tipo]".
        """
        return [
            {
                f"Banco: {conta['banco']} - Agência: {conta['agencia']} - "
                f"Conta: {conta['conta']} - Tipo: {conta['tipo']}"
            }
            for conta in self.contas
        ]

    def display_titular_contas_info(self) -> list:
        """
        Gera uma lista formatada com informações sobre os titulares das
        contas bancárias.

        Returns:
            list: Lista de dicionários formatados com informações sobre cada
                  titular, contendo uma string com o formato:
                  "Nome: [titular] - Documento: [documento]".
        """
        return [
            {f"Nome: {conta['titular']} -  Documento: {conta['documento']}"}
            for conta in self.contas
        ]


class ColaboradorSalario:
    """
    Classe para gerenciar as informações salariais de um colaborador.

    Attributes:
        salario (list): Lista de dicionários contendo informações salariais
                        e de vale transporte do colaborador.
    """

    def __init__(self, id_pessoal):
        """
        Inicializa a classe ColaboradorSalario.

        Args:
            id_pessoal (int): O ID do colaborador para buscar informações
                              salariais.
        """
        self.salario = self._get_salario(id_pessoal)

    def _get_salario(self, id_pessoal):
        """
        Obtém o salário e valor do vale transporte do colaborador.

        Args:
            id_pessoal (int): O ID do colaborador para buscar informações
                              salariais.

        Returns:
            list: Lista de dicionários com informações sobre salário e vale
                  transporte, onde cada dicionário contém:
                  - "idsalario": ID do registro salarial.
                  - "salario": Salário mensal do colaborador.
                  - "transporte": Valor do vale transporte do colaborador.
        """

        valores = Salario.objects.filter(idPessoal=id_pessoal)
        return [
            {
                "idsalario": item.idSalario,
                "salario": item.Salario,
                "transporte": item.ValeTransporte,
            }
            for item in valores
        ]

    def valor_salario_dia(self) -> Decimal:
        """
        Calcula o valor do salário diário do colaborador.

        Returns:
            Decimal: Valor do salário diário, arredondado para duas
                     casas decimais.
        """
        return round(self.salario[0]["salario"] / 30, 2)

    def valor_salario_hora(self) -> Decimal:
        """
        Calcula o valor do salário por hora do colaborador.

        Returns:
            Decimal: Valor do salário por hora, arredondado para duas
                     casas decimais.
        """
        return round((self.salario[0]["salario"] / 30) / 8, 2)
