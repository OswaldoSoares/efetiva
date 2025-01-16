# `meses_proporcionais_decimo_terceiro`

Calcula a quantidade de meses proporcionais para o pagamento de décimo terceiro salário com base na diferença entre duas datas.

## Lógica do Cálculo

O cálculo é feito considerando as seguintes regras:

* Se o dia da data inicial for maior ou igual a 16, a contagem inicia no mês seguinte.
* Se o dia da data final for menor ou igual a 14, a contagem encerra no mês anterior.
* A quantidade de meses é calculada como a diferença entre os meses ajustados mais um mês.

## Parâmetros
- `data_inicial` (datetime): A data inicial do período (do tipo `datetime`).
- `data_final` (datetime): A data final do período (do tipo `datetime`).

## Retorno
- (int): Número de meses proporcionais calculados para o décimo terceiro salário.

## Código da função

```{.py3 linenums="1"}
def meses_proporcionais_decimo_terceiro(data_inicial, data_final):
    inicio_contagem = data_inicial.month + (1 if data_inicial.day >= 16 else 0)
    fim_contagem = data_final.month - (1 if data_final.day <= 14 else 0)

    return fim_contagem - inicio_contagem + 1
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="10 20"}
from datetime import datetime

data_inicial = datetime(2023, 1, 16)
data_final = datetime(2023, 12, 14)

meses = meses_proporcionais_decimo_terceiro(data_inicial, data_final)
print(meses)

# Resultado esperado:
10

# Outro exemplo
data_inicial = datetime(2023, 1, 1)
data_final = datetime(2023, 12, 31)

meses = meses_proporcionais_decimo_terceiro(data_inicial, data_final)
print(meses)

# Resultado esperado:
12
```

