# `index_pagamento`

Renderiza a página inicial do módulo de pagamentos com o contexto necessário para exibir os meses relacionados aos pagamentos.

## Descrição

Esta função é protegida pelo decorador `@has_permission_decorator`, que verifica se o usuário possui permissão para acessar o módulo de pagamentos.

A lógica principal é construída com a função `facade.create_contexto_meses_pagamento`, responsável por criar o contexto necessário para a renderização da página inicial do módulo de pagamentos.

## Fluxo de Execução

1. O decorador `@has_permission_decorator("modulo_pagamentos")` verifica se o usuário tem permissão para acessar o módulo.
2. Chama a função `facade.create_contexto_meses_pagamento` para construir o contexto com os dados dos meses de pagamento.
3. Renderiza a página `pagamentos/index.html` utilizando o contexto retornado.

## Parâmetros

- `request` (HttpRequest): Objeto de solicitação HTTP contendo informações da requisição realizada pelo cliente.

## Retorno

- `HttpResponse`: Resposta HTTP com o conteúdo renderizado da página `pagamentos/index.html`.

## Dependências

- Decorador:
  - [`@has_permission_decorator`](https://django-role-permissions.readthedocs.io/en/stable): Valida as permissões do usuário.
- Função:
  - [`facade.create_contexto_meses_pagamento`](../facade/create_contexto_meses_pagamento.md): Constrói o contexto com informações dos meses de pagamento.

## Código da Função

```{.py3 linenums="1"}
@has_permission_decorator("modulo_pagamentos")
def index_pagamento(request):
    contexto = facade.create_contexto_meses_pagamento()
    return render(request, "pagamentos/index.html", contexto)
```

Exemplo de Uso

```{.py3 linenums="1"}
from django.test import RequestFactory

# Simulação de uma requisição
request = RequestFactory().get("/pagamentos/")

# Execução da função
response = index_pagamento(request)

# Verificação do conteúdo
print(response.content)
```
