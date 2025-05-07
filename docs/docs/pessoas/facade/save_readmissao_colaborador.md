# `save_readmissao_colaborador`

Função responsável por salvar a readmissão de um colaborador.

## Fluxo de Execução

- Obtém os parâmetros `id_pessoal` e `readmissao` da requisição.
- Verifica se os parâmetros são válidos.
- Converte a string `readmissao` para um objeto `datetime`.
- Recupera o colaborador no banco de dados.
- Cria um registro de readmissão no banco de dados.
- Atualiza os dados de admissão e demissão do colaborador.
- Retorna uma mensagem de sucesso.

## Parâmetros

- `request` (`HttpRequest`): Requisição HTTP recebida do cliente.

## Retorno

- `dict`: Retorna um dicionário contendo:
  - `"mensagem"` (`str`): Mensagem informando o resultado da operação.

## Dependências

- `datetime.strptime`
- `Pessoal.objects.get`
- `Readmissao.objects.create`

## Código da Função

```{py3 linenums="1"}
def save_readmissao_colaborador(request):
    id_pessoal = request.POST.get("id_pessoal")
    data_readmissao_str = request.POST.get("readmissao")

    if not id_pessoal or not data_readmissao_str:
        return {"mensagem": "Parâmetros inválidos"}

    try:
        data_readmissao = datetime.strptime(data_readmissao_str, "%Y-%m-%d")
    except ValueError:
        return {"mensagem": "Formato de data inválido"}

    colaborador = Pessoal.objects.get(idPessoal=id_pessoal)

    Readmissao.objects.create(
        DataAdmissao=colaborador.DataAdmissao,
        DataDemissao=colaborador.DataDemissao,
        DataReadmissao=data_readmissao,
        idPessoal=colaborador,
    )

    colaborador.DataAdmissao = data_readmissao
    colaborador.DataDemissao = None
    colaborador.save()

    return {"mensagem": "Colaborador Readmitido"}
```

## Exemplo de Uso
```{py3 linenums="1"}
# Simula uma requisição para salvar a readmissão de um colaborador
resposta = save_readmissao_colaborador(request)

# Exibe a resposta retornada
print(resposta)
```
