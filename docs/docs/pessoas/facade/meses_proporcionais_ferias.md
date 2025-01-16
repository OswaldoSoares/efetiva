# `meses_proporcionais_ferias`

Calcula a quantidade de meses proporcionais de férias com base na diferença entre duas datas.

## Lógica do Cálculo

O cálculo é feito com base na diferença de meses e dias entre a data inicial e final.

* Se os dias forem menores que 15, o valor retornado será o número total de meses.
* Se os dias forem maiores ou iguais a 15, um mês adicional será considerado.

## Parâmetros
- `data_inicial` (datetime): A data inicial do período (do tipo `datetime`).
- `data_final` (datetime): A data final do período (do tipo `datetime`).

## Retorno
- (int): Número de meses proporcionais de férias calculados.

## Código da função

```{.py3 linenums="1"}
from dateutil.relativedelta import relativedelta

def meses_proporcionais_ferias(data_inicial, data_final):
    periodo = relativedelta(data_final, data_inicial)
    return periodo.months + (1 if periodo.days >= 15 else 0)
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="10 19"}
from datetime import datetime

data_inicial = datetime(2024, 7, 1)
data_final = datetime(2025, 1, 16)

meses = meses_proporcionais_ferias(data_inicial, data_final)
print(meses)

# Resultado esperado:
7

data_inicial = datetime(2024, 1, 1)
data_final = datetime(2024, 9, 14)

meses = meses_proporcionais_ferias(data_inicial, data_final)
print(meses)

# Resultado esperado:
8
```
