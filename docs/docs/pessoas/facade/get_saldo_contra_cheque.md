
# `get_saldo_contra_cheque`

Função responsável por calcular o saldo de um contracheque com base nos itens registrados, separando valores de crédito e débito.

## Fluxo de Execução

1. Recebe um conjunto de itens do contracheque.
2. Filtra os valores de crédito (`Registro="C"`) e soma os valores.
3. Filtra os valores de débito (`Registro="D"`) e soma os valores.
4. Calcula o saldo final subtraindo débitos dos créditos.
5. Retorna um dicionário contendo os valores de crédito, débito e saldo.

## Parâmetros

- `contra_cheque_itens` (`QuerySet`): Conjunto de itens do contracheque.

## Retorno

- `dict`: Retorna um dicionário contendo os seguintes campos:
  - `credito` (`Decimal`): Valor total dos créditos.
  - `debito` (`Decimal`): Valor total dos débitos.
  - `saldo` (`Decimal`): Saldo resultante após subtrair os débitos dos créditos.

## Dependências

- `contra_cheque_itens.filter(...)`: ORM para buscar os itens de contracheque.
- `Sum("Valor")`: Agregação para calcular soma dos valores.
- `Decimal(...)`: Tipo utilizado para cálculos financeiros precisos.

## Código da Função

```{py3 linenums="1"}
def get_saldo_contra_cheque(contra_cheque_itens):
    creditos = contra_cheque_itens.filter(Registro="C").aggregate(
        total=Sum("Valor")
    ).get("total") or Decimal(0)

    debitos = contra_cheque_itens.filter(Registro="D").aggregate(
        total=Sum("Valor")
    ).get("total") or Decimal(0)

    saldo = creditos - debitos

    return {"credito": creditos, "debito": debitos, "saldo": saldo}
```

## Exemplo de Uso

```{py3 linenums="1"}
# Suponha que temos um queryset de itens de contracheque
saldo = get_saldo_contra_cheque(contra_cheque_itens)

# Exibe os valores calculados
print(f"Crédito: {saldo['credito']}")
print(f"Débito: {saldo['debito']}")
print(f"Saldo: {saldo['saldo']}")
```
