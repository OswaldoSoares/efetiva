# `atualizar_ou_adicionar_contra_cheque_item`

Função responsável por atualizar ou adicionar um item ao contracheque, garantindo que registros com valor `0` sejam removidos.

## Fluxo de Execução

1. Recebe os parâmetros do item do contracheque.
2. Se o valor for `0`, exclui o item existente no contracheque.
3. Caso contrário, atualiza ou cria um novo item com os dados fornecidos.
4. Retorna o objeto atualizado ou removido.

## Parâmetros

- `descricao` (`str`): Descrição do item do contracheque.
- `valor` (`float`): Valor do item do contracheque.
- `registro` (`str`): Tipo de registro do item (exemplo: `"C"` para crédito).
- `referencia` (`str`): Informação adicional sobre o item.
- `codigo` (`str`): Código identificador do evento do contracheque.
- `id_contra_cheque` (`int`): Identificador único do contracheque ao qual o item pertence.

## Retorno

- `None`: Se o item for removido por ter valor `0`.
- `ContraChequeItens`: Se um item for criado ou atualizado.

## Dependências

- `ContraChequeItens.objects.filter(...).delete()`: Remove um item existente se o valor for `0`.
- `ContraChequeItens.objects.update_or_create(...)`: Atualiza ou cria um novo item do contracheque.

## Código da Função

```{py3 linenums="1"}
def atualizar_ou_adicionar_contra_cheque_item(
    descricao, valor, registro, referencia, codigo, id_contra_cheque
):
    if valor == 0:
        ContraChequeItens.objects.filter(
            Codigo=codigo,
            idContraCheque_id=id_contra_cheque,
        ).delete()
    else:
        ContraChequeItens.objects.update_or_create(
            Codigo=codigo,
            idContraCheque_id=id_contra_cheque,
            defaults={
                "Descricao": descricao,
                "Registro": registro,
                "Valor": valor,
                "Referencia": referencia,
            },
        )
```

## Código da Função

```{py3 linenums="1"}
# Adiciona ou atualiza um item do contracheque com código "5501"
atualizar_ou_adicionar_contra_cheque_item(
    "ADIANTAMENTO DE SALÁRIO", 1200.00, "C", "40%", "5501", 42
)

# Remove o item do contracheque se o valor for zero
atualizar_ou_adicionar_contra_cheque_item(
    "ADIANTAMENTO DE SALÁRIO", 0, "C", "40%", "5501", 42
)
```
