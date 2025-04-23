# `calcular_saldo_computavel`

Função responsável por calcular o saldo computável de um contracheque a partir de um queryset de itens, considerando apenas os eventos marcados como computáveis.

## Fluxo de Execução

1. Cria um dicionário de lookup (`EVENTO_LOOKUP`) a partir da constante `EVENTOS_CONTRA_CHEQUE`.
2. Inicializa o saldo como `Decimal("0.00")`.
3. Percorre cada item do queryset.
4. Para cada item, busca o evento correspondente pelo código.
5. Se o evento for computável:
   - Soma o valor se `Registro == "C"` (crédito).
   - Subtrai o valor se `Registro != "C"` (débito).
6. Retorna o saldo total computável.

## Parâmetros

- `queryset` (QuerySet): Conjunto de registros relacionados a eventos de contracheque. Espera-se que cada item tenha os atributos:
  - `Codigo` (str): Código do evento.
  - `Registro` (str): Indicador de tipo de lançamento ("C" para crédito, outro para débito).
  - `Valor` (Decimal): Valor monetário do lançamento.

## Retorno

- `Decimal`: Valor total computável dos eventos, considerando créditos e débitos computáveis.

## Dependências

- [`EVENTOS_CONTRA_CHEQUE`](/core/tools/eventos_contra_cheque): Coleção de eventos definidas como constantes no formato de `dataclass` com os campos `codigo`, `descricao`, `computavel` e `credito`.

## Código da Função

```{.py3 linenums="1"}
from decimal import Decimal

def calcular_saldo_computavel(queryset) -> Decimal:
    saldo = Decimal("0.00")
    EVENTO_LOOKUP = {evento.codigo: evento for evento in EVENTOS_CONTRA_CHEQUE}

    for item in queryset:
        evento = EVENTO_LOOKUP.get(item.Codigo)
        if evento and evento.computavel:
            saldo += item.Valor if item.Registro == "C" else -item.Valor

    return saldo
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="8"}
# Supondo um queryset com objetos que têm os atributos: Codigo, Registro e Valor
contra_cheque_itens = ContraChequeItens.objects.filter(idContraCheque=123)

saldo = calcular_saldo_computavel(contra_cheque_itens)
print(f"Saldo computável: R$ {saldo:.2f}")

# Resultado esperado (exemplo fictício):
"Saldo computável: R$ 1565,85"

```
