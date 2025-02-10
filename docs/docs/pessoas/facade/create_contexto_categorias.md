# `create_contexto_categorias`

Gera um dicionário contendo as categorias do colaborador.

## Descrição

Esta função retorna um dicionário com uma chave `categorias`, cujo valor é uma lista de categorias associadas ao colaborador.

## Lógica da Função

1. Obtém a lista de categorias do colaborador a partir da variável `categorias_colaborador`.
2. Retorna um dicionário com essa lista associada à chave `categorias`.

## Parâmetros

A função não recebe parâmetros.

## Retorno

- `dict`: Um dicionário contendo a lista de categorias.
  - **Exemplo de retorno:**
    ```python
    {
        "categorias": ["Mensalista Ativos", "Avulsos Ativos", "Inativos"]
    }
    ```

## Dependências

- `categorias_colaborador`: Variável que armazena a lista de categorias associadas ao colaborador.

## Código da Função

```{.py3 linenums="1"}
def create_contexto_categoria():
    return {"categorias": categorias_colaborador}
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="8-10"}
# Executar a função
contexto = create_contexto_categoria()

# Verificar o resultado
print(contexto)

# Resultado esperado (exemplo fictício):
{
    "categorias": ["Mensalista Ativos", "Avulsos Ativos", "Inativos"]
}
```
