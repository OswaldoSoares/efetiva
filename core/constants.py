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

TIPOS_DOCS = ["RG", "CPF", "HABILITAÇÃO", "RESERVISTA", "PASSAPORTE"]

TIPOS_FONES = ["WHATSAPP", "VIVO", "TIM", "OI", "CLARO", "FIXO", "RECADO"]

TIPOS_CONTAS = ["CORRENTE", "POUPANÇA"]

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
