# `calcular_dsr_feriado`

Função responsável por calcular o número de dias de descanso semanal remunerado (DSR) adicionais devido a feriados em semanas onde o colaborador teve faltas.

## Fluxo de Execução

1. Obtém o primeiro e o último dia registrado no cartão de ponto.
2. Calcula o último dia do mês seguinte para garantir que todos os feriados relevantes sejam considerados.
3. Busca os feriados cadastrados no sistema dentro do intervalo de datas.
4. Converte os feriados para objetos `date`.
5. Obtém os dias em que o colaborador esteve de férias dentro dos feriados registrados.
6. Filtra os feriados válidos, removendo aqueles que coincidem com dias de férias.
7. Identifica as semanas em que há feriados válidos, excluindo aqueles que caem no domingo.
8. Para cada semana onde houve falta, verifica se há um feriado válido na semana seguinte e adiciona um dia de DSR caso positivo.
9. Retorna o número atualizado de dias de DSR.

## Parâmetros

- `id_pessoal` (`int`): Identificador único do colaborador.
- `dias_dsr` (`int`): Número inicial de dias de DSR.
- `semanas_faltas` (`list`): Lista de semanas onde houve faltas do colaborador.
- `cartao_ponto` (`QuerySet`): Conjunto de registros do cartão de ponto do colaborador.

## Retorno

- `int`: Retorna o número atualizado de dias de descanso semanal remunerado.

## Dependências

- `cartao_ponto.order_by("Dia").first()`: Obtém o primeiro dia registrado no cartão de ponto.
- `cartao_ponto.order_by("Dia").last()`: Obtém o último dia registrado no cartão de ponto.
- `relativedelta(months=+1)`: Calcula o último dia do mês seguinte.
- `Parametros.objects.filter(...)`: Filtra os registros de feriados cadastrados no sistema.
- `datetime.strptime(...)`: Conversão de strings para objetos `date`.
- `CartaoPonto.objects.filter(...)`: Filtra os dias de férias registrados no cartão de ponto.
- `datetime.strftime(feriado, "%V")`: Obtém o número da semana para cada feriado válido.

## Código da Função

```{py3 linenums="1"}
def calcula_dsr_feriado(id_pessoal, dias_dsr, semanas_faltas, cartao_ponto):
    """Calcula o número de dias de DSR considerando feriados e semanas com faltas."""
    primeiro_dia = cartao_ponto.order_by("Dia").first().Dia
    ultimo_dia = cartao_ponto.order_by("Dia").last().Dia
    ultimo_dia_mes_seguinte = ultimo_dia + relativedelta(months=+1)

    feriados = Parametros.objects.filter(
        Chave="FERIADO",
        Valor__range=[primeiro_dia, ultimo_dia_mes_seguinte],
    ).values_list("Valor", flat=True)

    feriado_datas = {
        datetime.strptime(data, "%Y-%m-%d").date() for data in feriados
    }

    dias_em_ferias = set(
        CartaoPonto.objects.filter(
            Dia__in=feriado_datas, idPessoal=id_pessoal, Ausencia="FERIAS"
        ).values_list("Dia", flat=True)
    )

    feriados_validos = feriado_datas - dias_em_ferias

    semanas_feriados = {
        int(datetime.strftime(feriado, "%V"))
        for feriado in feriados_validos
        if feriado.weekday() != 6  # Exclui feriados no domingo
    }

    for semana in semanas_faltas:
        semana_atual = 0 if semana == 52 else semana
        if semana_atual + 1 in semanas_feriados:
            dias_dsr += 1

    return dias_dsr
```

## Exemplo de Uso

```{py3 linenums="1"}
# Suponha que temos um conjunto de registros de cartão de ponto
dias_dsr = calcula_dsr_feriado(123, 4, [35, 36], cartao_ponto)

# Exibe os valores calculados
print(f"Dias de DSR ajustados: {dias_dsr}")
```
