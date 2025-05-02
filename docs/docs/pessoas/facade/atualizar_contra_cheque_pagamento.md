# `atualizar_contra_cheque_pagamento`

Função responsável por atualizar o contracheque de pagamento de um colaborador, computando seus eventos salariais com base nos registros do cartão de ponto.

## Fluxo de Execução

1. Obtém os dados do colaborador, incluindo:
   - Data de admissão e demissão.
   - Vale-transporte.
   - Salário mais recente antes da data de referência, buscando na tabela `AlteracaoSalarial`.
2. Calcula o primeiro e último dia do mês de referência, ajustando com datas de admissão/demissão quando necessário.
3. Filtra os registros do cartão de ponto do colaborador dentro do intervalo calculado.
4. Define os itens que serão computados no contracheque:
   - `SALARIO`: Cálculo do salário proporcional ao mês.
   - `VALE TRANSPORTE`: Cálculo baseado na tarifa diária e no cartão de ponto.
   - `HORA EXTRA`: Calcula horas extras registradas.
   - `ADIANTAMENTO`: Obtém valores referentes ao adiantamento salarial.
   - `ATRASO`: Desconta valores devido a atrasos registrados.
   - `FALTAS`: Aplica os descontos conforme as ausências não abonadas.
   - `DSR SOBRE FALTAS`: Calcula impacto do descanso semanal remunerado.
5. Processa os eventos do contracheque, registrando ou atualizando os valores no banco de dados.
6. Retorna os itens computados para serem armazenados e utilizados no pagamento.

## Parâmetros

- `id_pessoal` (`str`): Identificador único do colaborador.
- `mes` (`int`): Mês de referência do pagamento.
- `ano` (`int`): Ano de referência do pagamento.
- `contra_cheque` (`ContraCheque`): Objeto do contracheque a ser atualizado.

## Retorno

- Os itens do contracheque são atualizados no banco de dados.

## Dependências

- `classes.Colaborador(id_pessoal)`: Obtém informações do colaborador.
- `primeiro_e_ultimo_dia_do_mes(mes, ano)`: Calcula os limites do mês de referência.
- `AlteracaoSalarial.objects.filter(...).order_by("-Valor").values_list("Valor", flat=True).first()`: Obtém o salário mais recente do colaborador antes do último dia do período.
- `CartaoPonto.objects.filter(...)`: Obtém os registros do cartão de ponto.
- `EVENTOS_CONTRA_CHEQUE`: Lista de eventos aplicáveis ao contracheque.
- `atualizar_ou_adicionar_contra_cheque_item(...)`: Insere ou atualiza os itens do contracheque.

## Código da Função

```{py3 linenums="1"}
def atualizar_contra_cheque_pagamento(id_pessoal, mes, ano, contra_cheque):
    """Atualiza os eventos do contracheque de pagamento do colaborador."""
    colaborador = classes.Colaborador(id_pessoal)
    admissao = colaborador.dados_profissionais.data_admissao
    demissao = colaborador.dados_profissionais.data_demissao
    tarifa_dia = colaborador.salarios.salarios.ValeTransporte
    id_contra_cheque = contra_cheque.idContraCheque

    primeiro_dia, ultimo_dia = primeiro_e_ultimo_dia_do_mes(mes, ano)
    primeiro_dia = admissao if admissao > primeiro_dia.date() else primeiro_dia
    ultimo_dia = (
        demissao if demissao and demissao < ultimo_dia.date() else ultimo_dia
    )

    salario = (
        AlteracaoSalarial.objects.filter(
            idPessoal=id_pessoal, Data__lt=ultimo_dia
        )
        .order_by("-Valor")
        .values_list("Valor", flat=True)
        .first()
    )

    cartao_ponto = CartaoPonto.objects.filter(
        Dia__range=[primeiro_dia, ultimo_dia], idPessoal=id_pessoal
    )

    itens_contra_cheque = [
        {
            "nome": "SALARIO",
            "codigo": "1000",
            "calculo": lambda: calcular_salario(salario, cartao_ponto),
            "registro": "C",
            "referencia": lambda dias: dias,
        },
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

    evento_lookup = {evento.codigo: evento for evento in EVENTOS_CONTRA_CHEQUE}

    for item in itens_contra_cheque:
        evento = evento_lookup.get(item["codigo"])
        descricao = evento.descricao
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
# Atualiza um contracheque de pagamento de um colaborador específico
atualizar_contra_cheque_pagamento("123", 4, 2025, contra_cheque)
```
