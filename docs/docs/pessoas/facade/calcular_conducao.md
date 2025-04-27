# `calcular_conducao`

Função responsável por calcular o valor total de condução a ser pago a um colaborador com base nos dias em que utilizou transporte público.

## Fluxo de Execução

1. Filtra os registros do cartão de ponto onde `Conducao=1` e `CarroEmpresa=0`.
2. Conta o número de dias em que o colaborador utilizou transporte público.
3. Multiplica o número de dias pela tarifa diária.
4. Retorna o número de dias contabilizados e o valor total calculado.

## Parâmetros

- `tarifa_dia` (`float`): Valor da tarifa diária de transporte.
- `cartao_ponto` (`QuerySet`): Conjunto de registros do cartão de ponto do colaborador.

## Retorno

- `tuple`: Retorna uma tupla com dois elementos:
  - `dias_conducao` (`int`): Número de dias em que houve uso de transporte público.
  - `valor_conducao` (`float`): Valor total da condução calculado.

## Dependências

- `cartao_ponto.filter(...)`: Filtra os registros do cartão de ponto.
- `count()`: Obtém a quantidade total de registros filtrados.

## Código da Função

```{py3 linenums="1"}
def calcular_conducao(tarifa_dia, cartao_ponto):
    """Calcula o custo de condução com base nos dias registrados no cartão de ponto."""
    dias_conducao = cartao_ponto.filter(Conducao=1, CarroEmpresa=0).count()
    valor_conducao = dias_conducao * tarifa_dia

    return dias_conducao, valor_conducao
```

## Exemplo de Uso

```{py3 linenums="1"}
# Suponha que temos um conjunto de registros de cartão de ponto
dias, valor = calcular_conducao(5.00, cartao_ponto)

# Exibe os valores calculados
print(f"Dias de condução: {dias}")
print(f"Valor total: R${valor:.2f}")
```
