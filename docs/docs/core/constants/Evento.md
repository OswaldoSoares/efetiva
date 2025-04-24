# `Evento`

Classe que representa um evento de contracheque. Define os atributos essenciais para identificar o tipo do evento, sua natureza e se deve ser considerado no cálculo do saldo.

## Definição da Classe

```{.py3 linenums="1" }
from dataclasses import dataclass

@dataclass(frozen=True)
class Evento:
    codigo: str
    descricao: str
    computavel: bool
    credito: bool
```

| Atributo   | Tipo  | Descrição                                                                 |
|------------|-------|---------------------------------------------------------------------------|
| `codigo`   | str   | Código identificador único do evento no contracheque.                     |
| `descricao`| str   | Descrição textual do evento.                                              |
| `computavel` | bool | Indica se o valor do evento deve ser considerado no cálculo do saldo.     |
| `credito`  | bool  | Indica se o evento é um crédito (`True`) ou um débito (`False`).          |

## EVENTOS_CONTRA_CHEQUE
- [`ver no formato de tabela`](`/tabelas/eventos_contra_cheque`)

```{.py3 linenums="1"}
EVENTOS_CONTRA_CHEQUE = (
    Evento("1000", "SALÁRIO", True, True),
    Evento("1003", "HORAS EXTRAS", True, True),
    Evento("1019", "1/3 FÉRIAS", True, True),
    Evento("1020", "FÉRIAS", True, True),
    Evento("1211", "GRATIFICAÇÕES", True, True),
    Evento("1410", "VALE TRANSPORTE", True, True),
    Evento("5001", "13º SALÁRIO", True, True),
    Evento("5501", "ADIANTAMENTO DE SALÁRIO", True, True),
    Evento("5504", "13º SALÁRIO - ADIANTAMENTO", True, True),
    Evento("9200", "DESCOTO DE ADIANTAMENTOS", True, False),
    Evento("9207", "FALTAS", True, False),
    Evento("9208", "ATRASOS", True, False),
    Evento("9211", "DSR SOBRE FALTAS", True, False),
    Evento("9212", "DSR SOBRE ATRAZOS", True, False),
    Evento("9214", "13º SALÁRIO - DESCOTO DE ADIANTAMENTO", True, False),
    Evento("9901", "VALE", False, False),
    Evento("9902", "MULTA", False, False),
)
```

## Exemplo de Uso

```{.py3 linenums="1" hl_lines="11 16 21 26"}
evento = Evento(
    codigo="1000",
    descricao="SALÁRIO",
    computavel=True,
    credito=True
)

print(evento.codigo)

# Resultado esperado:
1000

print(evento.descricao)

# Resultado esperado:
SALÁRIO

print(evento.computavel)

# Resultado esperado:
True

print(evento.credito)

# Resultado esperado:
True
```
