# `save_pagamento_contra_cheque`

Função responsável por registrar o pagamento de um contracheque, atualizando seu valor e marcando-o como pago no banco de dados.

## Fluxo de Execução

1. Obtém os parâmetros `id_contra_cheque` e `valor` da requisição (`POST`).
2. Converte os parâmetros para os tipos apropriados (`int` e `float`).
3. Atualiza o contracheque correspondente com o novo valor e define o campo `Pago` como `True`.
4. Define uma mensagem de sucesso ou erro, com base no resultado da operação.
5. Retorna um dicionário com a mensagem apropriada.

## Parâmetros

- `request` (`HttpRequest`): Objeto de requisição contendo os dados enviados pelo cliente.

## Retorno

- `dict`: Um dicionário contendo a chave `"mensagem"` com o resultado da operação.

## Dependências

- `ContraCheque.objects.filter(...).update(...)`: Atualiza o contracheque no banco de dados.

## Código da Função

```{py3 linenums="1"}
def save_pagamento_contra_cheque(request):
    id_contra_cheque = int(request.POST.get("id_contra_cheque"))
    valor = float(request.POST.get("valor"))

    if ContraCheque.objects.filter(idContraCheque=id_contra_cheque).update(
        Valor=valor, Pago=True
    ):
        mensagem = "Informado pagamento do contra cheque com sucesso"
    else:
        mensagem = "Não foi possivel informar o pagamento"

    return {"mensagem": mensagem}
```

## Exemplo de Uso

```{py3 linenums="1"}
from django.test import RequestFactory

# Simula uma requisição POST com ID e valor
request = RequestFactory().post("/save-pagamento/", {
    "id_contra_cheque": 42,
    "valor": 2500.00
})

# Chama a função
response = save_pagamento_contra_cheque(request)

# Verifica a mensagem retornada
print(response["mensagem"])
```
