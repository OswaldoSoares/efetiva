
# `get_or_create_contra_cheque_itens`

Função responsável por obter ou criar itens do contracheque para um colaborador, vinculados a um objeto de contracheque específico.

## Fluxo de Execução

1. Recebe os parâmetros `descricao`, `valor`, `registro`, `referencia`, `contra_cheque` e `codigo`.
2. Busca os itens já existentes associados ao `contra_cheque`.
3. Caso nenhum item exista, cria um novo item de contracheque com os valores fornecidos.
4. Atualiza a lista de itens associados ao `contra_cheque`.
5. Retorna a lista de itens do contracheque.

## Parâmetros

- `descricao` (`str`): Descrição do item do contracheque.
- `valor` (`float`): Valor do item do contracheque.
- `registro` (`str`): Indicador do tipo de registro (exemplo: "C" para crédito).
- `referencia` (`str`): Informação adicional sobre o item.
- `contra_cheque` (`ContraCheque`): Objeto do modelo `ContraCheque` ao qual os itens estão associados.
- `codigo` (`str`): Código identificador do evento do contracheque.

## Retorno

- `QuerySet`: Retorna uma lista de objetos `ContraChequeItens` associados ao `contra_cheque`.

## Dependências

- `ContraChequeItens.objects.filter(...)`: ORM para buscar os itens de contracheque.
- `ContraChequeItens.objects.create(...)`: ORM para criar novos itens de contracheque.

## Código da Função

```{py3 linenums="1"}
def get_or_create_contra_cheque_itens(
    descricao, valor, registro, referencia, contra_cheque, codigo
):
    itens = ContraChequeItens.objects.filter(idContraCheque=contra_cheque)

    if not itens.exists():
        ContraChequeItens.objects.create(
            Descricao=descricao,
            Valor=valor,
            Registro=registro,
            Referencia=referencia,
            idContraCheque=contra_cheque,
            Codigo=codigo,
            Vales_id=0,
        )
        # Atualiza queryset após criar
        itens = ContraChequeItens.objects.filter(idContraCheque=contra_cheque)

    return itens
```

## Exemplo de Uso

```{py3 linenums="1"}
# Obtém ou cria um item do contracheque vinculado ao contracheque de ID 42
itens = get_or_create_contra_cheque_itens(
    "Adiantamento", 1000.00, "C", "40%", 42, "5501"
)

# Exibe os itens retornados
for item in itens:
    print(item)
```
