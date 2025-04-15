# `save_salario_colaborador`

Função responsável por salvar ou atualizar o salário de um colaborador e registrar a respectiva alteração salarial, garantindo a integridade das informações.

## Fluxo de Execução

1. Obtém e converte os dados da requisição:
   - `data`: Data da alteração salarial.
   - `valor`: Novo valor do salário (com vírgula convertida para ponto).
   - `id_pessoal`: Identificador do colaborador.
   - `id_salario`: Identificador da alteração salarial, se existente.
2. Busca ou cria o salário do colaborador utilizando `get_or_create()`:
   - Se o registro não existir, cria um novo com valores padrão (`Salario` igual a `0.00`, `HorasMensais` igual a `220` e `ValeTransporte` igual a `0.00`).
3. Se o salário já existir e `id_salario` estiver presente, atualiza o valor do salário.
4. Se `id_salario` estiver presente:
   - Atualiza o valor da alteração salarial correspondente.
   - Retorna a mensagem **"Salário alterado com sucesso"**.
5. Caso contrário:
   - Cria uma nova entrada na tabela `AlteracaoSalarial` com a observação "SALÁRIO INICIAL".
   - Retorna a mensagem **"Aumento salarial realizado com sucesso"**.

## Parâmetros

- `request` (`HttpRequest`): Objeto de requisição contendo os dados enviados pelo cliente.

## Retorno

- `dict`: Retorna um dicionário com a mensagem de sucesso da operação.

## Dependências

- `Salario.objects.get_or_create(...)`: Obtém ou cria o salário do colaborador.
- `Salario.objects.filter(...).update(...)`: Atualiza o valor do salário existente.
- `AlteracaoSalarial.objects.create(...)`: Cria um novo registro de alteração salarial.
- `AlteracaoSalarial.objects.filter(...).update(...)`: Atualiza um registro de alteração salarial existente.
- `Decimal` do módulo `decimal` para tratar valores monetários.
- `datetime.strptime` para converter a data.

## Código da Função

```{py3 linenums="1"}
def save_salario_colaborador(request):
    date = datetime.strptime(request.POST.get("data"), "%Y-%m-%d")
    valor = float(request.POST.get("valor").replace(",", "."))
    id_pessoal = request.POST.get("id_pessoal")
    id_salario = request.POST.get("id_salario")

    salario, created = Salario.objects.get_or_create(
        idPessoal_id=id_pessoal,
        defaults={
            "Salario": Decimal("0.00"),
            "HorasMensais": 220,
            "ValeTransporte": Decimal("0.00"),
        },
    )

    if not created and id_salario:
        Salario.objects.filter(idPessoal_id=id_pessoal).update(Salario=valor)

    if id_salario:
        AlteracaoSalarial.objects.filter(
            idAlteracaoSalarial=id_salario
        ).update(Valor=valor)
        mensagem = "Salário alterado com sucesso"
    else:
        AlteracaoSalarial.objects.create(
            Data=data,
            Valor=valor,
            Obs="SALÁRIO INICIAL",
            idPessoal_id=id_pessoal,
        )
        mensagem = "Aumento salarial realizado com sucesso"

    return {"mensagem": mensagem}
```

## Exemplo de Uso

```{py3 linenums="1"}
from django.test import RequestFactory

# Simula uma requisição POST com dados de alteração salarial
request = RequestFactory().post(
    "/salvar-salario/",
    {"data": "2025-01-01", "valor": "6000", "id_pessoal": "1"}
)

# Chama a função
response = save_salario_colaborador(request)

# Verifica a resposta
print(response)
```
