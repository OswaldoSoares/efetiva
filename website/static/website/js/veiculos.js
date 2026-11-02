// VEÍCULOS: lista, detalhes e cadastro (padrão ui-*)

// Como executarAjax (ajax.js), mas sem voltar ao topo da página,
// para não perder a posição na lista ao selecionar um veículo
function veiculosAjax(url, type, data, sucessoCallback) {
    $.ajax({
        type: type,
        url: url,
        data: data,
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(response) {
            sucessoCallback(response);
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log("ERROR: ", error);
            $(".box-loader").hide();
            mostrarToast("Não foi possível concluir a operação.", "error");
        }
    });
}

function veiculosFiltros() {
    var card = $(".js-veiculos");
    return {
        situacao: card.attr("data-situacao"),
        id_categoria: card.attr("data-id_categoria"),
    };
}

// Veículo aberto no card de detalhes
function veiculosSelecionado() {
    return $(".js-veiculos").attr("data-id_veiculo") || "";
}

function veiculosAtualiza(data) {
    if (data["html-card-veiculos"]) {
        $(".card-veiculos").html(data["html-card-veiculos"]);
    }
    if (data["html-card-veiculo"]) {
        $(".card-veiculo").html(data["html-card-veiculo"]);
    }
    if (data["html-card-categorias-veiculo"]) {
        $(".card-categorias-veiculo").html(data["html-card-categorias-veiculo"]);
    }
    if (data["mensagem"]) {
        mostrarToast(data["mensagem"], data["tipo"]);
    }
}

function veiculosCarregaLista(filtros) {
    filtros.id_veiculo = veiculosSelecionado();
    veiculosAjax($(".js-veiculos").data("url-lista"), "GET", filtros, veiculosAtualiza);
}

$(document).on("click", ".js-veiculos-filtro", function() {
    var filtros = veiculosFiltros();
    filtros.situacao = $(this).data("situacao");
    veiculosCarregaLista(filtros);
});

$(document).on("change", ".js-veiculos-categoria", function() {
    var filtros = veiculosFiltros();
    filtros.id_categoria = $(this).val();
    veiculosCarregaLista(filtros);
});

$(document).on("click", ".js-veiculo-selecionar", function() {
    var linha = $(this);
    var id = linha.data("id_veiculo");
    veiculosAjax(linha.data("url"), "GET", {id_veiculo: id}, function(data) {
        $(".js-veiculo-selecionar").removeClass("ui-linha-ativa");
        linha.addClass("ui-linha-ativa");
        $(".js-veiculos").attr("data-id_veiculo", id);
        veiculosAtualiza(data);
        // Em telas estreitas o card de detalhes fica abaixo da lista
        if (window.matchMedia("(max-width: 1200px)").matches) {
            $("html, body").animate({scrollTop: $(".card-veiculo").offset().top - 10}, 200);
        }
    });
});

// Foca o primeiro campo com erro ou, se não houver erro, o primeiro campo
function veiculosFocaCampo(modal) {
    var form = modal.find(".modal-body form");
    var campos = form.find(".errorlist").first().closest("div").find("input, select");
    if (!campos.length) {
        campos = form.find("input:visible, select:visible");
    }
    campos.first().trigger("focus").trigger("select");
}

function veiculosSubmit(modal) {
    var form = modal.find(".modal-body form");
    form.on("focus", "input", function() {
        this.select();
    });
    form.find("[name=Placa]").on("input", function() {
        this.value = this.value.toUpperCase();
    });
    modal.find(".modal-footer .btn-save").off("click").on("click", function() {
        form.trigger("submit");
    });
    form.on("submit", function(event) {
        event.preventDefault();
        var filtros = veiculosFiltros();
        filtros.id_selecionado = veiculosSelecionado();
        var dados = form.serialize() + "&" + $.param(filtros);
        veiculosAjax(form.attr("action"), "POST", dados, function(data) {
            if (data["html_form"]) {
                modal.find(".modal-body").html(data["html_form"]);
                veiculosSubmit(modal);
                veiculosFocaCampo(modal);
            } else {
                modal.modal("hide");
                veiculosAtualiza(data);
            }
        });
    });
}

$(document).on("click", ".js-veiculo-abrir", function() {
    var botao = $(this);
    var modal = $("#MyModal");
    var requestData = {};
    $.each(["id_veiculo", "id_categoria_form"], function(i, chave) {
        if (botao.data(chave)) {
            requestData[chave] = botao.data(chave);
        }
    });
    veiculosAjax(botao.data("url"), "GET", requestData, function(data) {
        modal.find(".modal-title").text(botao.data("title"));
        modal.find(".modal-footer .btn-save").text("SALVAR");
        modal.find(".modal-body").html(data["modal_html"]);
        veiculosSubmit(modal);
        // O Bootstrap foca o próprio modal ao terminar de abrir,
        // então o foco no campo só pode ser dado depois disso
        modal.off("shown.bs.modal.veiculos").one("shown.bs.modal.veiculos", function() {
            veiculosFocaCampo(modal);
        });
        modal.modal("show");
    });
});

// Ativar/inativar e excluir (veículo ou categoria): POST com confirmação opcional
$(document).on("click", ".js-veiculo-acao", function() {
    var botao = $(this);
    if (botao.data("confirmar") && !confirm(botao.data("confirmar"))) {
        return;
    }
    var dados = veiculosFiltros();
    dados.id_selecionado = veiculosSelecionado();
    $.each(["id_veiculo", "id_categoria_excluir"], function(i, chave) {
        if (botao.data(chave)) {
            dados[chave] = botao.data(chave);
        }
    });
    dados.csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").first().val();
    veiculosAjax(botao.data("url"), "POST", dados, veiculosAtualiza);
});
