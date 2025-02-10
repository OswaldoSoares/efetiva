# `create_contexto_salario`

Função responsável por criar o contexto necessário para exibir as informações salariais de um colaborador.

## Fluxo de Execução

1. Obtém o `id_pessoal` a partir dos parâmetros da requisição (`POST` ou `GET`).
2. Obtém os dados do colaborador utilizando a classe `Colaborador`.
3. Busca todas as alterações salariais associadas ao colaborador na tabela `AlteracaoSalarial`.
4. Retorna um dicionário contendo o colaborador e sua lista de alterações salariais.

## Parâmetros

- `request` (HttpRequest): Objeto de requisição contendo os dados enviados pelo cliente.

## Retorno

- `dict`: Dicionário contendo as informações do colaborador e suas alterações salariais.

## Dependências

- `classes.Colaborador(id_pessoal)`: Obtém os dados do colaborador.
- `AlteracaoSalarial.objects.filter(idPessoal=id_pessoal)`: Busca as alterações salariais do colaborador.

## Código da Função

```{.py3 linenums="1"}
def create_contexto_salario(request):
    id_pessoal = request.POST.get("id_pessoal") or request.GET.get(
        "id_pessoal"
    )
    colaborador = classes.Colaborador(id_pessoal)
    salarios = AlteracaoSalarial.objects.filter(idPessoal=id_pessoal)
    return {"colaborador": colaborador, "salarios": salarios}
```

## Exemplo de Uso

```{.py3 linenums="1"}
from django.test import RequestFactory

# Simula uma requisição GET com um ID de colaborador
request = RequestFactory().get("/contexto-salario/", {"id_pessoal": "1"})

# Chama a função
contexto = create_contexto_salario(request)

# Verifica os dados retornados
print(contexto)
```

