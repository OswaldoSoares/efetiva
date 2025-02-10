# `salario_html_data`

Função responsável por gerar os dados HTML para exibição das informações salariais de um colaborador.

## Fluxo de Execução

1. Define a lista de funções HTML a serem utilizadas:
   - `html_data.html_card_salario_colaborador`: Responsável por gerar o card de salário do colaborador.
2. Chama a função `gerar_data_html`, passando:
   - A lista de funções HTML.
   - O objeto `request` contendo os dados da requisição.
   - O `contexto` com as informações do colaborador e seus salários.
   - Um dicionário vazio `{}` como argumento adicional.
3. Retorna o HTML gerado.

## Parâmetros

- `request` (HttpRequest): Objeto de requisição contendo os dados enviados pelo cliente.
- `contexto` (dict): Dicionário contendo as informações do colaborador e suas alterações salariais.

## Retorno

- `str`: HTML gerado com os dados do salário do colaborador.

## Dependências

- `html_data.html_card_salario_colaborador`: Função responsável por renderizar o card de salário do colaborador.
- `gerar_data_html(...)`: Função que processa e gera os dados HTML com base nas funções fornecidas.

## Código da Função

```{.py3 linenums="1"}
def salario_html_data(request, contexto):
    html_functions = [
        html_data.html_card_salario_colaborador,
    ]
    return gerar_data_html(html_functions, request, contexto, {})
```

## Exemplo de Uso

```{.py3 linenums="1"}
from django.test import RequestFactory

# Simula uma requisição GET para obter os dados salariais em HTML
request = RequestFactory().get("/salario-html/")
contexto = {"colaborador": "João", "salarios": [5000, 5500]}

# Chama a função
html = salario_html_data(request, contexto)

# Verifica o HTML gerado
print(html)
```

