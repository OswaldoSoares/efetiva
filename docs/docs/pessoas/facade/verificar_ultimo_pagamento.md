# `verificar_ultimo_pagamento`

Função responsável por verificar o último pagamento realizado a um colaborador e calcular a data do próximo pagamento possível.

## Fluxo de Execução

1. Obtém a estrutura de ordenação dos meses usando [`get_meses_ordem`](./get_meses_ordem.md).
2. Busca o último pagamento realizado filtrando na tabela `ContraCheque` por:
   - `idPessoal_id` correspondente ao colaborador.
   - `Descricao="PAGAMENTO"`.
   - `Pago=True`.
3. Adiciona a ordenação por ano e mês de referência, garantindo que o último pagamento registrado seja obtido.
4. Se um pagamento for encontrado:
   - Calcula o próximo ano e mês possíveis para pagamento.
   - Retorna a data do próximo pagamento possível (`date(ano, mes, 1)`).
5. Se nenhum pagamento for encontrado, retorna `False`.

## Parâmetros

- `id_pessoal` (int): Identificador único do colaborador.

## Retorno

- `date` ou `bool`: Retorna a data do próximo pagamento possível ou `False` caso nenhum pagamento tenha sido encontrado.

## Dependências

- [`get_meses_ordem`](./get_meses_ordem.md): Obtém a estrutura de ordenação dos meses.
- `ContraCheque.objects.filter(...)`: Consulta a base de dados para obter o último pagamento.
- `date` do módulo `datetime` para gerar a próxima data de pagamento.

## Código da Função

```{py3 linenums="1"}
def verificar_ultimo_pagamento(id_pessoal):
    meses_ordem = get_meses_ordem()

    ultimo_mes_pago = (
        ContraCheque.objects.filter(
            idPessoal_id=id_pessoal, Descricao="PAGAMENTO", Pago=True
        )
        .annotate(mes_ordenado=meses_ordem)
        .order_by("-AnoReferencia", "-mes_ordenado")
    ).first()

    if ultimo_mes_pago:
        ano_possivel = (
            ultimo_mes_pago.AnoReferencia
            if ultimo_mes_pago.mes_ordenado < 12
            else ultimo_mes_pago.AnoReferencia + 1
        )
        mes_possivel = (
            ultimo_mes_pago.mes_ordenado + 1
            if ultimo_mes_pago.mes_ordenado < 12
            else 1
        )

        data_possivel = date(ano_possivel, mes_possivel, 1)

        return data_possivel

    return False
```

## Exemplo de Uso

```{py3 linenums="1" hl_lines="5"}
# Verifica o último pagamento de um colaborador com ID 10
data_proximo_pagamento = verificar_ultimo_pagamento(10)

print(data_proximo_pagamento)
2025-03-01
```
