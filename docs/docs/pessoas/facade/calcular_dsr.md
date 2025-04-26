# `calcular_dsr`

Função responsável por calcular o número de dias de descanso semanal remunerado (DSR) de um colaborador, levando em conta semanas com faltas e feriados.

## Fluxo de Execução

1. Filtra os registros do cartão de ponto onde há ausência (`Ausencia="FALTA"`), excluindo faltas abonadas (`Remunerado=1`).
2. Obtém a lista das semanas onde houve faltas.
3. Converte a lista de semanas em um conjunto para eliminar duplicatas.
4. Verifica se o primeiro dia registrado no cartão de ponto está entre segunda e quinta-feira.
5. Caso positivo, ajusta para considerar faltas do mês anterior.
6. Calcula o número inicial de dias de DSR com base nas semanas de falta.
7. Ajusta o número de dias de DSR levando em consideração feriados.
8. Calcula o valor financeiro correspondente ao DSR.
9. Retorna a quantidade de dias de DSR e o valor calculado.

## Parâmetros

- `id_pessoal` (`int`): Identificador único do colaborador.
- `salario` (`float`): Salário total do colaborador.
- `cartao_ponto` (`QuerySet`): Conjunto de registros do cartão de ponto do colaborador.

## Retorno

- `tuple`: Retorna uma tupla com dois elementos:
  - `dias_dsr` (`int`): Número de dias de descanso semanal remunerado.
  - `valor_dsr` (`float`): Valor financeiro correspondente ao DSR.

## Dependências

- `cartao_ponto.filter(...)`: Filtra os registros do cartão de ponto para identificar faltas.
- `datetime.strftime(falta.Dia, "%V")`: Obtém o número da semana para cada falta.
- `timedelta(...)`: Operação para calcular intervalos de tempo.
- `calcular_dsr_feriado(...)`: Ajusta os dias de DSR considerando feriados.
- `CartaoPonto.objects.filter(...)`: Obtém faltas do mês anterior.
- `values()`: Converte a query de registros em uma lista de dicionários.

## Código da Função

```{py3 linenums="1"}
def calcular_dsr(id_pessoal, salario, cartao_ponto):
    """Calcula o número de dias de DSR de um colaborador considerando semanas de faltas e feriados."""
    dias_faltas = cartao_ponto.filter(Ausencia="FALTA").exclude(Remunerado=1)

    semanas_faltas = []
    for falta in dias_faltas:
        semanas_faltas.append(datetime.strftime(falta.Dia, "%V"))

    semanas_faltas = list(map(int, semanas_faltas))
    semanas_faltas = set(semanas_faltas)

    primeiro_dia = cartao_ponto.order_by("Dia").first().Dia

    if 1 <= primeiro_dia.weekday() <= 4:
        inicio = primeiro_dia - timedelta(primeiro_dia.weekday())
        fim = primeiro_dia - timedelta(1)
        faltas_mes_anterior = list(
            CartaoPonto.objects.filter(
                idPessoal=id_pessoal,
                Ausencia="FALTA",
                Remunerado=False,
                Dia__range=[inicio, fim],
            ).values()
        )
        if faltas_mes_anterior:
            semana_mes_anterior = datetime.strftime(
                faltas_mes_anterior[0]["Dia"], "%V"
            )
            if semana_mes_anterior in semanas_faltas:
                semanas_faltas.remove(int(semana_mes_anterior))

    dias_dsr = len(semanas_faltas)
    dias_dsr = calcular_dsr_feriado(
        id_pessoal, dias_dsr, semanas_faltas, cartao_ponto
    )

    valor_dsr = salario / 30 * dias_dsr

    return dias_dsr, valor_dsr
```

## Código da Função

```{py3 linenums="1"}
# Suponha que temos um conjunto de registros de cartão de ponto
dias_dsr, valor_dsr = calcular_dsr(123, 5000.00, cartao_ponto)

# Exibe os valores calculados
print(f"Dias de DSR ajustados: {dias_dsr}")
print(f"Valor correspondente: R${valor_dsr:.2f}")
```
