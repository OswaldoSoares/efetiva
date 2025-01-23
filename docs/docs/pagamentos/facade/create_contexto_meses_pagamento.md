# `create_contexto_meses_pagamento`

Gera um dicionário contendo os nomes dos últimos 6 meses no formato "Mês/Ano" (ex.: Janeiro/2023).

## Descrição

Esta função configura a localidade para o idioma português do Brasil (`pt_BR.UTF-8`) e utiliza a data atual para calcular os nomes dos últimos seis meses no formato "Mês/Ano". O resultado é retornado como um dicionário, onde a chave é `meses` e o valor é uma lista com os nomes formatados.

## Lógica da Função

1. Define a localidade do sistema para `pt_BR.UTF-8`, garantindo que os meses sejam formatados no idioma português.
2. Obtém a data atual utilizando `datetime.datetime.today()`.
3. Calcula os últimos 6 meses a partir da data atual, usando `relativedelta` do módulo `dateutil`.
4. Formata os meses no formato "Mês/Ano" utilizando o método `strftime`.
5. Retorna um dicionário com a lista de meses.

## Parâmetros

A função não recebe parâmetros.

## Retorno

- `dict`: Um dicionário contendo a lista dos últimos 6 meses no formato "Mês/Ano".
  - **Exemplo de retorno:**
    ```python
    {
        "meses": ["Janeiro/2023", "Dezembro/2022", "Novembro/2022", "Outubro/2022", "Setembro/2022", "Agosto/2022"]
    }
    ```

## Dependências

- `locale`: Usado para configurar a localidade da aplicação.
- `datetime`: Usado para obter a data atual.
- `dateutil.relativedelta`: Usado para calcular os meses anteriores.

## Código da Função

```{.py3 linenums="1"}
import locale
import datetime
from dateutil.relativedelta import relativedelta

def create_contexto_meses_pagamento() -> dict:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    hoje = datetime.datetime.today()
    meses = [
        (hoje - relativedelta(months=i)).strftime("%B/%Y") for i in range(6)
    ]
    return {"meses": meses}
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="8-10"}
# Executar a função
contexto = create_contexto_meses_pagamento()

# Verificar o resultado
print(contexto)

# Resultado esperado (exemplo fictício):
{
    "meses": ["Janeiro/2023", "Dezembro/2022", "Novembro/2022", "Outubro/2022", "Setembro/2022", "Agosto/2022"]
}
```
