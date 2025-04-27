# `calcular_horas_extras`

Função responsável por calcular o total de horas extras realizadas por um colaborador, considerando a entrada antecipada e saída tardia em relação ao horário padrão.

## Fluxo de Execução

1. Define os horários padrão de entrada (`07:00`) e saída (`17:00`).
2. Inicializa a variável `total_extras` para armazenar o tempo extra acumulado.
3. Percorre os registros do cartão de ponto e calcula o tempo adicional nos casos de:
   - Entrada antes do horário padrão.
   - Saída após o horário padrão.
4. Aplica a regra de cálculo de horas extras com alteração a partir de `01/12/2024`:
   - Se a data do primeiro registro for posterior a `30/11/2024`, usa um fator de `220` horas mensais.
   - Caso contrário, usa um fator baseado em `30` dias e jornada diária de `9` horas.
5. Retorna a quantidade total de horas extras e o valor calculado.

## Parâmetros

- `salario` (`float`): Salário total do colaborador.
- `cartao_ponto` (`list`): Lista de registros do cartão de ponto do colaborador.

## Retorno

- `tuple`: Retorna uma tupla com dois elementos:
  - `total_extras` (`timedelta`): Tempo total de horas extras acumuladas.
  - `valor_extras` (`float`): Valor financeiro correspondente às horas extras.

## Dependências

- `datetime.strptime(...)`: Conversão de strings para objetos de tempo.
- `datetime.combine(...)`: Operação para calcular diferenças entre horários.
- `timedelta()`: Tipo utilizado para representar intervalos de tempo.

## Código da Função

```{py3 linenums="1"}
def calcular_horas_extras(salario, cartao_ponto):
    """Calcula o total de horas extras e o valor correspondente baseado no salário."""
    horario_padrao_entrada = datetime.strptime("07:00", "%H:%M").time()
    horario_padrao_saida = datetime.strptime("17:00", "%H:%M").time()
    total_extras = timedelta()

    for dia in cartao_ponto:
        if dia.Saida > horario_padrao_saida:
            total_extras += datetime.combine(
                datetime.min, dia.Saida
            ) - datetime.combine(datetime.min, horario_padrao_saida)

        if dia.Entrada < horario_padrao_entrada:
            total_extras += datetime.combine(
                datetime.min, horario_padrao_entrada
            ) - datetime.combine(datetime.min, dia.Entrada)

    # Forma de cálculo alterada em 01/12/2024.
    data_limite_calculo = datetime.strptime("2024-11-30", "%Y-%m-%d").date()
    if cartao_ponto[0].Dia > data_limite_calculo:
        valor_extras = (
            float(salario) / 220 / 60 / 60 * 1.5 * total_extras.seconds
        )
    else:
        valor_extras = (
            float(salario) / 30 / 9 / 60 / 60 * 1.5 * total_extras.seconds
        )

    return total_extras, valor_extras
```

## Exemplo de Uso

```{py3 linenums="1"}
# Suponha que temos um conjunto de registros de cartão de ponto
horas_extras, valor = calcular_horas_extras(5000.00, cartao_ponto)

# Exibe os valores calculados
print(f"Horas extras acumuladas: {horas_extras}")
print(f"Valor a pagar: R${valor:.2f}")
```
