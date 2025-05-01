# `excluir_arquivo`

Função responsável por excluir um arquivo previamente armazenado no sistema, garantindo que o arquivo seja removido fisicamente do servidor antes da exclusão do registro no banco de dados.

## Fluxo de Execução

1. Busca o objeto `FileUpload` pelo identificador fornecido.
2. Se o arquivo existir:
   - Obtém o caminho do arquivo e verifica se ele está presente no sistema.
   - Remove o arquivo físico do servidor.
   - Exclui o registro do banco de dados.
   - Retorna uma mensagem de sucesso.
3. Caso ocorra um erro ao excluir o arquivo, captura a exceção e retorna uma mensagem de falha.
4. Se o arquivo não for encontrado, retorna uma mensagem informando que o arquivo não existe.

## Parâmetros

- `id_file_upload` (`int`): Identificador único do arquivo a ser excluído.

## Retorno

- `dict`: Retorna um dicionário contendo:
  - `"mensagem"` (`str`): Mensagem informativa sobre o resultado da operação.

## Dependências

- `FileUpload.objects.filter(...).first()`: Obtém o objeto do arquivo armazenado.
- `os.path.exists(...)`: Verifica se o arquivo físico existe no sistema.
- `os.remove(...)`: Remove o arquivo físico do servidor.
- `file.delete()`: Exclui o registro do arquivo do banco de dados.

## Código da Função

```{py3 linenums="1"}
def excluir_arquivo(id_file_upload):
    file = FileUpload.objects.filter(idFileUpload=id_file_upload).first()
    if file:
        try:
            caminho = file.uploadFile.path
            if os.path.exists(caminho):
                os.remove(caminho)
            file.delete()
            mensagem = "Arquivo excluído com sucesso."

        # TODO: Refinar exceções específicas mais tarde
        except Exception as error:  # pylint: disable=W0703
            print(f"Erro ao excluir arquivo: {error}")
            mensagem = "Erro ao excluir o arquivo."
    else:
        mensagem = "Arquivo não encontrado."

    return {"mensagem": mensagem}
```

## Exemplo de Uso

```{py3 linenums="1"}
# Exclui um arquivo pelo seu identificador
resposta = excluir_arquivo(42)

# Exibe a resposta retornada
print(resposta)
```
