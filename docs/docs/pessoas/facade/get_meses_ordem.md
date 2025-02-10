# `get_meses_ordem`

Função responsável por gerar uma estrutura de ordenação personalizada para os meses do ano.

## Fluxo de Execução

1. Cria um dicionário `meses_inverso`, onde as chaves e valores do dicionário `MESES` são invertidos.
2. Retorna um objeto `Case`, contendo uma lista de condições `When`.
   - Cada condição `When` compara o campo `MesReferencia` com um dos meses disponíveis e retorna seu número correspondente.
   - Define `output_field=IntegerField()` para garantir que o retorno seja um campo inteiro.

## Retorno

- `Case`: Objeto `Case` configurado para ordenação dos meses.

## Dependências

- `MESES`: Dicionário contendo o mapeamento de nomes dos meses para seus respectivos números.
- `Case`, `When` e `IntegerField` do Django ORM.

## Código da Função

```{py3 linemums="1"}
def get_meses_ordem():
    meses_inverso = {v: k for k, v in MESES.items()}

    return Case(
        *[
            When(MesReferencia=mes, then=num)
            for mes, num in meses_inverso.items()
        ],
        output_field=IntegerField(),
    )
```

## Exemplo de Uso

```{py3 linemums="1"}
from django.db.models import F

# Exemplo de uso dentro de uma query
queryset = MinhaModel.objects.annotate(ordem_mes=get_meses_ordem()).order_by("ordem_mes")

# Verifica a ordenação
for item in queryset:
    print(item.MesReferencia, item.ordem_mes)
```
