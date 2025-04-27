# atualizar_contra_cheque_pagamento

Bloco de código responsável por processar eventos de contracheque e atualizar ou adicionar itens com base em cálculos específicos.

## Fluxo de Execução

1. Define uma lista de eventos do contracheque com nome, código, cálculo e método de referência.
2. Cria um dicionário (`evento_lookup`) para facilitar a busca de eventos pelo código.
3. Itera sobre cada item do contracheque:
   - Obtém o evento correspondente no `evento_lookup`.
   - Executa o cálculo do evento para determinar quantidade e valor.
   - Chama `atualizar_ou_adicionar_contra_cheque_item(...)` para registrar ou atualizar o item no contracheque.

## Parâmetros

- `EVENTOS_CONTRA_CHEQUE` (`list`): Lista de eventos disponíveis para cálculo.
- `tarifa_dia` (`float`): Tarifa diária usada para calcular `VALE TRANSPORTE`.
- `salario` (`float`): Salário do colaborador.
- `cartao_ponto` (`QuerySet`): Registros do cartão de ponto do colaborador.
- `contra_cheque` (`ContraCheque`): Objeto representando o contracheque do colaborador.
- `id_pessoal` (`int`): Identificador único do colaborador.
- `id_contra_cheque` (`int`): Identificador único do contracheque.

## Retorno

- Os itens do contracheque são atualizados ou adicionados à base de dados.

## Dependências

- `calcular_conducao(...)`: Calcula o valor do vale transporte.
- `calcular_horas_extras(...)`: Calcula o valor das horas extras.
- `calcular_adiantamento(...)`: Obtém o valor do adiantamento.
- `calcular_atrasos(...)`: Calcula o impacto de atrasos no contracheque.
- `calcular_faltas(...)`: Determina faltas e valores a serem descontados.
- `calcular_dsr(...)`: Calcula o descanso semanal remunerado sobre faltas.
- `atualizar_ou_adicionar_contra_cheque_item(...)`: Atualiza ou adiciona os itens ao contracheque.

## Código da Função

```{py3 linenums="1"}
eventos_contra_cheque = [
    {
        "nome": "VALE TRANSPORTE",
        "codigo": "1410",
        "calculo": lambda: calcular_conducao(tarifa_dia, cartao_ponto)
        if tarifa_dia
        else (0, 0),
        "registro": "C",
        "referencia": lambda dias: dias,
    },
    {
        "nome": "HORA EXTRA",
        "codigo": "1003",
        "calculo": lambda: calcular_horas_extras(salario, cartao_ponto),
        "registro": "C",
        "referencia": lambda horas: horas,
    },
    {
        "nome": "ADIANTAMENTO",
        "codigo": "9200",
        "calculo": lambda: calcular_adiantamento(contra_cheque),
        "registro": "D",
        "referencia": lambda porc: porc,
    },
    {
        "nome": "ATRASO",
        "codigo": "9208",
        "calculo": lambda: calcular_atrasos(salario, cartao_ponto),
        "registro": "D",
        "referencia": lambda horas: horas,
    },
    {
        "nome": "FALTAS",
        "codigo": "9207",
        "calculo": lambda: calcular_faltas(salario, cartao_ponto),
        "registro": "D",
        "referencia": lambda dias: dias,
    },
    {
        "nome": "DSR SOBRE FALTAS",
        "codigo": "9211",
        "calculo": lambda: calcular_dsr(id_pessoal, salario, cartao_ponto),
        "registro": "D",
        "referencia": lambda dias: dias,
    },
]

evento_lookup = {evento["codigo"]: evento for evento in eventos_contra_cheque}

for item in eventos_contra_cheque:
    evento = evento_lookup.get(item["codigo"])
    descricao = evento["nome"]
    quantidade, valor = item["calculo"]()
    atualizar_ou_adicionar_contra_cheque_item(
        descricao,
        valor,
        item["registro"],
        item["referencia"](quantidade),
        item["codigo"],
        id_contra_cheque,
    )
```

## Exemplo de Uso

```{py3 linenums="1"}
# Chama o processamento de eventos de contracheque para um colaborador específico
atualizar_contra_cheque_pagamento(id_pessoal, salario, cartao_ponto, contra_cheque)
```
