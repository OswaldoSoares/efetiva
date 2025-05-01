
# `create_contexto_contra_cheque_adiantamento`

Função responsável por gerar o contexto de contracheque para adiantamento salarial, incluindo os itens do contracheque e o saldo computável associado.

## Fluxo de Execução

1. Obtém os parâmetros `id_pessoal`, `mes` e `ano` da requisição.
2. Converte o número do mês para sua forma por extenso.
3. Busca ou cria um objeto `ContraCheque` para o colaborador referente ao adiantamento.
4. Obtém a descrição do evento de adiantamento a partir de `EVENTOS_CONTRA_CHEQUE`.
5. Calcula 40% do salário do colaborador.
6. Registra o item de contracheque com o evento de adiantamento.
7. Obtém o arquivo gerado referente ao contracheque.
8. Obtém o saldo do contracheque.
9. Monta o contexto com os dados do contracheque, itens e saldo.
10. Retorna o contexto formatado.

## Parâmetros

- `request` (`HttpRequest`): Objeto de requisição contendo os dados enviados pelo cliente.
  - `id_pessoal` (`str`): Identificador único do colaborador.
  - `mes` (`int`): Mês de referência do adiantamento.
  - `ano` (`str`): Ano de referência do adiantamento.

## Retorno

- `dict`: Retorna um dicionário contendo os seguintes campos:
  - `mensagem` (`str`): Mensagem informativa sobre o adiantamento processado.
  - `contra_cheque` (`ContraCheque`): Objeto representando o contracheque do colaborador.
  - `contra_cheque_itens` (`ContraChequeItens`): Lista de itens do contracheque.
  - `id_pessoal` (`str`): Identificador do colaborador.
  - `file` (`File`): Arquivo do contracheque gerado.
  - `saldo_computavel` (`dict`): Saldo calculado do contracheque.

## Dependências

- `obter_mes_por_numero(mes)`: Converte um número de mês para seu nome por extenso.
- `get_or_create_contra_cheque(...)`: Obtém ou cria um contracheque.
- `classes.Colaborador(id_pessoal)`: Obtém informações do colaborador.
- `get_or_create_contra_cheque_itens(...)`: Registra um item do contracheque.
- `get_file_contra_cheque(...)`: Obtém o arquivo gerado do contracheque.
- `get_saldo_contra_cheque(...)`: Obtém o saldo calculado dos itens do contracheque.

## Código da Função

```{py3 linenums="1"}
def create_contexto_contra_cheque_adiantamento(request):
    id_pessoal = request.GET.get("id_pessoal")
    mes_por_extenso = obter_mes_por_numero(int(request.GET.get("mes")))
    ano = request.GET.get("ano")

    contra_cheque, _ = get_or_create_contra_cheque(
        mes_por_extenso, ano, "ADIANTAMENTO", id_pessoal
    )

    evento_lookup = {evento.codigo: evento for evento in EVENTOS_CONTRA_CHEQUE}
    evento = evento_lookup.get("5501")
    descricao = evento.descricao

    colaborador = classes.Colaborador(id_pessoal)
    salario = colaborador.salarios.salarios.Salario
    quarenta_por_cento = (salario / 100) * 40

    contra_cheque_itens = get_or_create_contra_cheque_itens(
        descricao, quarenta_por_cento, "C", "40%", contra_cheque, "5501"
    )

    file = get_file_contra_cheque(contra_cheque.idContraCheque)

    contexto = {
        "mensagem": f"Adiantamento selecionado: {mes_por_extenso}/{ano}",
        "contra_cheque": contra_cheque,
        "contra_cheque_itens": contra_cheque_itens,
        "id_pessoal": id_pessoal,
        **get_saldo_contra_cheque(contra_cheque_itens),
    }

    return contexto
```

## Exemplo de Uso

```{py3 linenums="1"}
from django.test import RequestFactory

# Simula uma requisição GET com os parâmetros necessários
request = RequestFactory().get("/contra-cheque-adiantamento/", {
    "id_pessoal": "123",
    "mes": "4",
    "ano": "2025"
})

# Chama a função
contexto = create_contexto_contra_cheque_adiantamento(request)

# Exibe o contexto retornado
print(contexto)
```
