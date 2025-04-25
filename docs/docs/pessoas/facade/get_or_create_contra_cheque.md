
# `get_or_create_contra_cheque`

Função responsável por obter ou criar um objeto de contracheque para um colaborador, com base na referência de mês, ano e descrição fornecida.

## Fluxo de Execução

1. Recebe os parâmetros `mes`, `ano`, `descricao` e `id_pessoal`.
2. Busca um objeto `ContraCheque` existente com os mesmos parâmetros ou cria um novo.
3. Define valores padrão caso o objeto seja criado.
4. Retorna o objeto `ContraCheque`.

## Parâmetros

- `mes` (`str`): Mês de referência do contracheque.
- `ano` (`str`): Ano de referência do contracheque.
- `descricao` (`str`): Descrição do contracheque.
- `id_pessoal` (`int`): Identificador único do colaborador.

## Retorno

- `tuple`: Retorna uma tupla com dois elementos:
  - `ContraCheque` (`model`): Objeto do modelo `ContraCheque`.
  - `bool`: Indica se o objeto foi criado (`True`) ou encontrado (`False`).

## Dependências

- `ContraCheque.objects.get_or_create(...)`: Método do Django ORM para obter ou criar um objeto no banco de dados.

## Código da Função

```{py3 linenums="1"}
def get_or_create_contra_cheque(mes, ano, descricao, id_pessoal):
    return ContraCheque.objects.get_or_create(
        Descricao=descricao,
        AnoReferencia=ano,
        MesReferencia=mes,
        idPessoal_id=id_pessoal,
        defaults={
            "Valor": 0.00,
            "Pago": False,
            "Obs": "",
        },
    )
```

## Exemplo de Uso

```{py3 linenums="1"}
# Obtém ou cria um contracheque para o colaborador 123 referente a ABRIL de 2025
contra_cheque, criado = get_or_create_contra_cheque(
    "ABRIL", "2025", "ADIANTAMENTO", 123
)

# Exibe o resultado
print(f"ContraCheque criado? {criado}")
print(contra_cheque)
```
