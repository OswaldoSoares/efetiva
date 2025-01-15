# `calcular_dias_ferias_proporcionais`

Calcula os dias proporcionais de férias com base no número de faltas do período aquisitivo e no número de meses trabalhados.

## Lógica do Cálculo

O cálculo é feito com base em faixas predefinidas

* Até 5 faltas: 2.5 dias por dozeavos.
* De 6 a 14 faltas: 2.0 dias por dozeavos.
* De 15 a 23 faltas: 1.5 dias por dozeavos.
* De 24 a 32 faltas: 1.0 dia por dozeavos.
* Acima de 32 faltas: 0 dias (sem direito a férias).

## Parâmetros
- `faltas` (int): Número de faltas no período (deve ser maior ou igual a 0).
- `dozeavos` (int): Número de meses trabalhados no período, em dozeavos (entre 1 e 12).

## Retorno
- (float): Dias proporcionais de férias calculados.

## Código da função

```{.py3 linenums="1"}
def calcular_dias_ferias_proporcionais(faltas, dozeavos):
    faixas = [
        (5, 2.5),   # Até 5 faltas
        (14, 2.0),  # De 6 a 14 faltas
        (23, 1.5),  # De 15 a 23 faltas
        (32, 1.0),  # De 24 a 32 faltas
    ]

    multiplicador = next((valor for limite, valor in faixas if faltas <= limite), 0)

    return multiplicador * dozeavos
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="5 11 17 23"}
dias = calcular_dias_ferias_proporcionais(4, 6)
print(dias)

# Resultado esperado
15.0

dias = calcular_dias_ferias_proporcionais(10, 12)
print(dias)

# Resultado esperado
24.0

dias = calcular_dias_ferias_proporcionais(25, 9)
print(dias)

# Resultado esperado
9.0

dias = calcular_dias_ferias_proporcionais(35, 10)
print(dias)

# Resultado esperado
0
```
