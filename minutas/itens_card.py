"""
Módulo para criação e manipulação de itens de card baseados em informações
de uma minuta.

Este módulo define a classe base `ItemCard` e funções para criar e atualizar
listas de itens de card com base nas informações fornecidas em dicionários
de minuta.

Imports:
    - apos_meia_noite
    - calcular_diferenca
    - hora_str
    - data_str_br
"""
from core.tools import (
    apos_meia_noite,
    calcular_diferenca,
    hora_str,
    data_str_br,
)


class ItemCard:
    """Classe base para os itens do card."""

    # pylint: disable=too-many-instance-attributes, too-few-public-methods

    def __init__(self, **kwargs):
        """
        Inicializa um ItemCard.

        Args:
            **kwargs: Argumentos adicionais para inicializar o ItemCard.
                icon_class (str): Classe do ícone.
                label (str): Rótulo do item.
                icon_button_class (str): Classe do botão de ícone.
                type_button (str): Tipo do botão.
                has_input (bool): Se o item tem input.
                input_type (str): Tipo de input.
                input_name (str): Nome do input.
                input_value (str): Valor do input.
                has_modal (bool): Se o item tem modal.
                title_label (str): Título do modal.
                action (str): Ação do modal.
                save_label (str): Rótulo do botão de salvar.
                idobj (int): ID do objeto.
                has_attr (bool): Se o item tem atributos.
                attrs (list): Lista de atributos adicionais.
        """

        # Atributos comuns
        self.icon_class = f'icofont-{kwargs.get("icon_class")} i-button-null'
        self.label = kwargs.get("label")
        button_class = kwargs.get("icon_button_class")
        type_button = kwargs.get("type_button")
        self.icon_button_class = f"icofont-{button_class} {type_button}"

        # Atributos específicos de input
        self.has_input = kwargs.get("has_input", False)
        if self.has_input:
            self.input_type = kwargs.get("input_type")
            self.input_name = kwargs.get("input_name")
            self.input_value = kwargs.get("input_value")
            self.input_id = f'id_{kwargs.get("input_name")}'
            self.input_class = "form-control form-control-minuta text-center"

        # Atributos específicos de modal
        self.has_modal = kwargs.get("has_modal", False)
        if self.has_modal:
            self.onclick = "openMyModal(event); return false;"
            self.title_label = kwargs.get("title_label")
            self.action = kwargs.get("action")
            self.save_label = kwargs.get("save_label")
            self.idobj = kwargs.get("idobj")

        # Atributos específicos de attrs
        self.has_attr = kwargs.get("has_attr", False)
        if self.has_attr:
            self.data_atributos = {
                f"data-{chave}": valor
                for chave, valor in kwargs.get("attrs", [])
            }

    def deve_incluir(self):
        """Determina se o item deve ser incluído."""
        raise NotImplementedError(
            "As subclasses devem implementar este método"
        )


def adicionar_item_hora_final(minuta, itens):
    """
    Adiciona um item de hora final à lista de itens do card com base
    na minuta.

    Args:
        minuta (dict): Dicionário com informações da minuta.
        itens (list): Lista de itens do card.

    Returns:
        list: Lista de itens do card atualizada.
    """
    data = minuta.get("data")
    inicial = minuta.get("hora_inicial")
    final = minuta.get("hora_final")
    periodo = calcular_diferenca(data, inicial, final)
    str_periodo = hora_str(periodo)
    itens.append(
        ItemCard(
            icon_class="moon",
            label="time_input",
            icon_button_class="check-circled",
            type_button="i-button js-editar-minuta-hora-final",
            input_type="time",
            input_name="hora_final",
            input_value=final,
            has_input=True,
        )
    )
    if apos_meia_noite(periodo):
        itens.append(
            ItemCard(
                icon_class="wall-clock",
                label=str_periodo,
                icon_button_class="check",
                type_button="i-button-null",
            )
        )
    return itens


def adicionar_item_categoria_solicitada(minuta, itens):
    """
    Adiciona um item de categoria solicitada à lista de itens do card com
    base na minuta.

    Args:
        minuta (dict): Dicionário com informações da minuta.
        itens (list): Lista de itens do card.

    Returns:
        list: Lista de itens do card atualizada.
    """
    pedido = minuta.get("veiculo_solicitado")
    motorista = minuta.get("motorista")
    itens.append(
        ItemCard(
            icon_class="google-talk",
            label="INSERE VEICULO SOLICITADO" if pedido is None else pedido,
            icon_button_class="plus-circle" if pedido is None else "edit",
            type_button="i-button",
            title_label="ADICIONAR CATEGORIA VEICULO SOLICITADO",
            action="adicionar_veiculo_solicitado",
            save_label="EDITAR",
            idobj=minuta.get("idminuta"),
            has_modal=True,
        )
    )
    if pedido and not motorista:
        itens.append(
            ItemCard(
                icon_class="waiter-alt",
                label="INSERE MOTORISTA",
                icon_button_class="plus-circle",
                type_button="i-button",
                title_label="ADICIONAR MOTORISTA NA MINUTA",
                action="adicionar_motorista_minuta",
                save_label="ADICIONAR",
                idobj=minuta.get("idminuta"),
                has_modal=True,
            )
        )
    if motorista:
        atributos = [
            ("id_minuta_colaborador", motorista[0]["idMinutaColaboradores"]),
            ("id_minuta", minuta.get("idminuta")),
            ("cargo", "MOTORISTA"),
        ]
        itens.append(
            ItemCard(
                icon_class="waiter-alt",
                label=motorista[0]["apelido"],
                icon_button_class="ui-delete js-excluir-colaborador-minuta",
                type_button="i-button",
                attrs=atributos,
                has_attr=True,
            )
        )
    return itens


def adiciona_item_veiculo(minuta, itens):
    """
    Adiciona um item de veículo à lista de itens do card com base na minuta.

    Args:
        minuta (dict): Dicionário com informações da minuta.
        itens (list): Lista de itens do card.

    Returns:
        list: Lista de itens do card atualizada.
    """
    motorista = minuta.get("motorista")
    if not motorista:
        return itens
    km_total = int(minuta.get("km_final")) - int(minuta.get("km_inicial"))
    veiculo = minuta.get("veiculo")
    if veiculo:
        veiculo_string = f"{veiculo.Marca} {veiculo.Modelo} - {veiculo.Placa}"
        itens.extend(
            [
                ItemCard(
                    icon_class="truck",
                    label=veiculo_string,
                    icon_button_class="edit",
                    type_button="i-button",
                    title_label="ALTERAR VEÍCULO NA MINUTA",
                    action="adicionar_veiculo_minuta",
                    save_label="ALTERAR",
                    idobj=minuta.get("idminuta"),
                    has_modal=True,
                ),
                ItemCard(
                    icon_class="speed-meter",
                    label="time_input",
                    icon_button_class="check-circled",
                    type_button="i-button js-editar-minuta-km-inicial",
                    input_type="number",
                    input_name="km_inicial",
                    input_value=minuta.get("km_inicial"),
                    has_input=True,
                ),
                ItemCard(
                    icon_class="speed-meter",
                    label="time_input",
                    icon_button_class="check-circled",
                    type_button="i-button js-editar-minuta-km-final",
                    input_type="number",
                    input_name="km_final",
                    input_value=minuta.get("km_final"),
                    has_input=True,
                ),
            ]
        )
        if km_total > 0:
            itens.append(
                ItemCard(
                    icon_class="map-pins",
                    label=f"{km_total} KMs",
                    icon_button_class="check",
                    type_button="i-button-null",
                )
            )
    else:
        itens.append(
            ItemCard(
                icon_class="truck",
                label="ADICIONA VEÍCULO",
                icon_button_class="plus-circle",
                type_button="i-button",
                title_label="ADICIONAR VEÍCULO NA MINUTA",
                action="adicionar_veiculo_minuta",
                save_label="ADICIONAR",
                idobj=minuta.get("idminuta"),
                has_modal=True,
            )
        )
    return itens


def adicionar_item_ajudante(minuta, itens):
    """
    Adiciona itens de ajudante à lista de itens do card com base na minuta.

    Args:
        minuta (dict): Dicionário com informações da minuta.
        itens (list): Lista de itens do card.

    Returns:
        list: Lista de itens do card atualizada.
    """
    ajudantes = minuta.get("ajudantes")
    for ajudante in ajudantes:
        atributos = [
            ("id_minuta_colaborador", ajudante["idMinutaColaboradores"]),
            ("id_minuta", minuta.get("idminuta")),
            ("cargo", "AJUDANTE"),
        ]
        itens.append(
            ItemCard(
                icon_class="hotel-boy",
                label=ajudante["apelido"],
                icon_button_class="ui-delete js-excluir-colaborador-minuta",
                type_button="i-button",
                attrs=atributos,
                has_attr=True,
            )
        )
    itens.append(
        ItemCard(
            icon_class="hotel-boy",
            label="ADICIONAR AJUDANTE",
            icon_button_class="plus-circle",
            type_button="i-button",
            title_label="ADICIONAR AJUDANTE À MINUTA",
            action="adicionar_ajudante_minuta",
            save_label="ADICIONAR",
            idobj=minuta.get("idminuta"),
            has_modal=True,
        )
    )
    return itens


def adicionar_item_informacao(minuta, itens):
    """
    Adiciona um item de informações de coleta, entrega e observações
    à lista de itens do card com base na minuta.

    Args:
        minuta (dict): Dicionário com informações da minuta.
        itens (list): Lista de itens do card.

    Returns:
        list: Lista de itens do card atualizada.
    """
    coleta = minuta.get("coleta", "").strip()
    entrega = minuta.get("entrega", "").strip()
    obs = minuta.get("obs", "").strip()

    coleta = coleta if coleta else "COLETA NÃO INFORMADA"
    entrega = entrega if entrega else "ENTREGA NÃO INFORMADA"
    obs = obs if obs else "OBSERVAÇÕES NÃO INFORMADA"

    item_card_data = [
        ("truck-loaded", coleta),
        ("delivery-time", entrega),
        ("info", obs),
    ]

    itens.extend(
        [
            ItemCard(
                icon_class=icon,
                label=text,
                icon_button_class="edit",
                type_button="i-button",
                title_label="EDITAR INFORMAÇÕES DA MINUTA",
                action="editar_informacoes_minuta",
                save_label="EDITAR",
                idobj=minuta.get("idminuta"),
                has_modal=True,
            )
            for icon, text in item_card_data
        ]
    )
    return itens


def criar_itens_card_minuta(minuta):
    """
    Cria uma lista de itens de card com base nas informações da minuta.

    Args:
        minuta (dict): Dicionário com informações da minuta.

    Returns:
        list: Lista de objetos ItemCard.
    """
    itens = [
        ItemCard(
            icon_class="building",
            label=minuta.get("cliente"),
            icon_button_class="check",
            type_button="i-button-null",
        ),
        ItemCard(
            icon_class="layers",
            label=minuta.get("status_minuta"),
            icon_button_class="check",
            type_button="i-button-null",
        ),
        ItemCard(
            icon_class="calendar",
            label=data_str_br(minuta.get("data")),
            icon_button_class="check",
            type_button="i-button-null",
        ),
        ItemCard(
            icon_class="sun",
            label=hora_str(minuta.get("hora_inicial")),
            icon_button_class="check",
            type_button="i-button-null",
        ),
    ]
    itens = adicionar_item_hora_final(minuta, itens)
    itens = adicionar_item_categoria_solicitada(minuta, itens)
    itens = adiciona_item_veiculo(minuta, itens)
    itens = adicionar_item_ajudante(minuta, itens)
    itens = adicionar_item_informacao(minuta, itens)
    return itens
