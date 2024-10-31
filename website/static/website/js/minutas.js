$(document).ready(function() {
    localStorage.setItem("idminuta", $("#id_minuta").data("id"))
    $(".filtro-dados").hide();
    $(".card-minutas-consulta").hide();

    const id_minuta = localStorage.getItem("idminuta")
    if (id_minuta  !== 'undefined') {
        toggleButton();
    }
    verificaChecklist();
    mostraChecklist();
    verificaCheckboxClasse("total-recebe");
    formatarInicial();
    if ($(".status-minuta").text() != "FECHADA") {
        calcularTotais("recebe");
    }
    $(".box-loader").hide()
});

$(document).on("click", ".js-editar-minuta-hora-final", function() {
    var id_minuta = localStorage.getItem("idminuta")
    var hora_final = $("#id_hora_final").val()

    executarAjax("/minutas/editar_minuta_hora_final", "GET", {
        id_minuta: id_minuta,
        hora_final: hora_final,
    }, function(data) {
        atualizaAposMinutaAlterada(data)
    });
});

$(document).on("click", ".js-editar-minuta-km-inicial", function() {
    var id_minuta = localStorage.getItem("idminuta")
    var km_inicial = $("#id_km_inicial").val()

    executarAjax("/minutas/editar_minuta_km_inicial", "GET", {
        id_minuta: id_minuta,
        km_inicial: km_inicial,
    }, function(data) {
        atualizaAposMinutaAlterada(data)
    });
});

$(document).on("click", ".js-editar-minuta-km-final", function() {
    var id_minuta = localStorage.getItem("idminuta")
    var km_inicial = $("#id_km_inicial").val()
    var km_final = $("#id_km_final").val()

    executarAjax("/minutas/editar_minuta_km_final", "GET", {
        id_minuta: id_minuta,
        km_inicial: km_inicial,
        km_final: km_final,
    }, function(data) {
        atualizaAposMinutaAlterada(data)
    });
});

$(document).on("submit", "#js-gera-receitas", function(event) {
    event.preventDefault();
    var data = $(this).serialize();

    executarAjax("/minutas/gera_receitas", "POST", data, function(data) {
        atualizaAposMinutaAlterada(data)
        toggleButton()
    });
});
    
$(document).on("submit", "#js-gera-pagamentos", function(event) {
    event.preventDefault();
    var data = $(this).serialize();

    executarAjax("/minutas/gera_pagamentos", "POST", data, function(data) {
        $(".card-minuta").html(data["html-card-minuta"]);
        $(".card-checklist").html(data["html-card-checklist"]);
        $(".html-form-paga").html(data["html-card-pagamentos"]);
        mostraChecklist();
    });
});
    
$(document).on("click", ".estorna-pagamentos-ajudantes", function(event) {
    var idminuta = $(this).attr("idMinuta")

    executarAjax("/minutas/estorna_pagamentos_ajudantes", "GET", {
        idminuta: idminuta,
    }, function(data) {
        $(".card-minuta").html(data["html-card-minuta"]);
        $(".card-checklist").html(data["html-card-checklist"]);
        $(".html-form-paga").html(data["html-card-pagamentos"]);
        mostraChecklist();
    });
});

$(document).on("click", ".js-alterar-status-minuta", function() {
    var id_minuta = $(this).data("id_minuta")
    var proximo_status = $(this).data("proximo-status")

    executarAjax("/minutas/alterar_status_minuta", "GET", {
        id_minuta: id_minuta,
        proximo_status: proximo_status,
    }, function(data) {
        atualizaAposMinutaAlterada(data);
        toggleButton();
        verificaChecklist();
        mostraChecklist();
        $(".box-loader").hide();
    });
});

$(document).on("click", ".estorna-pagamentos-motorista", function(event) {
    var idminuta = $(this).attr("idMinuta")

    executarAjax("/minutas/estorna_pagamentos_motorista", "GET", {
        idminuta: idminuta,
    }, function(data) {
        $(".card-minuta").html(data["html-card-minuta"]);
        $(".card-checklist").html(data["html-card-checklist"]);
        $(".html-form-paga").html(data["html-card-pagamentos"]);
        mostraChecklist();
    });
});

$(document).on("click", ".js-estorna-faturamento", function(event) {
    var idminuta = $(this).data("idminuta")

    executarAjax("/minutas/estorna_faturamento", "GET", {
        idminuta: idminuta,
    }, function(data) {
        atualizaAposMinutaAlterada(data)
        toggleButton()
    });
});

$(document).on("click", ".js-excluir-colaborador-minuta", function() {
    var id_minuta = $(this).data("id_minuta")
    var id_minuta_colaborador = $(this).data("id_minuta_colaborador")
    var cargo = $(this).data("cargo")

    executarAjax("/minutas/excluir_colaborador_minuta", "GET", {
        id_minuta: id_minuta,
        id_minuta_colaborador: id_minuta_colaborador,
        cargo: cargo,
    }, function(data) {
        atualizaAposMinutaAlterada(data)
    });
});

$(document).on("click", ".js-excluir-despesa-minuta", function(event) {
    var id_minuta = localStorage.getItem("idminuta")
    var id_minuta_itens = $(this).data("id_minuta_itens")

    executarAjax("/minutas/excluir_despesa", "GET", {
        id_minuta_itens: id_minuta_itens,
        id_minuta: id_minuta,
    }, function(data) {
        atualizaAposDespesaAlterada(data)
    });
});

$(document).on("click", ".js-filtra-veiculo-categoria", function() {
    var filtro = $(this).val()

    executarAjax("/minutas/filtraveiculoescolhido", "GET", {
        idobj: $("#idminuta").attr("idminuta"),
        idPessoal: $("#idpessoal").attr("idpessoal"),
        Filtro: filtro,
    }, function(data) {
        $("#id_veiculo").html(data["html_filtro"])
    });
});

$(document).on("click", ".js-card-receitas-toggle", function() {
    // Verifica se o botão já tem a classe 'icofont-rounded-up'
    if ($(this).hasClass("icofont-rounded-up")) {
        // Oculta as linhas onde o checkbox NÃO está marcado
        $(".card-body-item-row").each(function() {
            let checkbox = $(this).find("input[type='checkbox']");
            if (!checkbox.is(":checked")) {
                $(this).slideUp(500);
            }
        });
        // Remove a classe para alternar o estado
        $(this).removeClass("icofont-rounded-up");
    } else {
        // Mostra as linhas onde o checkbox NÃO está marcado
        $(".card-body-item-row").each(function() {
            let checkbox = $(this).find("input[type='checkbox']");
            if (!checkbox.is(":checked")) {
                $(this).slideDown(500)
            }
        });
        // Adiciona a classe para alternar o estado
        $(this).addClass("icofont-rounded-up")
    }
});

$(document).on("click", ".js-alterar-capacidade", function () {
    $("#tabela-capacidade_peso-recebe").val($(this).data("valor"));
    $("#tabela-capacidade_peso-recebe").trigger("change");
    calcularTotais("recebe");
});

$(document).on("click", ".js-alterar-perimetro", function () {
    $("#tabela-perimetro-recebe").val($(this).data("valor"));
    $("#tabela-perimetro-recebe").trigger("change");
    calcularTotais("recebe");
});

function manipularModalEntrega() {
    if ($("#chk-perimetro").is(":checked")) {
        $(".js-perimetro-hide").hide();
    }
}

function openMyModal(event) {
    var modal = initModalDialog(event, "#MyModal");
    var url = $(event.target).data("action");
    var requestData = {
        idobj: $(event.target).data("idminuta"),
        idPessoal: $(event.target).data("idpessoal"),
        id_minuta_itens: $(event.target).data("id_minuta_itens"),
        id_minuta_nota: $(event.target).data("id_minuta_nota"),
    }

    executarAjax(url, "GET", requestData, function(data) {
        modal.find(".modal-body").html(data.modal_html);
        modal.modal("show");

        if ($(event.target).data("action") === '/minutas/adicionar_entrega') {
            manipularModalEntrega()
        }

        formAjaxSubmit(modal, url);
    }, function(errorThrown) {
        console.log(errorThrown)
    });
}

function initModalDialog(event, modal_element) {
    var modal = $(modal_element);
    var target = $(event.target);

    // Configura Titulo
    var title = target.data("title") || "";
    var subtitle = target.data("subtitle") || "";
    modal.find(".modal-title").text(title);
    modal.find(".modal-subtitle").text(subtitle);

    // Configura Estilo
    var dialog_class = (target.data("dialog-class") || "") + " modal-dialog";
    var icon_class = (target.data("icon") || "fa-laptop") + " fa modal-icon";
    modal.find(".modal-dialog").attr("class", dialog_class);
    modal.find(".modal-header .title-wrapper i").attr("class", icon_class);

    // Configura Botões
    var button_save_label = target.data("button-save-label") || "OK";
    modal.find(".modal-footer .btn-save").text(button_save_label);

    // Limpa o corpo do Modal e armazena alvo que disparou o evento
    modal.find(".modal-body").html("");
    modal.data("target", target);

    return modal;
}

function formAjaxSubmit(modal, action) {
    var form = modal.find(".modal-body form");
    var header = $(modal).find(".modal-header");
    var btn_save = modal.find(".modal-footer .btn-save");

    if (btn_save) {
        modal.find(".modal-body form .form-submit-row").hide();
        btn_save.off().on("click", function() {
            modal.find(".modal-body form").submit();
        });
    }

    form.find("input:visible").first().focus();
    title = modal.find(".modal-title").text();

    $(form).on("submit", function(event) {
        event.preventDefault();
        header.addClass("loading");
        var url = $(this).attr("action") || action;

        enviarRequisicaoAjax(url, form, function(xhr) {
            processarRespostaAjax(xhr, modal, url)
        });
    });
}

function processarRespostaAjax(xhr, modal, url) {
    modalBody = modal.find(".modal-body");
    modalBody.html(xhr["html_form"]);

    if (modalBody.find(".errorlist").length > 0) {
        formAjaxSubmit(modal, url);
    } else {
        $(modal).modal("hide");
        atualizarInterfaceComDados(xhr);
        exibirMensagem(xhr["mensagem"]);

        if (xhr["link"]) {
            window.location.href = xhr["link"];
        }
    }
}

function atualizarInterfaceComDados(xhr) {
    $(".card-minuta").html(xhr["html-card-minuta"]);
    $(".card-despesa").html(xhr["html-card-despesas"]);
    $(".card-entrega").html(xhr["html-card-entregas"]);
    $(".card-checklist").html(xhr["html-card-checklist"]);
    $(".card-receitas").html(xhr["html-card-receitas"]);
    $(".card-capacidade").html(xhr["html-card-capacidade"]);
    $(".card-perimetro").html(xhr["html-card-perimetro"]);
    verificaChecklist();
    verificaCheckboxClasse("total-recebe");
    calcularTotais("recebe");
    mostraChecklist();
}

$(document).on("click", "#chk-perimetro", function(event) {
    if ($("#chk-perimetro").is(":checked")) {
        $(".js-perimetro-hide").hide();
        $("#nota").val("PERIMETRO");
        $("#bairro").focus();
    } else {
        $(".js-perimetro-hide").show();
        $("#nota").val("");
        $("#nota").focus();
    }
});

$(document).on("click", "#chk-saida", function(event) {
    if ($("#chk-saida").is(":checked")) {
        $("#nota").val($("#label-chk-saida").data("saida"))
        $("#valor_nota").focus();
    } else {
        $("#nota").val("")
        $("#nota").focus();
    }
});

$(document).on("click", ".filtro-consulta", function() {
    var filtro = $(this).attr("data-filtro")
    var filtro_consula = $(this).data("filtro-consulta")
    var meses = $(this).data("meses")
    var anos = $(this).data("anos")

    executarAjax("/minutas/filtraminuta", "GET", {
        Filtro: filtro,
        FiltroConsulta: filtro_consula,
        Meses: meses,
        Anos: anos,
    }, function(data) {
        $(".card-minutas-consulta").html(data["html_filtra_minuta"])
        $(".card-minutas-consulta").show()
        // $(".filtro-lista").each(function() {
            // $(this).addClass("i-button")
        // });
        // $(this).removeClass("filtro-consulta")
        // $(this).removeClass("i-button")
        // $(this).addClass("i-button-null")
        $(".card-minutas-abertas").hide();
        $(".card-minutas-concluidas").hide();
        $(".card-minutas-fechadas").hide();
    });
});

$(document).on("click", ".filtro-periodo", function() {
    var filtro = $(this).data("filtro")
    var filtro_consula = $(this).data("filtro-consulta")
    var meses = $(this).data("meses")
    var anos = $(this).data("anos")
    var menu_selecionado = $(this)

    executarAjax("/minutas/filtraminuta", "GET", {
        Filtro: filtro,
        FiltroConsulta: filtro_consula,
        Meses: meses,
        Anos: anos,
    }, function(data) {
        $(".card-minutas-consulta").html(data["html_filtra_minuta"])
        $(".filtro-periodo").each(function() {
            if ($(this).text() == menu_selecionado.text()) {
                $(this).removeClass("i-button")
            } else {
                $(this).addClass("i-button")
            }
        });
    });
});


function formatMask() {
    $(".js-decimal").each(function() {
        $(this).mask("#.##0,00", { reverse: true })
        if ($(this).attr("id") == "tabela-seguro-recebe") {
            $(this).mask("#.##0,000", { reverse: true })
        }
    });
    $(".js-unidade").each(function() {
        $(this).mask("#.##0", { reverse: true })
    });
    $(".total-recebe").mask("#.##0,00", { reverse: true })
    $(".total-paga").mask("#.##0,00", { reverse: true })
}

function formatUnmask() {
    $(".js-decimal").each(function() {
        $(this).unmask()
    });
    $(".js-unidade").each(function() {
        $(this).unmask()
    });
    $(".total-recebe").unmask()
    $(".total-pagamentos").unmask()
}

$(document).on("click", ".js-gerenciar-romaneio-minuta", function() {
    var id_romaneio = $(this).data("id_romaneio")
    var id_minuta = $(this).data("id_minuta")
    var acao = $(this).data("acao")

    executarAjax("/minutas/gerenciar_romaneio_minuta", "GET", {
        id_romaneio: id_romaneio,
        id_minuta: id_minuta,
        acao: acao,
    }, function(data) {
        atualizaAposEntregaAlterada(data)
    });
});

$(document).on("change", ".js-checkbox-paga", function() {
    var div_mostra = $(this).attr("id").replace("check", "#js");
    var visible = $(div_mostra).is(":visible")
    var input_tabela = $(this).attr("id").replace("check", "#tabela");
    var input_valor = $(this).attr("id").replace("check", "#valor");
    $(div_mostra).slideToggle(500)
    if (visible) {
        $(input_valor).val("0,00")
    } else {
        var valor_digitado = $(input_tabela).val()
        calculosMudarInputPaga(input_tabela.replace("#", ""), valor_digitado)
        $(input_tabela).select()
    }
})

$(document).on("change", ".js-checkbox-recebe", function() {
    var div_mostra = $(this).attr("id").replace("chk", "#row");
    var visible = $(div_mostra).is(":visible")
    var input_tabela = $(this).attr("id").replace("chk", "#tabela");
    var input_valor = $(this).attr("id").replace("chk", "#valor");
    if (visible) {
        $(div_mostra).addClass("hidden")
        $(input_valor).val("0,00")
    } else {
        $(div_mostra).removeClass("hidden")
        var valor_digitado = $(input_tabela).val()
        calculosMudarInputRecebe(input_tabela.replace("#", ""), valor_digitado)
        $(input_tabela).select()
    }
})

$(document).on("click", ".js-remover-entrega-minuta", function(event) {
    var id_minuta = localStorage.getItem("idminuta")
    var id_minuta_notas = $(this).data("id_minuta_notas")

    executarAjax("/minutas/remover_entrega", "GET", {
        id_minuta: id_minuta,
        id_minuta_notas: id_minuta_notas,
    }, function(data) {
        atualizaAposEntregaAlterada(data)
    });
});

$(document).on("click", ".lista-consulta", function(event) {
    $(".lista-consulta").each(function() {
        $(this).removeClass("bi-caret-down").addClass("bi-caret-right");
    });
    $(this).removeClass("bi-caret-right").addClass("bi-caret-down");
    var filtro = ".filtro-" + $(this).data("filtro") + "-lista"
    if ($(filtro).is(":visible")) {
        $(filtro).hide();
        $(this).removeClass("bi-caret-down").addClass("bi-caret-right");
    } else {
        $(".filtro-cliente-lista").hide();
        $(".filtro-colaborador-lista").hide();
        $(".filtro-veiculo-lista").hide();
        $(".filtro-entrega-cidade-lista").hide();
        if ($(this).data("filtro") == "cliente") {
            $(".filtro-cliente-lista").show();
        } else if ($(this).data("filtro") == "colaborador") {
            $(".filtro-colaborador-lista").show();
        } else if ($(this).data("filtro") == "veiculo") {
            $(".filtro-veiculo-lista").show();
        } else if ($(this).data("filtro") == "entrega-cidade") {
            $(".filtro-entrega-cidade-lista").show();
        }
    }
});

function mostraChecklist() {
    $(".card-checklist").slideDown(500)
    $(".chk-red").each(function() {
        $(".js-conclui-minuta").slideUp(500)
    })
    $(".chk-red-gera-paga").each(function() {
        $(".js-conclui-minuta").slideUp(500)
    });
}

function somaMotorista() {
    var valor_paga = 0.00;
    $(".total-paga").each(function() {
        if ($(this).attr("id") != "valor-ajudante-paga") {
            valor_paga += parseFloat($(this).val().replace(".", "").replace(",", "."))
        }
    });
    $("#total-motorista").text(valor_paga.toFixed(2))
    if (valor_paga > 0) {
        $(".div-motorista").slideDown(500)
    } else {
        $(".div-motorista").slideUp(500)
    }
    $("#total-motorista").unmask()
    $("#total-motorista").mask("#.##0,00", { reverse: true })
    var text_total = $("#total-motorista").text();
    var text_total = "R$ " + text_total
    $("#total-motorista").text(text_total)
}

/**
 * Verifica e atualiza o status dos checkboxes e elementos relacionados
 * com base no valor de inputs associados.
 *
 * Para cada elemento com da classe fornecida, a função faz o seguinte:
 * 1. Obtém o ID do checkbox e da linha da tabela correspondente, com base
 *    no nome do input.
 * 2. Verifica o estado do checkbox (se está marcado ou não).
 * 3. Se o checkbox estiver marcado e o valor do input for maior que 0,
 *    mantém o checkbox marcado e exibe a linha correspondente.
 * 4. Se o valor for 0 ou menor, desmarca o checkbox, oculta a linha e
 *    realiza uma animação de recolhimento para elementos com a classe
 *    `.body-row`.
 * 5. Se o checkbox não estiver marcado, define o valor do input como 0,
 *    desmarca o checkbox, oculta a linha correspondente e recolhe a linha
 *    com animação.
 *
 * A função é flexível para funcionar com qualquer classe, bastando passar
 * o nome da classe como parâmetro.
 *
 * @param {string} classe - O nome da classe dos elementos a serem verificados
 * (por exemplo, 'total-recebe' ou 'total-paga').
 *
 * A animação de recolhimento das linhas `.body-row` é realizada com um efeito de slide.
 */
function verificaCheckboxClasse(classe) {
    $("." + classe).each(function() {
        var checkbox_id = $(this).attr("name").replace("total", "#chk");
        var div_row_id = $(this).attr("name").replace("total", "#row");
        var body_item_class = $(this).attr("name").replace("total", ".body-row");
        var checkbox_status = $(checkbox_id).attr("checked");

        if (checkbox_status == "checked") {
            if (parseFloat($(this).val()) > 0) {
                $(checkbox_id).prop("checked", true)
                $(div_row_id).removeClass("hidden")
            } else {
                $(checkbox_id).prop("checked", false)
                $(div_row_id).addClass("hidden")
                $(body_item_class).slideUp(500)
            }
        } else {
            $(this).val(0.00)
            $(checkbox_id).prop("checked", false)
            $(div_row_id).addClass("hidden")
            $(body_item_class).slideUp(500)
        }
    });
};

$(document).on("input", "#periodo-inicial", function(event) {
    $("#print-minutas-periodo").prop('href', function() {
        var href = $("#print-minutas-periodo").prop('href');
        var url = new URL(href);
        url.searchParams.set('inicial', $("#periodo-inicial").val());
        $("#print-minutas-periodo").attr("href", url.toString());
    });
});

$(document).on("input", "#periodo-final", function(event) {
    $("#print-minutas-periodo").prop('href', function() {
        var href = $("#print-minutas-periodo").prop('href');
        var url = new URL(href);
        url.searchParams.set('final', $("#periodo-final").val());
        $("#print-minutas-periodo").attr("href", url.toString());
    });
});

$(document).on("input", "#cliente", function(event) {
    $("#print-minutas-periodo").prop('href', function() {
        var href = $("#print-minutas-periodo").prop('href');
        var url = new URL(href);
        url.searchParams.set('cliente', $("#cliente").val());
        $("#print-minutas-periodo").attr("href", url.toString());
    });
});

$(document).on("click", ".js-consulta-minuta", function() {
    var idminuta = $(this).data("idminuta")
    $.ajax({
        type: "GET",
        url: "/minutas/minuta_cards",
        data: {
            idminuta: idminuta,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-entrega").html(data["html_entrega"])
            $(".card-romaneio").html(data["html_romaneio"])
            $(".box-loader").hide()
        },
    });
});


const calculosMinuta = {
    "taxa_expedicao": {
        funcao: "calcularMultiplo",
    },
    "seguro": {
        funcao: "calcularPorcentagem"
    },
    "porcentagem_nota": {
        funcao: "calcularPorcentagem"
    },
    "porcentagem_nota_extra": {
        funcao: "calcularPorcentagemHora"
    },
    "hora": {
        funcao: "calcularHora"
    },
    "hora_extra": {
        funcao: "calcularPorcentagemHora"
    },
    "quilometragem": {
        funcao: "calcularMultiplo"
    },
    "quilometragem_extra": {
        funcao: "calcularPorcentagemHora"
    },
    "entregas": {
        funcao: "calcularMultiplo"
    },
    "entregas_extra": {
        funcao: "calcularPorcentagemHora"
    },
    "saida": {
        funcao: "calcularMultiplo"
    },
    "saida_extra": {
        funcao: "calcularPorcentagemHora"
    },
    "capacidade_peso": {
        funcao: "calcularMultiplo"
    },
    "capacidade_peso_extra": {
        funcao: "calcularPorcentagemHora"
    },
    "entregas_quilos": {
        funcao: "calcularMultiplo"
    },
    "entregas_quilos_extra": {
        funcao: "calcularPorcentagemHora"
    },
    "entregas_volume": {
        funcao: "calcularMultiplo"
    },
    "entregas_volume_extra": {
        funcao: "calcularPorcentagemHora"
    },
    "perimetro": {
        funcao: "calcularPorcentagem"
    },
    "perimetro_extra": {
        funcao: "calcularPorcentagemHora"
    },
    "pernoite": {
        funcao: "calcularPorcentagem"
    },
    "ajudante": {
        funcao: "calcularMultiplo"
    },
}

function formatarNumero(valor, casasDecimais) {
    valor = valor.replace(/\./g, '').replace(',', '.');
    valor = parseFloat(valor)
    valorFormatado = valor.toLocaleString("pt-BR", {
        minimumFractionDigits: casasDecimais,
        maximumFractionDigits: casasDecimais
    });
    return valorFormatado
}

function formatarInicial() {
    $(".js-decimal, .js-inteiro, .total-recebe, .total-paga").each(function() {
        formatarInput($(this));
    });
}

function formatarInput(input) {
    var casasDecimais = 2;

    if (input.hasClass("js-decimal")) {
        if (input.attr("name") === "tabela-seguro-recebe" || 
            input.attr("name") === "minuta-entregas_quilos-recebe" || 
            input.attr("name") === "minutas-entregas_quilos-paga") {
            casasDecimais = 3;
        }
    } else if (input.hasClass("js-inteiro")) {
        casasDecimais = 0;
    }

    input.val(formatarNumero(input.val(), casasDecimais));   
}

$(document).on("change", ".js-input-change", function() {
    const stringPartes = $(this).attr("name").split("-");
    const tipoCalculo = stringPartes[1];
    const padrao = stringPartes[2];
    const calculo = calculosMinuta[tipoCalculo];

    if (calculo && typeof window[calculo.funcao] === "function") {

        let tabela = $(`#tabela-${tipoCalculo}-${padrao}`).val();
        tabela = tabela.replace(/\./g, '').replace(',', '.');
        let minuta = $(`#minuta-${tipoCalculo}-${padrao}`).val();
        if ($(this).attr("type") == "text") {
            minuta = minuta.replace(/\./g, '').replace(',', '.');
        }
        let base = null;

        if (tipoCalculo.includes("_extra")) {
            const elementoBase = tipoCalculo.replace("_extra", "")
            base = $(`#total-${elementoBase}-${padrao}`).val()
            base = base.replace(/\./g, '').replace(',', '.');
            
        }

        const resultado = window[calculo.funcao]({tabela, minuta, base});
        
        $(`#total-${tipoCalculo}-${padrao}`).val(
            resultado.toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
                maximumFractionDigits:2
            })
        );
    }
    calcularTotais(padrao)
});

$(document).on("change", ".js-decimal, .js-inteiro", function() {
    formatarInput($(this));
});

function calcularPorcentagem({tabela, minuta}) {
    return (parseFloat(tabela) * parseFloat(minuta)) / 100;
}

function calcularHora({tabela, minuta}) {
    const [horas, minutos] = minuta.split(":").map(num => parseInt(num, 10));

    if (isNaN(horas) || isNaN(minutos)) {
        return 0;
    }

    const valorHora = parseFloat(tabela) / 10
    const valorMinuto = valorHora / 60

    return (valorHora * horas) + (valorMinuto * minutos)
}

function calcularPorcentagemHora({tabela, minuta, base}) {
    const [horas, minutos] = minuta.split(":").map(num => parseInt(num, 10));

    if (isNaN(horas) || isNaN(minutos) || !base) {
        return 0;
    }

    const valorHora = parseFloat(base) / 10
    const valorMinuto = valorHora / 60

    return (((valorHora * horas) + (valorMinuto * minutos)) / 100) * parseFloat(tabela)
}

function calcularMultiplo({tabela, minuta}) {
    return parseFloat(tabela) * parseFloat(minuta)
}

function calcularTotais(padrao) {
    let valorTotal = 0.00;
    let basePerimetroPernoite = 0.00;


    $(`.total-${padrao}`).each(function() {
        const checkboxId = $(this).attr("name").replace("total", "#chk");
        const checkboxStatus = $(checkboxId).prop("checked");

        if (checkboxStatus) {
            const valorItem = $(this).val().replace(/\./g, '').replace(',', '.');

            valorTotal += parseFloat(valorItem);

            if ($(this).hasClass(`total-phkesc-${padrao}`)) {
                basePerimetroPernoite += parseFloat(valorItem);
            }
            
        }
    });

    const valorTotalFormatado = valorTotal.toLocaleString("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    const valorBaseFormatado = basePerimetroPernoite.toLocaleString("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    $(`#minuta-perimetro-${padrao}`).val(valorBaseFormatado)
    $(`#minuta-pernoite-${padrao}`).val(valorBaseFormatado)
    $(`#saldo-${padrao}`).text("R$ " + valorTotalFormatado)

    if (padrao == "recebe") {
        $("#total-minuta").val(valorTotal)   
    }
}

function atualizaAposMinutaAlterada(data) {
    $(".card-minuta").html(data["html-card-minuta"])
    $(".card-checklist").html(data["html-card-checklist"])
    atualizaAposComum(data)
}

function atualizaAposEntregaAlterada(data) {
    $(".card-romaneio").html(data["html-card-romaneios"])
    $(".card-entrega").html(data["html-card-entregas"])
    atualizaAposComum(data)
}

function atualizaAposDespesaAlterada(data) {
    $(".card-despesa").html(data["html-card-despesas"])
    atualizaAposComum(data)
}

function atualizaAposComum(data) {
    $(".card-receitas").html(data["html-card-receitas"])
    $(".card-capacidade").html(data["html-card-capacidade"])
    $(".card-perimetro").html(data["html-card-perimetro"])
    exibirMensagem(data["mensagem"])
    verificaChecklist()
    verificaCheckboxClasse("total-recebe")
    if ($(".status-minuta").text() != "FECHADA") {
        calcularTotais("recebe");
    }
}

function verificaChecklist() {
    if ($(".chk-red").length == 0) {
        $("#btn-concluir-minuta").show()
        $("#btn-finalizar-minuta").show()
    } else {
        $("#btn-concluir-minuta").hide()
        $("#btn-finalizar-minuta").hide()
    }
}

function toggleButton() {
    if ($(".status-minuta").text() != "ABERTA") {
        $(".i-button").each(function() {
            $(this).addClass("disabled")
            $("#btn-estornar-concluir").removeClass("disabled")
            $("#btn-finalizar-minuta").removeClass("disabled")
            $("#btn-estornar-finalizar").removeClass("disabled")
            $(".js-alterar-capacidade").removeClass("disabled")
            $(".js-alterar-perimetro").removeClass("disabled")
        });
    } else {
        $(".disabled").removeClass("disabled");
    }
}
