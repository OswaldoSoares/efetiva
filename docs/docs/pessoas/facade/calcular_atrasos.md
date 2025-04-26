# `calcular_atrasos`

Função responsável por calcular o total de atrasos de um colaborador com base nos horários registrados no cartão de ponto.

## Fluxo de Execução

1. Define o horário padrão de entrada (`07:00`).
2. Inicializa a variável `total_atrasos` para armazenar o tempo de atraso acumulado.
3. Percorre os registros do cartão de ponto e calcula o tempo adicional nos casos de entrada tardia em relação ao horário padrão.
4. Aplica a regra de cálculo de atrasos com alteração a partir de `01/12/2024`:
   - Se a data do primeiro registro for posterior a `30/11/2024`, usa um fator de `220` horas mensais.
   - Caso contrário, usa um fator baseado em `30` dias e jornada diária de `9` horas.
5. Retorna a quantidade total de atrasos e o valor calculado.

## Parâmetros

- `salario` (`float`): Salário total do colaborador.
- `cartao_ponto` (`list`): Lista de registros do cartão de ponto do colaborador.

## Retorno

- `tuple`: Retorna uma tupla com dois elementos:
  - `total_atrasos` (`timedelta`): Tempo total de atrasos acumulados.
  - `valor_atrasos` (`float`): Valor financeiro correspondente aos atrasos.

## Dependências

- `datetime.strptime(...)`: Conversão de strings para objetos de tempo.
- `datetime.combine(...)`: Operação para calcular diferenças entre horários.
- `timedelta()`: Tipo utilizado para representar intervalos de tempo.

## Código da Função

```{py3 linenums="1"}
def calcular_atrasos(salario, cartao_ponto):
    """Calcula o total de atrasos e o valor correspondente baseado no salário."""
    horario_padrao_entrada = datetime.strptime("07:00", "%H:%M").time()
    total_atrasos = timedelta()

    for dia in cartao_ponto:
        if dia.Entrada > horario_padrao_entrada:
            total_atrasos += datetime.combine(
                datetime.min, dia.Entrada
            ) - datetime.combine(datetime.min, horario_padrao_entrada)

    # Forma de cálculo alterada em 01/12/2024.
    data_limite_calculo = datetime.strptime("2024-11-30", "%Y-%m-%d").date()
    if cartao_ponto[0].Dia > data_limite_calculo:
        valor_atrasos = float(salario) / 220 / 60 / 60 * total_atrasos.seconds
    else:
        valor_atrasos = (
            float(salario) / 30 / 9 / 60 / 60 * total_atrasos.seconds
        )

    return total_atrasos, valor_atrasos
```

## Código da Função

```{py3 linenums="1"}
# Suponha que temos um conjunto de registros de cartão de ponto
atrasos, valor = calcular_atrasos(5000.00, cartao_ponto)

# Exibe os valores calculados
print(f"Atrasos acumulados: {atrasos}")
print(f"Valor descontado: R${valor:.2f}")
```
