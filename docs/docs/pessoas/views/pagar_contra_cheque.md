# `pagar_contra_cheque`

Função responsável por processar o pagamento do contracheque de um colaborador, utilizando um modal para interação e execução das operações necessárias.

## Fluxo de Execução

1. Chama a função `handle_modal_colaborador(...)` para processar o pagamento dentro de um modal.
2. Define as funções utilizadas no modal:
   - `facade.modal_pagar_contra_cheque`: Responsável por exibir o modal de pagamento.
   - `facade.save_pagamento_contra_cheque`: Salva os dados do pagamento no sistema.
   - `partial(facade.create_contexto_contra_cheque, request)`: Cria o contexto do contracheque do colaborador.
   - `facade.contra_cheque_html_data`: Gera os dados HTML para exibição.

## Parâmetros

- `request` (`HttpRequest`): Requisição HTTP recebida do cliente.

## Retorno

- `HttpResponse`: Retorna o modal processado contendo as informações do pagamento do contracheque.

## Dependências

- `handle_modal_colaborador(...)`: Função que gerencia o modal de pagamento.
- `facade.modal_pagar_contra_cheque(...)`: Exibe o modal de pagamento.
- `facade.save_pagamento_contra_cheque(...)`: Salva os dados do pagamento no banco de dados.
- `facade.create_contexto_contra_cheque(...)`: Cria o contexto do contracheque.
- `facade.contra_cheque_html_data(...)`: Gera os dados HTML para exibição no modal.

## Código da Função

```{py3 linenums="1"}
def pagar_contra_cheque(request):
    return handle_modal_colaborador(
        request,
        facade.modal_pagar_contra_cheque,
        facade.save_pagamento_contra_cheque,
        partial(facade.create_contexto_contra_cheque, request),
        facade.contra_cheque_html_data,
    )
```

## Exemplo de Uso

```{py3 linenums="1"}
# Simula uma requisição HTTP para pagamento de contracheque
resposta = pagar_contra_cheque(request)

# Exibe a resposta retornada
print(resposta)
```
