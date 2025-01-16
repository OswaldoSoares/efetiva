# `calcular_decimo_terceiro_proporcional`

Calcula o valor proporcional do décimo terceiro salário de um colaborador com base em suas datas de admissão e demissão, pagamentos anteriores e salário base.

## Lógica do Cálculo

1. Determina o início e o fim do ano de referência para o cálculo, ajustando para o ano anterior caso o colaborador tenha sido desligado.
2. Consulta as parcelas de décimo terceiro já pagas no ano de referência.
3. Calcula o período proporcional com base nas datas de admissão e demissão.
4. Calcula o valor proporcional ao décimo terceiro considerando o salário base do colaborador.

## Parâmetros

- `colaborador` (objeto): Objeto representando o colaborador, contendo as seguintes informações:
  - `id_pessoal` (int): Identificador único do colaborador.
  - `dados_profissionais` (objeto): Informações sobre o vínculo empregatício, incluindo:
    - `data_admissao` (date): Data de admissão do colaborador.
    - `data_demissao` (date): Data de demissão do colaborador.
  - `salarios` (objeto): Informações salariais, incluindo:
    - `Salario` (Decimal): Salário base do colaborador.

## Funções Necessárias

Esta função depende da seguinte função auxiliar. Consulte sua documentação para mais detalhes:

- [`meses_proporcionais_decimo_terceiro`](./meses_proporcionais_decimo_terceiro.md): Calcula o número de meses proporcionais ao décimo terceiro.

## Retorno

- (dict): Dicionário contendo:
  - `decimo_terceiro_valor` (Decimal): Valor proporcional do décimo terceiro salário.
  - `decimo_terceiro_meses` (int): Quantidade de meses proporcionais ao décimo terceiro.
  - `decimo_terceiro_parcelas_pagas` (QuerySet): Parcelas já pagas do décimo terceiro no ano de referência.
  - `decimo_terceiro_total_pago` (Decimal): Valor total já pago referente ao décimo terceiro.

## Código da Função

```{.py3 linenums="1"}
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum

def calcular_decimo_terceiro_proporcional(colaborador):
    data_admissao = colaborador.dados_profissionais.data_admissao
    data_demissao = colaborador.dados_profissionais.data_demissao
    hoje = datetime.today().date()
    inicio_ano = date(hoje.year, 1, 1)
    fim_ano = date(hoje.year, 12, 31)

    if hoje.year > data_demissao.year:
        inicio_ano = date(hoje.year - 1, 1, 1)
        fim_ano = date(hoje.year - 1, 12, 31)

    parcelas_pagas = ContraCheque.objects.filter(
        idPessoal=colaborador.id_pessoal,
        Descricao="DECIMO TERCEIRO",
        AnoReferencia=data_demissao.year,
        Pago=True,
    )

    total_valor = (
        parcelas_pagas.aggregate(soma_valor=Sum("Valor"))["soma_valor"] or 0
    )

    data_inicial = data_admissao if data_admissao > inicio_ano else inicio_ano
    data_final = data_demissao if data_demissao < fim_ano else fim_ano

    dozeavos = meses_proporcionais_decimo_terceiro(data_inicial, data_final)

    valor = (colaborador.salarios.salarios.Salario / 12 * dozeavos).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return {
        "decimo_terceiro_valor": valor,
        "decimo_terceiro_meses": dozeavos,
        "decimo_terceiro_parcelas_pagas": parcelas_pagas,
        "decimo_terceiro_total_pago": total_valor,
    }
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="9-13"}
# Suponha um objeto `colaborador` configurado corretamente
dados = calcular_decimo_terceiro_proporcional(colaborador)

print(dados["decimo_terceiro_valor"])
print(dados["decimo_terceiro_meses"])
print(dados["decimo_terceiro_total_pago"])

# Resultado esperado (exemplo fictício):
{
    "decimo_terceiro_valor": Decimal('1500.00'),
    "decimo_terceiro_meses": 11,
    "decimo_terceiro_total_pago": Decimal('500.00')
}
```

