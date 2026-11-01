"""Km rodados (a partir das minutas) e consumo (km/L) por veículo e mês.

O abastecimento não tem hodômetro: o km de cada veículo no mês é a soma do
percurso das suas minutas (KMFinal - KMInicial). Somar o percurso de cada
minuta, em vez de "maior km - menor km", não é afetado pelos erros de
digitação do km absoluto (dígito a mais, sequências misturadas).

Como nem sempre o tanque é completado, o consumo é calculado por mês:
km rodados no mês / litros abastecidos no mês.
"""

from collections import defaultdict

from minutas.models import Minuta

# Percurso máximo aceito numa minuta; acima disso é erro de digitação
KM_MAXIMO_MINUTA = 1000

# Faixa de consumo plausível; fora dela o valor é marcado para conferência
CONSUMO_MINIMO = 1
CONSUMO_MAXIMO = 25


def km_rodados_por_veiculo_mes(inicio, fim):
    """Retorna {(id_veiculo, mes): {"km": int, "descartadas": int}}.

    `mes` é o primeiro dia do mês. Minutas canceladas são ignoradas e as
    com percurso negativo ou maior que KM_MAXIMO_MINUTA são descartadas.
    """
    resultado = defaultdict(lambda: {"km": 0, "descartadas": 0})
    minutas = (
        Minuta.objects.filter(
            DataMinuta__gte=inicio,
            DataMinuta__lt=fim,
            idVeiculo__isnull=False,
        )
        .exclude(StatusMinuta="CANCELADA")
        .values_list("idVeiculo_id", "DataMinuta", "KMInicial", "KMFinal")
        .order_by()
    )
    for id_veiculo, data, km_inicial, km_final in minutas:
        item = resultado[(id_veiculo, data.replace(day=1))]
        percurso = km_final - km_inicial
        if km_inicial > 0 and 0 <= percurso <= KM_MAXIMO_MINUTA:
            item["km"] += percurso
        else:
            item["descartadas"] += 1
    return resultado


def calcular_consumo(km, litros):
    """Retorna (km/L ou None, fora_da_faixa)."""
    if not km or not litros:
        return None, False
    consumo = km / float(litros)
    return consumo, not CONSUMO_MINIMO <= consumo <= CONSUMO_MAXIMO
