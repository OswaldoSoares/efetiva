
# `calcular_salario`

Função responsável por calcular o salário proporcional de um colaborador com base nos dias trabalhados e em ajustes de meses com menos de 30 dias.

## Fluxo de Execução

1. Obtém o último dia registrado no cartão de ponto.
2. Conta os dias trabalhados, excluindo ausências por férias.
3. Ajusta a contagem de dias para evitar valores acima de 30.
4. Aplica um incremento caso o último dia do mês seja 28 ou 29.
5. Calcula o valor proporcional do salário com base nos dias ajustados.
6. Retorna a quantidade de dias pagos e o valor calculado.

## Parâmetros

- `salario` (`float`): Salário total do colaborador.
- `cartao_ponto` (`QuerySet`): Conjunto de registros do cartão de ponto do colaborador.

## Retorno

- `tuple`: Retorna uma tupla com dois elementos:
  - `dias_pagar` (`int`): Número de dias a serem pagos.
  - `valor_pagar` (`float`): Valor total a ser pago com base nos dias trabalhados.

## Dependências

- `cartao_ponto.order_by("Dia").last()`: Obtém o último dia registrado no cartão de ponto.
- `cartao_ponto.exclude(Ausencia__icontains="FÉRIAS")`: Filtra apenas os dias sem ausência por férias.
- `incrementos.get(ultimo_dia, 0)`: Aplica um ajuste nos meses menores.

## Código da Função

```{py3 linenums="1"}
def calcular_salario(salario, cartao_ponto):
    ultimo_dia = cartao_ponto.order_by("Dia").last().Dia.day

    dias_pagar = cartao_ponto.exclude(Ausencia__icontains="FÉRIAS").count()
    dias_pagar = 30 if dias_pagar == 31 else dias_pagar

    incrementos = {28: 2, 29: 1}
    dias_pagar += incrementos.get(ultimo_dia, 0)

    valor_pagar = salario / 30 * dias_pagar

    return dias_pagar, valor_pagar
```

## Exemplo de Uso

```{py3 linenums="1"}
# Suponha que temos um conjunto de registros de cartão de ponto
dias, valor = calcular_salario(3000.00, cartao_ponto)

# Exibe os valores calculados
print(f"Dias pagos: {dias}")
print(f"Valor a pagar: R${valor:.2f}")
```
