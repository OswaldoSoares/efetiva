# `calcular_adiantamento`

Função responsável por calcular o valor do adiantamento realizado no contracheque de um colaborador, verificando se o pagamento foi efetuado e retornando a referência percentual e o valor correspondente.

## Fluxo de Execução

1. Busca o contracheque de adiantamento correspondente ao contracheque principal.
2. Caso o adiantamento exista, verifica se foi pago e obtém os valores correspondentes.
3. Retorna a referência percentual e o valor do adiantamento.
4. Caso contrário, retorna `"0%"` e um valor zero.

## Parâmetros

- `contra_cheque` (`ContraCheque`): Objeto representando o contracheque do colaborador.

## Retorno

- `tuple`: Retorna uma tupla com dois elementos:
  - `referencia` (`str`): Percentual do adiantamento realizado (`"0%"` se não foi pago).
  - `valor` (`Decimal`): Valor do adiantamento (`0.00` se não foi pago).

## Dependências

- `ContraCheque.objects.filter(...)`: ORM para buscar o contracheque de adiantamento.
- `ContraChequeItens.objects.filter(...)`: ORM para buscar os itens do contracheque de adiantamento.
- `Decimal(0.00)`: Representação numérica precisa para valores financeiros.

## Código da Função

```{py3 linenums="1"}
def calcular_adiantamento(contra_cheque):
    contra_cheque_adiantamento = ContraCheque.objects.filter(
        Descricao="ADIANTAMENTO",
        MesReferencia=contra_cheque.MesReferencia,
        AnoReferencia=contra_cheque.AnoReferencia,
        idPessoal=contra_cheque.idPessoal,
    ).first()

    if contra_cheque_adiantamento:
        contra_cheque_itens = ContraChequeItens.objects.filter(
            idContraCheque=contra_cheque_adiantamento.idContraCheque,
            Descricao="ADIANTAMENTO",
        ).first()
        referencia = (
            contra_cheque_itens.Referencia
            if contra_cheque_adiantamento.Pago
            else "0%"
        )
        valor = (
            contra_cheque_itens.Valor
            if contra_cheque_adiantamento.Pago
            else Decimal(0.00)
        )

        return referencia, valor

    return "0%", Decimal(0.00)
```

## Exemplo de Uso

```{py3 linenums="1"}
# Suponha que temos um objeto de contracheque
referencia, valor = calcular_adiantamento(contra_cheque)

# Exibe os valores calculados
print(f"Referência do adiantamento: {referencia}")
print(f"Valor do adiantamento: R${valor:.2f}")
```
