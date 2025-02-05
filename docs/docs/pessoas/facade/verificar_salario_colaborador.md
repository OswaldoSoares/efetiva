# `verificar_salario_colaborador`

Verifica e registra a alteração salarial de um colaborador.

## Descrição

Esta função busca todas as alterações salariais registradas para um colaborador. Caso não haja registros, ela obtém o salário inicial do colaborador e cria um novo registro na tabela de alteração salarial com a data de admissão e uma observação indicando que é o salário inicial.

## Lógica da Função

1. Busca o salário do colaborador na tabela `Salario`.
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
def verifica_salario_colaborador(colaborador):
    salario = Salario.objects.filter(idPessoal=colaborador.id_pessoal).first()
    
    AlteracaoSalarial.objects.get_or_create(
        idPessoal=colaborador.id_pessoal,
        Data=colaborador.admissao,
        defaults={"Valor": salario.Salario if salario else 0, "Obs": "SALÁRIO INICIAL"},
    )

    return AlteracaoSalarial.objects.filter(idPessoal=colaborador.id_pessoal)
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="8-10"}
# Supondo que temos um objeto colaborador
contexto = verifica_salario_colaborador(colaborador)

# Verificar o resultado
print(contexto)

# Resultado esperado (exemplo fictício):
<QuerySet [
    <AlteracaoSalarial: idPessoal=123, Data='2024-01-01', Valor=3000, Obs='SALÁRIO INICIAL'>
]>
```

