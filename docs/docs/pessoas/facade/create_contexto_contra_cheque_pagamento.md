
# `create_contexto_contra_cheque_pagamento`

Função responsável por gerar o contexto de contracheque para pagamento salarial, incluindo os itens do contracheque e o saldo computável associado.

## Fluxo de Execução

1. Obtém os parâmetros `id_pessoal`, `mes` e `ano` da requisição.
2. Converte o número do mês para sua forma por extenso.
3. Busca ou cria um objeto `ContraCheque` para o colaborador referente ao pagamento.
4. Atualiza o contracheque com os dados do pagamento por meio de `atualizar_contra_cheque_pagamento`.
5. Obtém os itens do contracheque ordenados por tipo de registro.
6. Obtém o arquivo gerado referente ao contracheque.
7. Calcula o saldo do contracheque.
8. Retorna o contexto com os dados do contracheque, itens e saldo.

## Parâmetros

- `request` (`HttpRequest`): Objeto de requisição contendo os dados enviados pelo cliente.
  - `id_pessoal` (`str`): Identificador único do colaborador.
  - `mes` (`int`): Mês de referência do pagamento.
  - `ano` (`int`): Ano de referência do pagamento.

## Retorno

- `dict`: Retorna um dicionário contendo os seguintes campos:
  - `mensagem` (`str`): Mensagem informativa sobre o pagamento processado.
  - `contra_cheque` (`ContraCheque`): Objeto representando o contracheque do colaborador.
  - `contra_cheque_itens` (`QuerySet`): Lista de itens do contracheque ordenados por registro.
  - `id_pessoal` (`str`): Identificador do colaborador.
  - `file` (`File`): Arquivo do contracheque gerado.
  - `saldo_computavel` (`dict`): Saldo calculado do contracheque.

## Dependências

- `obter_mes_por_numero(mes)`: Converte um número de mês para seu nome por extenso.
- `get_or_create_contra_cheque(...)`: Obtém ou cria um contracheque.
- `atualizar_contra_cheque_pagamento(...)`: Atualiza os dados de pagamento do contracheque.
- `ContraChequeItens.objects.filter(...)`: Obtém os itens do contracheque.
- `get_file_contra_cheque(...)`: Obtém o arquivo gerado do contracheque.
- `get_saldo_contra_cheque(...)`: Calcula o saldo do contracheque.

## Código da Função

```{py3 linenums="1"}
def create_contexto_contra_cheque_pagamento(request):
    id_pessoal = request.GET.get("id_pessoal")
    mes = int(request.GET.get("mes"))
    mes_por_extenso = obter_mes_por_numero(mes)
    ano = int(request.GET.get("ano"))

    contra_cheque, criado = get_or_create_contra_cheque(
        mes_por_extenso, ano, "PAGAMENTO", id_pessoal
    )

    atualizar_contra_cheque_pagamento(id_pessoal, mes, ano, contra_cheque)

    contra_cheque_itens = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque
    ).order_by("Registro")

    file = get_file_contra_cheque(contra_cheque.idContraCheque)

    return {
        "mensagem": f"Pagamento selecionado: {mes_por_extenso}/{ano}",
        "contra_cheque": contra_cheque,
        "contra_cheque_itens": contra_cheque_itens,
        "id_pessoal": id_pessoal,
        **get_saldo_contra_cheque(contra_cheque_itens),
    }
```

## Exemplo de Uso

```{py3 linenums="1"}
from django.test import RequestFactory

# Simula uma requisição GET com os parâmetros necessários
request = RequestFactory().get("/contra-cheque-pagamento/", {
    "id_pessoal": "123",
    "mes": "4",
    "ano": "2025"
})

# Chama a função
contexto = create_contexto_contra_cheque_pagamento(request)

# Exibe o contexto retornado
print(contexto)
```

