# `modal_salario_colaborador`

Função responsável por gerar o modal de salário do colaborador, retornando um HTML formatado com os dados necessários.

## Fluxo de Execução

1. Obtém os parâmetros `id_pessoal` e `id_salario` da requisição (`POST` ou `GET`).
2. Busca o colaborador correspondente a `id_pessoal`, se fornecido.
3. Obtém a data atual (`hoje`).
4. Obtém o salário atual do colaborador.
5. Busca uma alteração salarial existente, caso `id_salario` tenha sido fornecido.
6. Monta o contexto com os dados do colaborador e da alteração salarial.
7. Renderiza o modal HTML usando `html_data.html_modal_salario_colaborador`.
8. Retorna um `JsonResponse` contendo o HTML do modal.

## Parâmetros

- `id_salario` (int ou None): Identificador da alteração salarial, se aplicável.
- `request` (HttpRequest): Objeto de requisição contendo os dados enviados pelo cliente.

## Retorno

- `JsonResponse`: Retorna um JSON contendo o HTML do modal formatado.

## Dependências

- `classes.Colaborador(id_pessoal)`: Obtém os dados do colaborador.
- `AlteracaoSalarial.objects.filter(idAlteracaoSalarial=id_salario).first()`: Busca a alteração salarial existente.
- `html_data.html_modal_salario_colaborador(request, contexto)`: Renderiza o modal HTML com os dados do contexto.

## Código da Função

```{py3 linenums="1"}
def modal_salario_colaborador(id_salario, request):
    id_pessoal = request.POST.get("id_pessoal") or request.GET.get(
        "id_pessoal"
    )
    id_salario = request.POST.get("id_salario") or request.GET.get(
        "id_salario"
    )
    colaborador = classes.Colaborador(id_pessoal) if id_pessoal else False
    hoje = datetime.today().date()
    salario = colaborador.salarios.salarios.Salario
    alteracao_salarial = (
        AlteracaoSalarial.objects.filter(
            idAlteracaoSalarial=id_salario
        ).first()
        if id_salario
        else None
    )

    contexto = {
        "colaborador": colaborador,
        "hoje": hoje.strftime("%Y-%m-%d"),
        "salario": salario,
        "alteracao_salarial": alteracao_salarial,
    }
    modal_html = html_data.html_modal_salario_colaborador(request, contexto)
    return JsonResponse({"modal_html": modal_html})
```

## Exemplo de Uso

```{py3 linenums="1"}
from django.test import RequestFactory

# Simula uma requisição GET com um ID de colaborador
request = RequestFactory().get("/modal-salario/", {"id_pessoal": 1})

# Chama a função
response = modal_salario_colaborador(None, request)

# Verifica a resposta
print(response.json())
```

