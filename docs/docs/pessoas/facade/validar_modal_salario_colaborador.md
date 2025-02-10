# `validar_modal_salario_colaborador`

Função responsável por validar os dados enviados para alteração salarial de um colaborador.

## Fluxo de Execução

1. Verifica se a requisição é do tipo `POST`.
2. Obtém e converte os dados da requisição:
   - `data`: Data da alteração salarial.
   - `valor`: Novo valor do salário.
   - `id_pessoal`: Identificador do colaborador.
   - `id_salario`: Identificador da alteração salarial, se existente.
3. Caso não exista um `id_salario`, busca a última alteração salarial do colaborador.
   - Se a data informada for menor ou igual à última alteração, retorna um erro.
   - Obtém a possível data do próximo pagamento via [`verificar_ultimo_pagamento`](./documentacao_verificar_ultimo_pagamento.md) e valida se a data informada é válida.
4. Obtém o salário atual do colaborador:
   - Se o novo valor for menor ou igual ao salário atual, retorna um erro.
   - Se o novo valor for menor ou igual a zero, retorna um erro.
5. Caso todas as validações sejam atendidas, a função segue normalmente.

## Parâmetros

- `request` (HttpRequest): Objeto de requisição contendo os dados enviados pelo cliente.

## Retorno

- `JsonResponse`: Retorna uma resposta JSON contendo erros, caso alguma validação falhe, com status `400`. Caso contrário, permite a continuidade do processo.

## Dependências

- [`verificar_ultimo_pagamento`](./verificar_ultimo_pagamento.md): Obtém a data do último pagamento do colaborador.
- `AlteracaoSalarial.objects.filter(...)`: Consulta a base de dados para verificar a última alteração salarial.
- `classes.Colaborador(id_pessoal)`: Obtém os dados do colaborador.
- `Decimal` do módulo `decimal` para tratar valores monetários.

## Código da Função

```{.py3 linenums="1"}
def validar_modal_salario_colaborador(request):
    if request.method == "POST":
        data = datetime.strptime(request.POST.get("data"), "%Y-%m-%d").date()
        valor = float(request.POST.get("valor").replace(",", "."))
        id_pessoal = request.POST.get("id_pessoal")
        id_salario = request.POST.get("id_salario")

        if not id_salario:
            ultima_alteracao = (
                AlteracaoSalarial.objects.filter(idPessoal=id_pessoal)
                .order_by("-Data")
                .first()
            )
            if ultima_alteracao and data <= ultima_alteracao.Data:
                msg = "A data tem que ser maior que a última alteração"
                data_str = datetime.strftime(ultima_alteracao.Data, "%d/%m/%Y")

                return JsonResponse(
                    {"error": f"{msg} - {data_str}"}, status=400
                )

            data_possivel = verificar_ultimo_pagamento(id_pessoal)
            if data_possivel and data < data_possivel:
                msg = "O mês tem que ser maior que do último pagamento"
                mes_ano = (
                    f"{MESES[data_possivel.month -1]}/{data_possivel.year}"
                )

                return JsonResponse(
                    {"error": f"{msg} - {mes_ano}"}, status=400
                )

        colaborador = classes.Colaborador(id_pessoal)
        salario = (
            colaborador.salarios.salarios.Salario
            if colaborador.salarios.salarios
            else Decimal(0.00)
        )
        if valor <= salario:
            msg = "O valor tem que ser maior que o salário atual"

            return JsonResponse(
                {"error": f"{msg} - R$ {salario}"},
                status=400,
            )

        if valor <= 0:
            return JsonResponse(
                {"error": "O Valor do vale tem que ser maior que R$ 0,00."},
                status=400,
            )
```

## Exemplo de Uso

```{.py3 linenums="1"}
from django.test import RequestFactory

# Simula uma requisição POST com dados de alteração salarial
request = RequestFactory().post(
    "/validar-salario/", {"data": "2025-01-01", "valor": "5500", "id_pessoal": "1"}
)

# Chama a função
response = validar_modal_salario_colaborador(request)

# Verifica a resposta
print(response.json())
```
