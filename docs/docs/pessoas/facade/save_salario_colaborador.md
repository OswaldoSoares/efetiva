# `save_salario_colaborador`

Função responsável por salvar ou atualizar o salário de um colaborador, garantindo a integridade transacional.

## Fluxo de Execução

1. Obtém e converte os dados da requisição:
   - `data`: Data da alteração salarial.
   - `valor`: Novo valor do salário.
   - `id_pessoal`: Identificador do colaborador.
   - `id_salario`: Identificador da alteração salarial, se existente.
2. Monta um dicionário `registro` com os dados do salário.
3. Inicia uma transação atômica para garantir a integridade dos dados:
   - Se `id_salario` existir, atualiza a alteração salarial existente e exibe uma mensagem de sucesso.
   - Se `id_salario` não existir, cria um novo registro de alteração salarial com observação "AUMENTO SALARIAL".
   - Atualiza ou cria um novo registro na tabela `Salario`, garantindo que o novo salário e outros atributos sejam registrados corretamente.
4. Retorna um dicionário contendo a mensagem de sucesso correspondente.

## Parâmetros

- `request` (HttpRequest): Objeto de requisição contendo os dados enviados pelo cliente.

## Retorno

- `dict`: Retorna um dicionário com a mensagem de sucesso da operação.

## Dependências

- `transaction.atomic()`: Garante que todas as operações dentro do bloco sejam executadas de forma transacional.
- `AlteracaoSalarial.objects.filter(...).update(...)`: Atualiza um registro de alteração salarial existente.
- `AlteracaoSalarial.objects.create(...)`: Cria um novo registro de alteração salarial.
- `Salario.objects.update_or_create(...)`: Atualiza ou cria um novo registro de salário para o colaborador.
- `Decimal` do módulo `decimal` para tratar valores monetários.

## Código da Função

```{.py3 linenums="1"}
def save_salario_colaborador(request):
    data = datetime.strptime(request.POST.get("data"), "%Y-%m-%d")
    valor = float(request.POST.get("valor").replace(",", "."))
    id_pessoal = request.POST.get("id_pessoal")
    id_salario = request.POST.get("id_salario")

    registro = {
        "idPessoal_id": id_pessoal,
        "Data": data,
        "Valor": valor,
    }

    with transaction.atomic():
        if id_salario:
            AlteracaoSalarial.objects.filter(
                idAlteracaoSalarial=id_salario
            ).update(**registro)
            mensagem = "Salário alterado com sucesso"
        else:
            registro["Obs"] = "AUMENTO SALARIAL"
            AlteracaoSalarial.objects.create(**registro)
            mensagem = "Aumento salarial realizado com sucesso"

        Salario.objects.update_or_create(
            idPessoal_id=request.POST.get("id_pessoal"),
            defaults={
                "Salario": valor,
                "HorasMensais": 220,
                "ValeTransporte": Decimal("0.00"),
            },
        )

    return {"mensagem": mensagem}
```

## Exemplo de Uso

```{.py3 linenums="1"}
from django.test import RequestFactory

# Simula uma requisição POST com dados de alteração salarial
request = RequestFactory().post(
    "/salvar-salario/", {"data": "2025-01-01", "valor": "6000", "id_pessoal": "1"}
)

# Chama a função
response = save_salario_colaborador(request)

# Verifica a resposta
print(response)
```

