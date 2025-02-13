# `verificar_salario_colaborador`

Verifica e registra a alteração salarial de um colaborador.

## Descrição

Esta função busca todas as alterações salariais registradas para um colaborador. Caso não haja registros, ela obtém o salário inicial do colaborador e cria um novo registro na tabela de alteração salarial com a data de admissão e uma observação indicando que é o salário inicial.

## Lógica da Função

1. Busca ou cria o salário do colaborador na tabela `Salario` utilizando `get_or_create()`.
   - Se o registro não existir, é criado com valores padrão (`Salario` igual a `0.00`, `HorasMensais` igual a `220` e `ValeTransporte` igual a `0.00`).
2. Utiliza `get_or_create()` para garantir que exista um registro na tabela `AlteracaoSalarial` com a data de admissão do colaborador.
3. Se o registro não existir, ele é criado com o salário inicial.
4. Retorna um `QuerySet` contendo todas as alterações salariais do colaborador.

## Parâmetros

- `colaborador` (*objeto*): Instância do colaborador cujo salário será verificado.

## Retorno

- `QuerySet`: Um conjunto de objetos representando todas as alterações salariais do colaborador.

  **Exemplo de retorno:**
  ```{.py3 linenums="1"}
  <QuerySet [
      <AlteracaoSalarial: idPessoal=123, Data='2024-01-01', Valor=3000, Obs='SALÁRIO INICIAL'>
  ]>
  ```

## Dependências

- `Salario`: Modelo que armazena o salário base do colaborador.
- `AlteracaoSalarial`: Modelo que registra alterações salariais dos colaboradores.

## Código da Função

```{.py3 linenums="1"}
def verificar_salario_colaborador(colaborador):
    salario, created = Salario.objects.get_or_create(
        idPessoal_id=colaborador.id_pessoal,
        defaults={
            "Salario": Decimal("0.00"),
            "HorasMensais": 220,
            "ValeTransporte": Decimal("0.00"),
        },
    )

    AlteracaoSalarial.objects.get_or_create(
        idPessoal=colaborador.id_pessoal,
        Data=colaborador.admissao,
        defaults={"Valor": salario.Salario, "Obs": "SALÁRIO INICIAL"},
    )

    return AlteracaoSalarial.objects.filter(idPessoal=colaborador.id_pessoal)
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="8-10"}
# Supondo que temos um objeto colaborador
contexto = verificar_salario_colaborador(colaborador)

# Verificar o resultado
print(contexto)

# Resultado esperado (exemplo fictício):
<QuerySet [
    <AlteracaoSalarial: idPessoal=123, Data='2024-01-01', Valor=3000, Obs='SALÁRIO INICIAL'>
]>
```

