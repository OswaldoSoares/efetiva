# `injetar_parametro_no_request_post`

Função responsável por extrair parâmetros de uma URL presente no corpo da requisição `POST` e injetá-los no próprio `request.POST`.

## Fluxo de Execução

1. Obtém a string da URL a partir do campo `url_field` da requisição `POST`.
2. Caso a URL esteja presente:
   - Analisa a URL e extrai os parâmetros de consulta.
   - Copia os dados do `request.POST` para um novo objeto `new_post`.
   - Itera sobre os parâmetros extraídos e os adiciona ao `new_post`, exceto `id_file_upload`.
   - Remove o campo `url_field` do `new_post`.
   - Mantém os arquivos enviados originalmente (`request.FILES`).
3. Atualiza o objeto de requisição para refletir as mudanças.
4. Retorna o `request` modificado.

## Parâmetros

- `request` (`HttpRequest`): Requisição HTTP contendo os dados enviados pelo cliente.
- `url_field` (`str`, opcional): Nome do campo em `request.POST` que contém a URL (padrão: `"request_passado"`).

## Retorno

- `HttpRequest`: Retorna o objeto `request` modificado com os parâmetros da URL injetados no corpo da requisição.

## Dependências

- `urlparse(...)`: Analisa a URL e extrai componentes individuais.
- `parse_qs(...)`: Converte parâmetros de consulta da URL em um dicionário.
- `request.POST.copy()`: Cria uma cópia modificável dos parâmetros `POST`.

## Código da Função

```{py3 linenums="1"}
def injetar_parametro_no_request_post(request, url_field="request_passado"):
    url_string = request.POST.get(url_field)

    if url_string:
        parsed_url = urlparse(url_string)
        query_params = parse_qs(parsed_url.query)

        new_post = request.POST.copy()

        for key, value in query_params.items():
            if not key == "id_file_upload":
                if value:
                    new_post[key] = value[0]

        del new_post[url_field]

        request._post = new_post
        request._files = request.FILES  # mantém arquivos se houver

    return request
```

## Exemplo de Uso

```{py3 linenums="1"}
# Suponha que temos uma requisição com uma URL contendo parâmetros
request.POST["request_passado"] = "https://exemplo.com/?id_pessoal=123&mes=4&ano=2025"

# Chama a função para modificar a requisição
request_modificado = injetar_parametro_no_request_post(request)

# Exibe os novos parâmetros injetados
print(request_modificado.POST)
```
