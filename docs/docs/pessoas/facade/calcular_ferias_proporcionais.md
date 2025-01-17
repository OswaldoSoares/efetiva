# `calcular_ferias_proporcionais`

Calcula os valores de férias proporcionais de um colaborador com base no período aquisitivo, número de faltas, e o salário base.

## Lógica do Cálculo

1. Identifica ou cria o período aquisitivo mais recente para o colaborador.
   - Se o colaborador não possuir período aquisitivo registrado, cria um novo com as datas de admissão e demissão.
   - Caso contrário, atualiza a data final do período existente.

2. Calcula o número de faltas no período aquisitivo.

3. Determina o número de meses trabalhados no período (em dozeavos).

4. Calcula os dias proporcionais de férias com base nas faltas e meses trabalhados.

5. Calcula o valor proporcional das férias:
   - Divisão do salário base por 30 dias, multiplicado pelo número de dias proporcionais.
   - Um terço adicional do valor calculado.

## Parâmetros

- `colaborador` (objeto): Objeto representando o colaborador, contendo as seguintes informações:
  - `id_pessoal` (int): Identificador único do colaborador.
  - `dados_profissionais` (objeto): Informações sobre o vínculo empregatício, incluindo:
    - `data_admissao` (date): Data de admissão do colaborador.
    - `data_demissao` (date): Data de demissão do colaborador.
  - `salarios` (objeto): Informações salariais, incluindo:
    - `Salario` (Decimal): Salário base do colaborador.

## Funções Necessárias

Esta função depende das seguintes funções auxiliares. Acesse os links para consultar suas respectivas documentações:

- [`faltas_periodo_aquisitivo`](./faltas_periodo_aquisitivo.md): Função que calcula as faltas do colaborador no período aquisitivo.
- [`meses_proporcionais_ferias`](./meses_proporcionais_ferias.md): Função que calcula o número de meses proporcionais de férias em dozeavos.
- [`calcular_dias_ferias_proporcionais`](./calcular_dias_ferias_proporcionais.md): Função que calcula os dias proporcionais de férias com base no número de faltas e meses trabalhados.

## Retorno

- (dict): Dicionário contendo:
  - `ferias_valor` (Decimal): Valor proporcional das férias.
  - `ferias_meses` (int): Número de meses trabalhados no período aquisitivo.
  - `ferias_um_terco` (Decimal): Valor adicional correspondente a um terço do valor proporcional das férias.

## Código da Função

```{.py3 linenums="1"}
from decimal import Decimal, ROUND_HALF_UP

def calcular_ferias_proporcionais(colaborador):
    aquisitivo = (
        Aquisitivo.objects.filter(idPessoal=colaborador.id_pessoal)
        .order_by("-DataInicial")
        .first()
    )

    if not aquisitivo:
        aquisitivo = Aquisitivo.objects.create(
            DataInicial=colaborador.dados_profissionais.data_admissao,
            DataFinal=colaborador.dados_profissionais.data_demissao,
            idPessoal_id=colaborador.id_pessoal,
        )
    else:
        aquisitivo.DataFinal = colaborador.dados_profissionais.data_demissao
        aquisitivo.save()

    faltas = faltas_periodo_aquisitivo(colaborador.id_pessoal, aquisitivo)

    dozeavos = meses_proporcionais_ferias(
        aquisitivo.DataInicial, aquisitivo.DataFinal
    )

    dias = Decimal(calcular_dias_ferias_proporcionais(len(faltas), dozeavos))

    salario_base = colaborador.salarios.salarios.Salario
    valor = (salario_base / 30 * dias).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    um_terco = (valor / 3).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "ferias_valor": valor,
        "ferias_meses": dozeavos,
        "ferias_um_terco": um_terco,
    }
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="5-9"}
ferias = calcular_ferias_proporcionais(colaborador)
print(ferias)

# Resultado esperado (exemplo fictício):
{
    "ferias_valor": Decimal('1234.56'),
    "ferias_meses": 11,
    "ferias_um_terco": Decimal('411.52')
}
```
