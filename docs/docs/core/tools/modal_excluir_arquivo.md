# `modal_excluir_arquivo`

Função responsável por gerar um modal HTML contendo informações sobre um arquivo, incluindo sua URL e extensão, para ser renderizado dinamicamente na interface.

## Fluxo de Execução

1. Obtém o objeto `FileUpload` correspondente ao identificador fornecido.
2. Extrai a extensão do arquivo e a armazena em `file_ext`.
3. Cria um dicionário `contexto` contendo os detalhes do arquivo:
   - Objeto `FileUpload`.
   - URL do arquivo.
   - Extensão do arquivo.
   - Identificador do arquivo.
4. Renderiza um template HTML chamado `"core/modal_excluir_arquivo.html"` usando o contexto.
5. Retorna a resposta JSON contendo o HTML renderizado.

## Parâmetros

- `id_file_upload` (`int`): Identificador único do arquivo a ser exibido.
- `request` (`HttpRequest`): Requisição HTTP necessária para a renderização do template.

## Retorno

- `JsonResponse`: Retorna um objeto JSON contendo:
  - `"modal_html"` (`str`): HTML renderizado para exibição do modal.

## Dependências

- `FileUpload.objects.get(...)`: Obtém o objeto de arquivo armazenado.
- `Path(file.uploadFile.name).suffix.lower().strip(".")`: Obtém a extensão do arquivo.
- `render_to_string(...)`: Renderiza o template HTML com base no contexto.
- `JsonResponse(...)`: Retorna a resposta formatada como JSON.

## Código da Função

```{py3 linenums="1"}
def modal_excluir_arquivo(id_file_upload, request):
    file = FileUpload.objects.get(idFileUpload=id_file_upload)
    ext = Path(file.uploadFile.name).suffix.lower().strip(".")

    contexto = {
        "file": file,
        "file_url": file.uploadFile.url,
        "file_ext": ext,
        "file_id": file.idFileUpload,
    }

    modal_html = render_to_string(
        "core/modal_excluir_arquivo.html", contexto, request=request
    )

    return JsonResponse({"modal_html": modal_html})
```

## Exemplo de Uso

```{py3 linenums="1"}
# Gera um modal de exclusão para um arquivo específico
resposta = modal_excluir_arquivo(42, request)

# Exibe a resposta JSON retornada
print(resposta.content.decode("utf-8"))
```
