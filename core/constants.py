"""
constants.py

Este módulo contém todas as constantes e variáveis imutáveis usadas em
todo o projeto.

As constantes definidas aqui incluem:
- Configurações de cálculos, como tipos de formas de cálculo e itens de
operação.

Estas constantes são utilizadas em várias partes do código para garantir
consistência e facilitar a manutenção.
Modificações nesses valores devem ser feitas com cuidado, garantindo que
a integridade das operações do projeto seja mantida.

Exemplo de uso:
    from .constants import TIPOS_FORMAS_CALCULO
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Evento:
    codigo: str
    descricao: str
    computavel: bool
    credito: bool


# Tupla de eventos
EVENTOS_CONTRA_CHEQUE = (
    Evento("1000", "SALÁRIO", True, True),
    Evento("1002", "DSR SOBRE HORAS EXTRAS", True, True),
    Evento("1003", "HORAS EXTRAS", True, True),
    Evento("1019", "1/3 FÉRIAS", True, True),
    Evento("1020", "FÉRIAS", True, True),
    Evento("1211", "GRATIFICAÇÕES", True, True),
    Evento("1410", "VALE TRANSPORTE", True, True),
    Evento("5001", "13º SALÁRIO", True, True),
    Evento("5501", "ADIANTAMENTO DE SALÁRIO", True, True),
    Evento("5504", "13º SALÁRIO - ADIANTAMENTO", True, True),
    Evento("6000", "SALDO DE SALÁRIO", True, True),
    Evento("6002", "13º SALÁRIO PROPORCIONAL", True, True),
    Evento("6006", "FÉRIAS PROPORCIONAIS", True, True),
    Evento("6007", "FÉRIAS VENCIDAS", True, True),
    Evento("6901", "DESCONTO DO AVISO PRÉVIO", True, False),
    Evento("9200", "DESCONTO DE ADIANTAMENTOS", True, False),
    Evento("9201", "INSS", True, False),
    Evento("9207", "FALTAS", True, False),
    Evento("9208", "ATRASOS", True, False),
    Evento("9211", "DSR SOBRE FALTAS", True, False),
    Evento("9212", "DSR SOBRE ATRAZOS", True, False),
    Evento("9214", "13º SALÁRIO - DESCONTO DE ADIANTAMENTO", True, False),
    Evento("9216", "DESCONTO DE VALE TRANSPORTE", True, False),
    Evento("9801", "VALE", False, False),
    Evento("9802", "MULTA", False, False),
    Evento("9908", "FGTS", True, True),
)

EVENTOS_INCIDE_INSS = (
    "1000",
    "1002",
    "1003",
    "1019",
    "1020",
    "1211",
    "2001",
    "6002",
    "9207",
    "9208",
    "9211",
)

EVENTOS_INCIDE_FGTS = (
    "1000",
    "1002",
    "1003",
    "1019",
    "1020",
    "1211",
    "2001",
    "6002",
    "9207",
    "9208",
    "9211",
)

EVENTOS_INCIDE_IRRF = (
    "1000",
    "1002",
    "1003",
    "1019",
    "1020",
    "1211",
    "2001",
    "6002",
    "9207",
    "9208",
    "9211",
)



MESES = {
    1: "JANEIRO",
    2: "FEVEREIRO",
    3: "MARÇO",
    4: "ABRIL",
    5: "MAIO",
    6: "JUNHO",
    7: "JULHO",
    8: "AGOSTO",
    9: "SETEMBRO",
    10: "OUTUBRO",
    11: "NOVEMBRO",
    12: "DEZEMBRO",
}

# Constants Módulo Pessoal
CATEGORIAS = [
    "AGREGADO",
    "AJUDANTE",
    "FUNCIONÁRIO",
    "MOTORISTA",
    "PROPRIETÁRIO",
]

TIPOPGTO = ["MENSALISTA", "MINUTA", "NENHUM", "SAIDA"]

TIPOS_DOCS = ["CNH", "CPF", "CTPS", "RESERVISTA", "RG", "TITULO ELEITOR"]

TIPOS_FONES = ["WHATSAPP", "VIVO", "TIM", "OI", "CLARO", "FIXO", "RECADO"]

TIPOS_CONTAS = ["CORRENTE", "POUPANÇA"]

MOTIVOS_DEMISSAO = [
    ("comum_acordo", "DEMISSAO DE COMUM ACORDO"),
    ("sem_justa_causa", "DISPENSA SEM JUSTA CAUSA"),
    ("com_justa_causa", "DISPENSA COM JUSTA CAUSA"),
    ("pedido_demissao", "PEDIDO DE DEMISSÃO"),
    ("experiencia_no_prazo", "ENCERRAMENTO EXPERIÊNCIA NO PRAZO"),
    ("experiencia_fora_prazo", "ENCERRAMENTO EXPERIÊNCIA ANTES DO PRAZO"),
    ("aposentadoria", "APOSENTADORIA DO COLABORADOR"),
]

AVISO_PREVIO = [
    ("trabalhado", "TRABALHADO"),
    ("indenizado", "INDENIZADO PELO EMPREGADOR"),
    ("nao_comprido", "NÃO COMPRIDO PELO COLABORADOR"),
    ("dispensado", "DISPENSADO"),
]

EVENTOS_RESCISORIOS = [
    ("saldo_salario", "SALDO SALARIO"),
    ("ferias_vencidas", "FÉRIAS VENCIDAS"),
    ("ferias_proporcionais", "FÉRIAS PROPORCIONAIS"),
    ("decimo_terceiro_proporcional", "13º PROPORCIONAL"),
    ("fgts", "FGTS"),
]

# Tipos de contracheque
TIPO_CONTRA_CHEQUE_RESCISAO = "RESCISÃO"
TIPO_CONTRA_CHEQUE_PAGAMENTO = "PAGAMENTO"

# Campos do modelo ContraChequeItens
CAMPO_CODIGO_CONTRA_CHEQUE_ITEM = "Codigo"

# Descrições de itens
DESCRICAO_SALARIO = "SALÁRIO"

# Códigos
CODIGO_SALARIO = "6000"

# Constants Módulo Minutas
SETUP_CALCULO_MINUTA = {
    "taxa_expedicao": {
        "descricao": "TAXA DE EXPEDIÇÃO",
        "forma_calculo": "R$_UN",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "text",
        "field_tabela": "base",
        "field_minuta": "quantidade",
        "field_total": "valor",
        "indice": 1,
    },
    "seguro": {
        "descricao": "SEGURO",
        "forma_calculo": "%_R$",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "text",
        "field_tabela": "porcento",
        "field_minuta": "base",
        "field_total": "valor",
        "indice": 2,
    },
    "porcentagem_nota": {
        "descricao": "PORCENTAGEM NOTA",
        "forma_calculo": "%_R$",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "text",
        "field_tabela": "porcento",
        "field_minuta": "base",
        "field_total": "valor",
        "indice": 3,
    },
    "porcentagem_nota_extra": {
        "descricao": "PORCENTAGEM NOTA HORA EXTRA",
        "forma_calculo": "%_HS",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "time",
        "field_tabela": "porcento",
        "field_minuta": "tempo",
        "field_total": "valor",
        "indice": 4,
    },
    "hora": {
        "descricao": "HORAS",
        "forma_calculo": "R$_HS",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "time",
        "field_tabela": "base",
        "field_minuta": "tempo",
        "field_total": "valor",
        "indice": 5,
    },
    "hora_extra": {
        "descricao": "HORAS EXCEDENTE",
        "forma_calculo": "%_HS",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "time",
        "field_tabela": "porcento",
        "field_minuta": "tempo",
        "field_total": "valor",
        "indice": 6,
    },
    "quilometragem": {
        "descricao": "QUILOMETRAGEM",
        "forma_calculo": "R$_UN",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "text",
        "field_tabela": "base",
        "field_minuta": "quantidade",
        "field_total": "valor",
        "indice": 7,
    },
    "quilometragem_extra": {
        "descricao": "QUILOMETRAGEM HORA EXTRA",
        "forma_calculo": "%_HS",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "time",
        "field_tabela": "porcento",
        "field_minuta": "tempo",
        "field_total": "valor",
        "indice": 8,
    },
    "entregas": {
        "descricao": "ENTREGAS",
        "forma_calculo": "R$_UN",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "text",
        "field_tabela": "base",
        "field_minuta": "quantidade",
        "field_total": "valor",
        "indice": 9,
    },
    "entregas_extra": {
        "descricao": "ENTREGAS HORA EXTRA",
        "forma_calculo": "%_HS",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "time",
        "field_tabela": "porcento",
        "field_minuta": "tempo",
        "field_total": "valor",
        "indice": 10,
    },
    "saida": {
        "descricao": "SAIDA",
        "forma_calculo": "R$_UN",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "text",
        "field_tabela": "base",
        "field_minuta": "quantidade",
        "field_total": "valor",
        "indice": 15,
    },
    "saida_extra": {
        "descricao": "SAIDA HORA EXTRA",
        "forma_calculo": "%_HS",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "time",
        "field_tabela": "porcento",
        "field_minuta": "tempo",
        "field_total": "valor",
        "indice": 16,
    },
    "capacidade_peso": {
        "descricao": "CAPACIDADE PESO",
        "forma_calculo": "R$_UN",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "text",
        "field_tabela": "base",
        "field_minuta": "quantidade",
        "field_total": "valor",
        "indice": 17,
    },
    "capacidade_peso_extra": {
        "descricao": "CAPACIDADE PESO HORA EXTRA",
        "forma_calculo": "%_HS",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "time",
        "field_tabela": "porcento",
        "field_minuta": "tempo",
        "field_total": "valor",
        "indice": 18,
    },
    "entregas_quilos": {
        "descricao": "ENTREGAS QUILOS",
        "forma_calculo": "R$_KG",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "text",
        "field_tabela": "base",
        "field_minuta": "peso",
        "field_total": "valor",
        "indice": 11,
    },
    "entregas_quilos_extra": {
        "descricao": "ENTREGAS QUILOS HORA EXTRA",
        "forma_calculo": "%_HS",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "time",
        "field_tabela": "porcento",
        "field_minuta": "tempo",
        "field_total": "valor",
        "indice": 12,
    },
    "entregas_volume": {
        "descricao": "ENTREGAS VOLUME",
        "forma_calculo": "R$_UN",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "text",
        "field_tabela": "base",
        "field_minuta": "quantidade",
        "field_total": "valor",
        "indice": 13,
    },
    "entregas_volume_extra": {
        "descricao": "ENTREGAS VOLUME HORA EXTRA",
        "forma_calculo": "%_HS",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "time",
        "field_tabela": "porcento",
        "field_minuta": "tempo",
        "field_total": "valor",
        "indice": 14,
    },
    "perimetro": {
        "descricao": "PERIMETRO",
        "forma_calculo": "%_R$",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "text",
        "field_tabela": "porcento",
        "field_minuta": "base",
        "field_total": "valor",
        "indice": 19,
    },
    "perimetro_extra": {
        "descricao": "PERIMETRO HORA EXTRA",
        "forma_calculo": "%_HS",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "time",
        "field_tabela": "porcento",
        "field_minuta": "tempo",
        "field_total": "valor",
        "indice": 20,
    },
    "pernoite": {
        "descricao": "PERNOITE",
        "forma_calculo": "%_R$",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "text",
        "field_tabela": "porcento",
        "field_minuta": "base",
        "field_total": "valor",
        "indice": 21,
    },
    "ajudante": {
        "descricao": "AJUDANTE",
        "forma_calculo": "R$_UN",
        "tabela": 0.00,
        "minuta": 0,
        "ativo": False,
        "input_type": "text",
        "field_tabela": "base",
        "field_minuta": "quantidade",
        "field_total": "valor",
        "indice": 22,
    },
}


TIPOS_CALCULO = [
    "porcentagem_nota",
    "hora",
    "quilometragem",
    "entregas",
    "saida",
    "capacidade_peso",
    "entregas_quilos",
    "entregas_volume",
]


FUNCOES_CALCULO = {
    "R$_UN": {
        "funcao": "calcular_valor_por_unidade",
        "parametros_comuns": ["tabela", "minuta"],
    },
    "%_R$": {
        "funcao": "calcular_percentual_valor",
        "parametros_comuns": ["tabela", "minuta"],
    },
    "R$_HS": {
        "funcao": "calcular_valor_por_tempo",
        "parametros_comuns": ["tabela", "minuta"],
    },
    "%_HS": {
        "funcao": "calcular_percentual_horas",
        "parametros_comuns": ["tabela", "minuta"],
        "parametros_extras": ["valor_base"],
    },
    "R$_KG": {
        "funcao": "calcular_valor_por_quilos",
        "parametros_comuns": ["tabela", "minuta"],
    },
}

TIPOS_DOCUMENTO_PARA_ARQUIVAR = TIPOS_DOCS + [
    "ATESTADO MÉDICO",
    "COMPROVANTE DE ENDEREÇO",
    "CONTRATO DE TRABALHO",
    "EXAME ADMISSIONAL",
    "RESCISÃO",
]
