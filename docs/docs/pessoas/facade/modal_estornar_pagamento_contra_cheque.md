# `modal_estornar_pagamento_contra_cheque`

Função responsável por gerar um modal HTML contendo informações sobre o estorno de pagamento do contracheque de um colaborador.

## Fluxo de Execução

1. Obtém os identificadores do colaborador e do contracheque a partir da requisição.
2. Busca o objeto `ContraCheque` correspondente ao identificador fornecido.
3. Obtém os itens do contracheque ordenados por código.
4. Monta um dicionário `contexto` contendo os dados do colaborador e do contracheque.
5. Renderiza o modal HTML utilizando `html_data.html_modal_estornar_pagamento_contra_cheque(...)`.
6. Retorna a resposta JSON contendo o HTML renderizado.

## Parâmetros

- `request` (`HttpRequest`): Requisição HTTP recebida do cliente.

## Retorno

- `JsonResponse`: Retorna um objeto JSON contendo:
  - `"modal_html"` (`str`): HTML renderizado para exibição do modal.

## Dependências

- `get_request_data(...)`: Obtém parâmetros da requisição.
- `ContraCheque.objects.filter(...).first()`: Busca o objeto de contracheque no banco de dados.
- `ContraChequeItens.objects.filter(...).order_by("Codigo")`: Obtém os itens do contracheque ordenados.
- `html_data.html_modal_estornar_pagamento_contra_cheque(...)`: Renderiza o modal de estorno.
- `JsonResponse(...)`: Retorna a resposta formatada como JSON.

## Código da Função

```{py3 linenums="1"}
def modal_estornar_pagamento_contra_cheque(_, request):
    id_pessoal = get_request_data(request, "id_pessoal")
    id_contra_cheque = get_request_data(request, "id_contra_cheque")

    contra_cheque = ContraCheque.objects.filter(
        idContraCheque=id_contra_cheque
    ).first()

    contra_cheque_itens = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque
    ).order_by("Codigo")

    contexto = {
        "id_pessoal": id_pessoal,
        "contra_cheque": contra_cheque,
        "contra_cheque_itens": contra_cheque_itens,
    }

    modal_html = html_data.html_modal_estornar_pagamento_contra_cheque(
        request, contexto
    )

    return JsonResponse({"modal_html": modal_html})
```

## Exemplo de Uso

```{py3 linenums="1"}
# Gera um modal de estorno para um contracheque específico
resposta = modal_estornar_pagamento_contra_cheque(None, request)

# Exibe a resposta JSON retornada
print(resposta.content.decode("utf-8"))
```
