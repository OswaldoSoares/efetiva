# `estornar_pagamento_contra_cheque`

Função responsável por processar o estorno do pagamento do contracheque de um colaborador, utilizando um modal para interação e execução das operações necessárias.

## Fluxo de Execução

1. Chama a função `handle_modal_colaborador(...)` para processar o estorno do pagamento dentro de um modal.
2. Define as funções utilizadas no modal:
   - `facade.modal_estornar_pagamento_contra_cheque`: Responsável por exibir o modal de estorno.
   - `facade.save_estorno_pagamento_contra_cheque`: Salva os dados do estorno no sistema.
   - `partial(facade.create_contexto_contra_cheque, request)`: Cria o contexto do contracheque do colaborador.
   - `facade.contra_cheque_html_data`: Gera os dados HTML para exibição.

## Parâmetros

- `request` (`HttpRequest`): Requisição HTTP recebida do cliente.

## Retorno

- `HttpResponse`: Retorna o modal processado contendo as informações do estorno do contracheque.

## Dependências

- `handle_modal_colaborador(...)`: Função que gerencia o modal de estorno.
- `facade.modal_estornar_pagamento_contra_cheque(...)`: Exibe o modal de estorno.
- `facade.save_estorno_pagamento_contra_cheque(...)`: Salva os dados do estorno no banco de dados.
- `facade.create_contexto_contra_cheque(...)`: Cria o contexto do contracheque.
- `facade.contra_cheque_html_data(...)`: Gera os dados HTML para exibição no modal.

## Código da Função

```{py3 linenums="1"}
def estornar_pagamento_contra_cheque(request):
    return handle_modal_colaborador(
        request,
        facade.modal_estornar_pagamento_contra_cheque,
        facade.save_estorno_pagamento_contra_cheque,
        partial(facade.create_contexto_contra_cheque, request),
        facade.contra_cheque_html_data,
    )
```

## Exemplo de Uso

```{py3 linenums="1"}
# Simula uma requisição HTTP para estorno do pagamento do contracheque
resposta = estornar_pagamento_contra_cheque(request)

# Exibe a resposta retornada
print(resposta)
```
