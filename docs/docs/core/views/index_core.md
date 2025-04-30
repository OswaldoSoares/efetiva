# `index_core`

Função responsável por renderizar a página inicial do módulo, garantindo que o usuário esteja autenticado antes de acessar o conteúdo.

## Fluxo de Execução

1. Aplica o decorador `@login_required` para exigir que o usuário esteja logado.
2. Renderiza o template `"core/index.html"` utilizando `render(...)`.
3. Retorna a página inicial do sistema.

## Parâmetros

- `request` (`HttpRequest`): Requisição HTTP recebida do cliente.

## Retorno

- `HttpResponse`: Retorna a página inicial renderizada.

## Dependências

- `login_required(login_url="login")`: Redireciona para a página de login caso o usuário não esteja autenticado.
- `render(...)`: Renderiza o template HTML.

## Código da Função

```{py3 linenums="1"}
@login_required(login_url="login")
def index_core(request):
    """Renderiza a página inicial do sistema, exigindo autenticação."""
    return render(request, "core/index.html")
```

## Exemplo de Uso

```{py3 linenums="1"}
# Acessa a página inicial do módulo (usuário deve estar autenticado)
resposta = index_core(request)

# Exibe a resposta retornada
print(resposta)
```
