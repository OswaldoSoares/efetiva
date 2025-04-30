# `upload_de_arquivo`

Função responsável por validar, processar e salvar um arquivo enviado via requisição HTTP, garantindo que o tipo e tamanho estejam dentro dos limites permitidos.

## Fluxo de Execução

1. Verifica se a requisição é do tipo `POST`, caso contrário, retorna erro.
2. Confirma se um arquivo foi enviado na requisição, caso contrário, retorna erro.
3. Obtém o arquivo enviado e valida sua extensão (`pdf`, `jpg` ou `png`).
4. Verifica o tamanho máximo permitido e retorna erro se o arquivo for maior que o limite.
5. Ajusta o nome do arquivo de acordo com o nome fornecido.
6. Busca um objeto `FileUpload` existente com a mesma descrição:
   - Se encontrado, remove o arquivo anterior caso exista.
   - Caso contrário, cria um novo objeto `FileUpload`.
7. Salva o arquivo e retorna uma resposta de sucesso.
8. Em caso de erro durante o salvamento, captura a exceção e retorna uma mensagem de falha.

## Parâmetros

- `request` (`HttpRequest`): Requisição HTTP contendo o arquivo enviado pelo usuário.
- `nome_arquivo` (`str`): Nome do arquivo a ser salvo.
- `max_size_mb` (`int`): Tamanho máximo permitido do arquivo em megabytes.

## Retorno

- `dict`: Retorna um dicionário contendo:
  - `"mensagem"` (`str`): Mensagem informativa sobre o resultado da operação.

## Dependências

- `request.FILES`: Objeto contendo os arquivos enviados na requisição.
- `os.path.isfile(...)`: Verifica se o arquivo anterior existe.
- `os.remove(...)`: Remove o arquivo anterior caso exista.
- `FileUpload.objects.filter(...).first()`: Busca um objeto `FileUpload` existente.
- `FileUpload.objects.create(...)`: Cria um novo objeto `FileUpload`.

## Código da Função

```{py3 linenums="1"}
def upload_de_arquivo(request, nome_arquivo, max_size_mb):
    if request.method != "POST":
        return {"mensagem": "Método inválido."}

    if not request.FILES:
        return {"mensagem": "Arquivo não selecionado."}

    file_uploaded = request.FILES["arquivo"]
    ext_file = file_uploaded.name.split(".")[-1].lower()

    if ext_file not in ["pdf", "jpg", "png"]:
        return {
            "mensagem": "Tipo de arquivo não permitido. Permitidos: pdf, jpg e png",
        }

    max_file_size = max_size_mb * 1024 * 1024
    if file_uploaded.size > max_file_size:
        return {
            "mensagem": f"Arquivo muito grande. O limite é {max_size_mb}MB.",
        }

    descricao = nome_arquivo.rsplit(".", 1)[0]
    name_file = f"{descricao}.{ext_file}"
    file_uploaded.name = name_file

    try:
        obj = FileUpload.objects.filter(DescricaoUpload=descricao).first()

        if obj:
            if obj.uploadFile and os.path.isfile(obj.uploadFile.path):
                os.remove(obj.uploadFile.path)
        else:
            obj = FileUpload()

        obj.DescricaoUpload = descricao
        obj.uploadFile = file_uploaded
        obj.save()

        return {"mensagem": "Arquivo enviado ao servidor com sucesso"}

    # TODO: Refinar exceções específicas mais tarde
    except Exception as error:  # pylint: disable=W0703
        print(f"Erro ao salvar: {error}")

        return {"mensagem": "Falha ao salvar o arquivo, tente novamente"}
```

## Exemplo de Uso

```{py3 linenums="1"}
from django.test import RequestFactory

# Simula uma requisição POST com um arquivo
request = RequestFactory().post("/upload/", {
    "arquivo": open("documento.pdf", "rb"),
})

# Chama a função com um limite de 5MB
resposta = upload_de_arquivo(request, "documento.pdf", 5)

# Exibe a resposta retornada
print(resposta)
```
