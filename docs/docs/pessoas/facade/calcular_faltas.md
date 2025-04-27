# `calcular_faltas`

Função responsável por calcular o total de faltas de um colaborador e determinar o valor a ser descontado do salário.

## Fluxo de Execução

1. Filtra os registros de cartão de ponto onde há ausência (`Ausencia="FALTA"`).
2. Conta o número de faltas abonadas (`Remunerado=1`).
3. Calcula o número de faltas que devem ser descontadas.
4. Determina o valor total a ser descontado do salário com base nos dias de falta.
5. Retorna a quantidade de faltas a descontar e o valor correspondente.

## Parâmetros

- `salario` (`float`): Salário total do colaborador.
- `cartao_ponto` (`QuerySet`): Conjunto de registros do cartão de ponto do colaborador.

## Retorno

- `tuple`: Retorna uma tupla com dois elementos:
  - `dias_descontar` (`int`): Número de dias de falta que serão descontados.
  - `valor_faltas` (`float`): Valor total das faltas a ser descontado.

## Dependências

- `cartao_ponto.filter(...)`: Filtra os registros do cartão de ponto para identificar faltas.
- `count()`: Obtém a quantidade total de faltas abonadas.

## Código da Função

```{py3 linenums="1"}
def calcular_faltas(salario, cartao_ponto):
    """Calcula o total de faltas e o valor correspondente a ser descontado do salário."""
    dias_faltas = cartao_ponto.filter(Ausencia="FALTA")
    faltas_abonadas = dias_faltas.filter(Remunerado=1).count()

    dias_descontar = len(dias_faltas) - faltas_abonadas

    valor_faltas = salario / 30 * dias_descontar

    return dias_descontar, valor_faltas
```

## Exemplo de Uso

```{py3 linenums="1"}
# Suponha que temos um conjunto de registros de cartão de ponto
dias_faltas, valor = calcular_faltas(5000.00, cartao_ponto)

# Exibe os valores calculados
print(f"Faltas descontadas: {dias_faltas}")
print(f"Valor descontado: R${valor:.2f}")
```
