# `save_estorno_pagamento_contra_cheque`

Função responsável por processar o estorno do pagamento de um contracheque, garantindo que seu valor seja zerado e o status de pagamento atualizado.

## Fluxo de Execução

1. Verifica se a requisição é do tipo `POST`, caso contrário, a função não é executada.
2. Obtém o identificador do contracheque a partir dos dados enviados na requisição.
3. Atualiza o registro do contracheque no banco de dados:
   - Define o valor como `0.00`.
   - Define o status de pagamento como `False` (não pago).
4. Retorna uma mensagem indicando sucesso ou falha na operação.

## Parâmetros

- `request` (`HttpRequest`): Requisição HTTP recebida do cliente.

## Retorno

- `dict`: Retorna um dicionário contendo:
  - `"mensagem"` (`str`): Mensagem informando o resultado da operação.

## Dependências

- `request.POST.get(...)`: Obtém dados do corpo da requisição `POST`.
- `ContraCheque.objects.filter(...).update(...)`: Atualiza os valores no banco de dados.
- `Decimal(0.00)`: Representação numérica precisa para valores financeiros.

## Código da Função

```{py3 linenums="1"}
def save_estorno_pagamento_contra_cheque(request):
    if request.method == "POST":
        id_contra_cheque = request.POST.get("id_contra_cheque")

        if ContraCheque.objects.filter(idContraCheque=id_contra_cheque).update(
            Valor=Decimal(0.00), Pago=False
        ):
            mensagem = "Pagamento estornado com sucesso"

        else:
            mensagem = "Não foi possivel estornar o pagamento"

        return {"mensagem": mensagem}
```

## Exemplo de Uso

```{py3 linenums="1"}
# Simula uma requisição POST para estorno do pagamento do contracheque
resposta = save_estorno_pagamento_contra_cheque(request)

# Exibe a resposta retornada
print(resposta)
```
