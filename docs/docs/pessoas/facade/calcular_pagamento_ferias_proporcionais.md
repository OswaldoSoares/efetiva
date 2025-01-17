# `calcular_pagamento_ferias_proporcionais`

Calcula o pagamento de férias proporcionais de um colaborador com base no período aquisitivo e verifica se já houve pagamento anterior.

## Lógica do Cálculo

1. Identifica o período aquisitivo mais recente do colaborador, ordenado pela data inicial.
   - Obtém o período aquisitivo do colaborador pelo identificador único.

2. Determina o período final do ano aquisitivo:
   - Calcula a data final original adicionando um ano e subtraindo um dia da data inicial.
   - Obtém o mês por extenso e o ano da data final.

3. Verifica se existe contracheque de férias para o colaborador no período de referência:
   - Se o pagamento já tiver sido efetuado:
     - Calcula o total pago a partir dos itens do contracheque de férias.
     - Retorna o valor total como desconto de férias.
   - Caso contrário, indica que as férias não foram pagas.

## Parâmetros

- `colaborador` (objeto): Objeto representando o colaborador, contendo as seguintes informações:
  - `id_pessoal` (int): Identificador único do colaborador.

## Funções Necessárias

Esta função depende das seguintes funções ou modelos auxiliares:

- `Aquisitivo` (model): Modelo que representa os períodos aquisitivos do colaborador.
- `ContraCheque` (model): Modelo que representa os contracheques emitidos para o colaborador.
- `ContraChequeItens` (model): Modelo que detalha os itens de cada contracheque.
- `MESES` (dict): Dicionário que mapeia os números dos meses para seus nomes por extenso.
- [`relativedelta`](https://dateutil.readthedocs.io/en/stable/relativedelta.html): Função para calcular diferenças relativas de datas.

## Retorno

- (dict): Dicionário contendo:
  - `desconto_ferias` (Decimal): Valor total das férias já pagas, caso aplicável.
  - `ferias_nao_paga` (str): Indicação de que as férias não foram pagas, caso aplicável.

## Código da Função

```{.py3 linenums="1"}
from decimal import Decimal
from django.db.models import Sum
from dateutil.relativedelta import relativedelta

def calcular_pagamento_ferias_proporcionais(colaborador):
    aquisitivo = (
        Aquisitivo.objects.filter(idPessoal=colaborador.id_pessoal)
        .order_by("-DataInicial")
        .first()
    )

    data_inicial = aquisitivo.DataInicial
    data_final_original = data_inicial + relativedelta(years=1, days=-1)
    mes_por_extenso = MESES[data_final_original.month]
    ano = data_final_original.year

    contra_cheque_ferias = ContraCheque.objects.filter(
        idPessoal=colaborador.id_pessoal,
        MesReferencia=mes_por_extenso,
        AnoReferencia=ano,
        Descricao="FERIAS",
    ).first()

    if contra_cheque_ferias and contra_cheque_ferias.Pago:
        total_ferias_paga = ContraChequeItens.objects.filter(
            idContraCheque=contra_cheque_ferias.id, Registro="C"
        ).aggregate(total=Sum("Valor")).get("total") or Decimal(0)

        return {"desconto_ferias": total_ferias_paga}

    return {"ferias_nao_paga": "ferias_nao_paga"}
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="11 14"}
# Suponha um objeto `colaborador` configurado corretamente
resultado = calcular_pagamento_ferias_proporcionais(colaborador)

if "desconto_ferias" in resultado:
    print(f"Total de férias pagas: {resultado['desconto_ferias']}")
else:
    print("As férias ainda não foram pagas.")

# Resultado esperado (exemplo fictício):
# Caso já tenha sido pago:
Total de férias pagas: 1500.00

# Caso não tenha sido pago:
As férias ainda não foram pagas.
```
