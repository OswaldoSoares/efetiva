# `index_pessoal`

Renderiza a página inicial do módulo de colaboradores com o contexto necessário para exibir informações sobre os funcionários mensalistas.

## Descrição

Esta função é protegida pelo decorador `@has_permission_decorator`, que verifica se o usuário possui permissão para acessar o módulo de colaboradores.

A lógica principal é construída com as funções `facade.create_contexto_categoria` e `facade.create_contexto_colaboradores`, responsáveis por criar o contexto necessário para a renderização da página inicial.

## Fluxo de Execução

1. O decorador `@has_permission_decorator("modulo_colaboradores")` verifica se o usuário tem permissão para acessar o módulo.
2. Chama a função `facade.create_contexto_categoria` para obter o contexto base.
3. Chama a função `facade.create_contexto_colaboradores("MENSALISTA", True)` para adicionar ao contexto os colaboradores mensalistas ativos.
4. Renderiza a página `pessoas/index.html` utilizando o contexto final.

## Parâmetros

- `request` (HttpRequest): Objeto de solicitação HTTP contendo informações da requisição realizada pelo cliente.

## Retorno

- `HttpResponse`: Resposta HTTP com o conteúdo renderizado da página `pessoas/index.html`.

## Dependências

- Decorador:
  - [`@has_permission_decorator`](https://django-role-permissions.readthedocs.io/en/stable): Valida as permissões do usuário.
- Funções:
  - `facade.create_contexto_categoria()`: Constrói o contexto base para a página.
  - `facade.create_contexto_colaboradores("MENSALISTA", True)`: Adiciona ao contexto os colaboradores mensalistas ativos.

## Código da Função

```{.py3 linenums="1"}
@has_permission_decorator("modulo_colaboradores")
def indexpessoal(request):
    contexto = facade.create_contexto_categoria()
    contexto.update(facade.create_contexto_colaboradores("MENSALISTA", True))
    return render(request, "pessoas/index.html", contexto)
```

## Exemplo de Uso

```{.py3 linenums="1"}
from django.test import RequestFactory

# Simulação de uma requisição
request = RequestFactory().get("/pessoas/")

# Execução da função
response = indexpessoal(request)

# Verificação do conteúdo
print(response.content)
```

