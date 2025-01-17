# `create_contexto_eventos_rescisorios_colaborador`

Cria o contexto necessário para exibir informações sobre eventos rescisórios de um colaborador.

## Lógica do Cálculo

1. Obtém o identificador único do colaborador a partir dos parâmetros da requisição (`id_pessoal`).
2. Recupera as constantes predefinidas para:
   - Eventos rescisórios (`EVENTOS_RESCISORIOS`).
   - Motivos de demissão (`MOTIVOS_DEMISSAO`).
   - Regras de aviso prévio (`AVISO_PREVIO`).
3. Retorna um dicionário com as informações para serem usadas no contexto.

## Parâmetros

- `request` (HttpRequest): Objeto de requisição HTTP contendo os parâmetros necessários.

## Retorno

- (dict): Dicionário contendo:
  - `id_pessoal` (str): Identificador único do colaborador obtido da requisição.
  - `eventos` (list): Lista de eventos rescisórios predefinidos.
  - `motivos` (list): Lista de motivos de demissão predefinidos.
  - `aviso_previo` (dict): Regras de aviso prévio predefinidas.
  - `mensagem` (str): Mensagem padrão a ser exibida no contexto.

## Código da Função

```{.py3 linenums="1"}
def create_contexto_eventos_rescisorios_colaborador(request):
    id_pessoal = request.GET.get("id_pessoal")
    eventos = EVENTOS_RESCISORIOS
    motivos = MOTIVOS_DEMISSAO
    aviso_previo = AVISO_PREVIO

    return {
        "id_pessoal": id_pessoal,
        "eventos": eventos,
        "motivos": motivos,
        "aviso_previo": aviso_previo,
        "mensagem": "SELECIONAR EVENTOS",
    }
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="11-17"}
from django.http import HttpRequest

# Simulando uma requisição GET
request = HttpRequest()
request.GET["id_pessoal"] = "12345"

contexto = create_contexto_eventos_rescisorios_colaborador(request)
print(contexto)

# Resultado esperado (exemplo fictício):
{
    "id_pessoal": "12345",
    "eventos": [...],
    "motivos": [...],
    "aviso_previo": {...},
    "mensagem": "SELECIONAR EVENTOS",
}
```

