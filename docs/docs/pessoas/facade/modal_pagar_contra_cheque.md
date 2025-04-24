# `modal_pagar_contra_cheque`

Função responsável por gerar o modal de pagamento de contracheque, retornando um HTML formatado com os dados do contracheque e o saldo computável associado.

## Fluxo de Execução

1. Obtém os parâmetros `id_pessoal` e `id_contra_cheque` da requisição.
2. Busca o objeto `ContraCheque` correspondente ao `id_contra_cheque`.
3. Busca todos os itens (`ContraChequeItens`) associados ao `ContraCheque`.
4. Calcula o saldo computável a partir dos itens do contracheque.
5. Monta o contexto com os dados do contracheque, saldo e `id_pessoal`.
6. Renderiza o modal HTML usando `html_data.html_modal_pagar_contra_cheque`.
7. Retorna um `JsonResponse` contendo o HTML do modal.

## Parâmetros

- `id_teste` (qualquer): Não é utilizado na função, possivelmente legado.
- `request` (`HttpRequest`): Objeto de requisição contendo os dados enviados pelo cliente.

## Retorno

- `JsonResponse`: Retorna um JSON com o campo `"modal_html"` contendo o HTML do modal de pagamento.

## Dependências

- `get_request_data(request, "chave")`: Função para extrair dados da requisição.
- `ContraCheque.objects.filter(...)`: ORM para buscar o contracheque.
- `ContraChequeItens.objects.filter(...)`: ORM para buscar os itens do contracheque.
- `calcular_saldo_computavel(...)`: Função utilitária para calcular o saldo com base nos itens.
- `html_data.html_modal_pagar_contra_cheque(...)`: Renderiza o modal HTML com o contexto.

## Código da Função

```{py3 linenums="1"}
def modal_pagar_contra_cheque(id_teste, request):
    id_pessoal = get_request_data(request, "id_pessoal")
    id_contra_cheque = get_request_data(request, "id_contra_cheque")

    contra_cheque = ContraCheque.objects.filter(
        idContraCheque=id_contra_cheque
    ).first()
    contra_cheque_itens = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque
    )

    saldo = calcular_saldo_computavel(contra_cheque_itens)

    contexto = {
        "id_pessoal": id_pessoal,
        "contra_cheque": contra_cheque,
        "saldo": saldo,
    }

    modal_html = html_data.html_modal_pagar_contra_cheque(request, contexto)

    return JsonResponse({"modal_html": modal_html})
```

## Exemplo de Uso

```{py3 linenums="1"}
from django.test import RequestFactory

# Simula uma requisição POST com IDs
request = RequestFactory().post("/modal-pagar-contra-cheque/", {
    "id_pessoal": 1,
    "id_contra_cheque": 42
})

# Chama a função
response = modal_pagar_contra_cheque(None, request)

# Verifica o HTML retornado
print(response.json())
```
