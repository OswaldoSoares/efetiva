
# `modal_data_readmissao_colaborador`

Função responsável por gerar o modal de readmissão de um colaborador.

## Fluxo de Execução

- Obtém o `id_pessoal` da requisição, verificando se o método é `POST` ou `GET`.
- Cria uma instância do colaborador com base no `id_pessoal`, caso ele seja fornecido.
- Obtém a data atual.
- Cria o contexto contendo os dados do colaborador e a data atual formatada.
- Gera o HTML do modal utilizando `html_data.html_modal_data_readmissao_colaborador`.
- Retorna um objeto `JsonResponse` com o HTML do modal.

## Parâmetros

- `id_pessoal` (`str`): Identificador do colaborador.
- `request` (`HttpRequest`): Requisição HTTP recebida do cliente.

## Retorno

- `JsonResponse`: Retorna um dicionário contendo:
  - `"modal_html"` (`str`): HTML gerado do modal.

## Dependências

- `classes.Colaborador`
- `datetime.today`
- `html_data.html_modal_data_readmissao_colaborador`
- `JsonResponse`

## Código da Função

```{py3 linenums="1"}
def modal_data_readmissao_colaborador(id_pessoal, request):
    id_pessoal = (
        request.POST.get("id_pessoal")
        if request.method == "POST"
        else request.GET.get("id_pessoal")
    )
    colaborador = classes.Colaborador(id_pessoal) if id_pessoal else False
    hoje = datetime.today().date()
    contexto = {
        "colaborador": colaborador,
        "hoje": hoje.strftime("%Y-%m-%d"),
    }
    modal_html = html_data.html_modal_data_readmissao_colaborador(
        request, contexto
    )
    return JsonResponse({"modal_html": modal_html})
```

## Exemplo de Uso

```{py3 linenums="1"}
# Simula uma requisição para obter o modal de readmissão
resposta = modal_data_readmissao_colaborador("12345", request)

# Exibe a resposta retornada
print(resposta)
```
