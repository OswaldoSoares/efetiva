# `faltas_periodo_aquisitivo`

Gera uma lista com as datas de faltas não remuneradas de um colaborador dentro de um período aquisitivo.

## Lógica da Função

A função consulta o banco de dados para identificar as faltas não remuneradas de um colaborador dentro do intervalo de datas especificado no período aquisitivo. As datas das faltas são retornadas no formato `dd/mm/aaaa`.

## Parâmetros
- `id_pessoal` (int): Identificador único do colaborador no banco de dados.
- `aquisitivo`: Objeto contendo os atributos:
  - `DataInicial` (datetime): Data inicial do período aquisitivo.
  - `DataFinal` (datetime): Data final do período aquisitivo.

## Retorno
- (List[str]): Lista de strings representando as datas das faltas no formato `dd/mm/aaaa`.

## Código da função

```{.py3 linenums="1"}
def faltas_periodo_aquisitivo(id_pessoal: int, aquisitivo) -> List[str]:
    inicio = aquisitivo.DataInicial
    final = aquisitivo.DataFinal

    dias_faltas = CartaoPonto.objects.filter(
        idPessoal=id_pessoal,
        Dia__range=[inicio, final],
        Ausencia="FALTA",
        Remunerado=False,
    ).values_list("Dia", flat=True)

    return [datetime.strftime(dia, "%d/%m/%Y") for dia in dias_faltas]
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="19"}
# Exemplo de um objeto com período aquisitivo
>>>class PeriodoAquisitivo:
...    def __init__(self, data_inicial, data_final):
...        self.DataInicial = data_inicial
...        self.DataFinal = data_final

# Período de 1º de janeiro de 2024 a 31 de dezembro de 2024
>>>aquisitivo = PeriodoAquisitivo(
...    data_inicial=datetime(2024, 1, 1),
...    data_final=datetime(2024, 12, 31)
...)

# Obtendo as faltas de um colaborador com ID 1234
>>>faltas = faltas_periodo_aquisitivo(1234, aquisitivo)

>>>print(faltas)

# Resultado esperado (exemplo fictício):
['15/03/2024', '28/05/2024', '10/09/2024']
```
