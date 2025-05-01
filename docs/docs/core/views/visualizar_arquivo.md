# `visualizar_arquivo`

Função responsável por buscar e retornar um arquivo armazenado no sistema, garantindo que ele seja entregue na resposta com o tipo de conteúdo apropriado.

## Fluxo de Execução

1. Obtém o objeto `FileUpload` correspondente ao identificador fornecido.
2. Extrai o caminho do arquivo armazenado.
3. Determina o tipo de conteúdo do arquivo usando `mimetypes.guess_type(...)`.
4. Retorna o arquivo como uma resposta utilizando `FileResponse(...)`.
5. Em caso de erro durante a recuperação do arquivo, lança uma exceção `Http404`.

## Parâmetros

- `request` (`HttpRequest`): Requisição HTTP recebida do cliente.
- `id_file_upload` (`int`): Identificador único do arquivo a ser visualizado.

## Retorno

- `FileResponse`: Retorna o arquivo correspondente com o tipo de conteúdo adequado.
- `Http404`: Em caso de erro na recuperação do arquivo.

## Dependências

- `FileUpload.objects.get(...)`: Obtém o objeto `FileUpload` pelo identificador.
- `mimetypes.guess_type(...)`: Determina o tipo de conteúdo do arquivo.
- `FileResponse(...)`: Retorna o arquivo como resposta HTTP.
- `Http404(...)`: Lança um erro caso o arquivo não seja encontrado ou haja falha ao carregá-lo.

## Código da Função

```{py3 linenums="1"}
@xframe_options_exempt
def visualizar_arquivo(request, id_file_upload):
    try:
        arquivo = FileUpload.objects.get(idFileUpload=id_file_upload)
        file_path = arquivo.uploadFile.path
        content_type, _ = mimetypes.guess_type(file_path)

        return FileResponse(open(file_path, "rb"), content_type=content_type)

    except Exception as error:
        raise Http404(f"Erro ao carregar arquivo: {error}")
```

## Exemplo de Uso

```{py3 linenums="1"}
# Chama a função para visualizar um arquivo específico
resposta = visualizar_arquivo(request, 42)

# Exibe a resposta retornada
print(resposta)
```
