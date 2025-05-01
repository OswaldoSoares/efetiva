# `excluir_arquivo_contra_cheque`

Função responsável por excluir um arquivo associado a um contracheque, garantindo que a operação seja executada corretamente com um contexto atualizado.

## Fluxo de Execução

1. Obtém o identificador do arquivo a partir da requisição `POST`.
2. Se a requisição for do tipo `POST`:
   - Injeta parâmetros adicionais na requisição usando `injetar_parametro_no_request_post(...)`.
   - Exclui o arquivo utilizando `excluir_arquivo(...)`.
   - Obtém o contexto atualizado do contracheque através de `facade.create_contexto_contra_cheque(...)`.
   - Atualiza o contexto com a mensagem de retorno da exclusão.
   - Gera os dados HTML do contracheque para exibição.
3. Caso contrário, exibe um modal de confirmação para exclusão do arquivo.
4. Retorna os dados processados.

## Parâmetros

- `request` (`HttpRequest`): Requisição HTTP recebida do cliente.

## Retorno

- `dict`: Retorna um dicionário contendo os dados do contracheque atualizados ou um modal de confirmação.

## Dependências

- `get_request_data(...)`: Obtém o identificador do arquivo enviado na requisição.
- `injetar_parametro_no_request_post(...)`: Injeta parâmetros adicionais na requisição.
- `excluir_arquivo(...)`: Executa a exclusão do arquivo.
- `facade.create_contexto_contra_cheque(...)`: Obtém o contexto atualizado do contracheque.
- `facade.contra_cheque_html_data(...)`: Gera os dados HTML do contracheque.
- `modal_excluir_arquivo(...)`: Exibe um modal de confirmação antes da exclusão.

## Código da Função

```{py3 linenums="1"}
def excluir_arquivo_contra_cheque(request):
    id_file_upload = get_request_data(request, "id_file_upload")
    if request.method == "POST":
        request_injetado = injetar_parametro_no_request_post(request)
        mensagem = excluir_arquivo(id_file_upload)

        contexto = facade.create_contexto_contra_cheque(request_injetado)
        contexto.update(mensagem)

        data = facade.contra_cheque_html_data(request, contexto)
    else:
        data = modal_excluir_arquivo(id_file_upload, request)

    return data
```

## Exemplo de Uso

```{py3 linenums="1"}
# Simula uma requisição POST para exclusão de um arquivo do contracheque
resposta = excluir_arquivo_contra_cheque(request)

# Exibe a resposta retornada
print(resposta)
```
