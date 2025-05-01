# `upload_contra_cheque`

Função responsável por processar o upload de um arquivo de contracheque, associando-o a um identificador específico e atualizando o contexto do contracheque.

## Fluxo de Execução

1. Obtém o identificador do contracheque a partir do campo `id_contra_cheque` na requisição `POST`.
2. Define o nome do arquivo utilizando o identificador do contracheque.
3. Executa a função `upload_de_arquivo(...)` para processar o envio do arquivo.
4. Obtém o contexto do contracheque através de `facade.create_contexto_contra_cheque(...)`.
5. Atualiza o contexto do contracheque com a mensagem de retorno do upload.
6. Gera os dados HTML do contracheque para exibição.
7. Retorna os dados formatados para interface.

## Parâmetros

- `request` (`HttpRequest`): Requisição HTTP contendo os dados enviados pelo cliente.

## Retorno

- `dict`: Retorna um dicionário contendo os dados do contracheque atualizados.

## Dependências

- `upload_de_arquivo(...)`: Executa o processamento e armazenamento do arquivo.
- `facade.create_contexto_contra_cheque(...)`: Obtém o contexto do contracheque.
- `facade.contra_cheque_html_data(...)`: Gera os dados HTML do contracheque.

## Código da Função

```{py3 linenums="1"}
def upload_contra_cheque(request):
    id_contra_cheque = request.POST.get("id_contra_cheque")
    nome_arquivo = f"Contra-Cheque_-_{str(id_contra_cheque).zfill(6)}"
    mensagem = upload_de_arquivo(request, nome_arquivo, 5)

    contexto = facade.create_contexto_contra_cheque(request)
    contexto.update(mensagem)

    data = facade.contra_cheque_html_data(request, contexto)

    return data
```

## Exemplo de Uso

```{py3 linenums="1"}
# Simula uma requisição POST para upload de contracheque
resposta = upload_contra_cheque(request)

# Exibe a resposta retornada
print(resposta)
```
