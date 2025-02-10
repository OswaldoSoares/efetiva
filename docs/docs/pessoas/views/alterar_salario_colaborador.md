# `alterar_salario_colaborador`

Função responsável por validar e processar a alteração do salário de um colaborador.

## Fluxo de Execução

1. Valida os dados da requisição por meio da função `facade.validar_modal_salario_colaborador`.
   - Se houver erros de validação, retorna a resposta de erro imediatamente.

2. Chama a função `handle_modal_colaborador` para processar os dados e salvar as alterações.
   - Utiliza `facade.modal_salario_colaborador` para obter os dados do modal de salário.
   - Usa `facade.save_salario_colaborador` para salvar a informação no banco de dados.
   - Passa `facade.create_contexto_salario` com `request` para gerar o contexto necessário.
   - Utiliza `facade.salario_html_data` para formatar os dados em HTML.

## Parâmetros

- `request` (HttpRequest): Objeto de requisição HTTP contendo os dados da alteração do salário do colaborador.

## Retorno

- `HttpResponse` ou `dict`: Se houver erro na validação, retorna um dicionário com a resposta de erro. Caso contrário, retorna uma resposta processada pelo `handle_modal_colaborador`.

## Dependências

- `facade.validar_modal_salario_colaborador(request)`: Valida os dados enviados.
- `facade.modal_salario_colaborador`: Obtém os dados do modal de salário.
- `facade.save_salario_colaborador`: Salva a alteração do salário do colaborador.
- `facade.create_contexto_salario(request)`: Cria o contexto para renderização dos dados.
- `facade.salario_html_data`: Formata os dados em HTML.

## Código da Função

```{py3 linenums=1}
def alterar_salario_colaborador(request):
    error = facade.validar_modal_salario_colaborador(request)
    if error:
        return error

    return handle_modal_colaborador(
        request,
        facade.modal_salario_colaborador,
        facade.save_salario_colaborador,
        partial(facade.create_contexto_salario, request),
        facade.salario_html_data,
    )
```

## Exemplo de Uso

```{py3 linenums=1}
from django.test import RequestFactory

# Simula uma requisição POST com dados de alteração de salário
request = RequestFactory().post("/alterar-salario/", {"id_pessoal": 239, "data": "2025-01-01", "valor": 5000}

# Chama a função
response = alterar_salario_colaborador(request)

# Verifica a resposta
print(response)
```

