# `validar_modal_data_readmissao_colaborador`

Função responsável por validar os dados de readmissão de um colaborador.

## Fluxo de Execução

- Verifica se a requisição é do tipo `POST`, caso contrário, a função não é executada.
- Obtém os valores `id_pessoal` e `readmissao` da requisição.
- Converte `readmissao` para um objeto `date`.
- Recupera os dados do colaborador com base no `id_pessoal`.
- Obtém a data de demissão do colaborador e o último dia do mês da demissão.
- Valida se a data de readmissão não é posterior à data atual.
- Valida se a data de readmissão é posterior ao mês de demissão.
- Retorna `False` caso os dados sejam válidos ou um erro em formato JSON caso contrário.

## Parâmetros

- `request` (`HttpRequest`): Requisição HTTP recebida do cliente.

## Retorno

- `JsonResponse`: Retorna um erro em caso de validação falha.
- `False`: Retorna `False` caso os dados sejam válidos.

## Dependências

- `request.POST.get(...)`: Obtém valores enviados na requisição `POST`.
- `datetime.strptime(...)`: Converte string para `date`.
- `datetime.today().date()`: Obtém a data atual.
- `classes.Colaborador`
- `primeiro_e_ultimo_dia_do_mes`
- `JsonResponse`

## Código da Função

```{py3 linenums="1"}
def validar_modal_data_readmissao_colaborador(request):
    if request.method != "POST":
        return False

    id_pessoal = request.POST.get("id_pessoal")
    readmissao_str = request.POST.get("readmissao")

    data_readmissao = datetime.strptime(readmissao_str, "%Y-%m-%d").date()
    hoje = datetime.today().date()

    colaborador = classes.Colaborador(id_pessoal)
    data_demissao = colaborador.dados_profissionais.data_demissao
    _, ultimo_dia_mes_demissao = primeiro_e_ultimo_dia_do_mes(
        data_demissao.month, data_demissao.year
    )

    if data_readmissao > hoje:
        return JsonResponse(
            {
                "error": "A data de readmissão não pode ser posterior ao dia de hoje."
            },
            status=400,
        )

    if data_readmissao <= ultimo_dia_mes_demissao.date():
        return JsonResponse(
            {
                "error": "A data de readmissão deve ser posterior ao mês de demissão."
            },
            status=400,
        )

    return False
```

## Exemplo de Uso

```{py3 linenums="1"}
# Simula uma requisição para validar a readmissão de um colaborador
resposta = validar_modal_data_readmissao_colaborador(request)

# Exibe a resposta retornada
print(resposta)
```
