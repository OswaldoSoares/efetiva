$(document).ready(function() {
    localStorage.setItem("idminuta", $("#id_minuta").data("id"))
    $(".box-loader").hide()
    $(".filtro-dados").hide()
    $(".card-minutas-consulta").hide();
    verificaTotalKms()
    verificaTotalHoras()
    verificaCheckboxPaga();
    verificaCheckboxRecebe();
    mostraChecklist();
    formatMask();
    somaReceitas();
    somaPagamentos();

    /* Versão Nova - Função que envia formulário com os itens de
    recebimento para serem processados pelo servidor */
    $(document).on("submit", "#js-gera-receitas", function(event) {
        event.preventDefault();
        $.ajax({
            type: "POST",
            url: "/minutas/gera_receitas",
            data: $(this).serialize(),
            beforeSend: function() {
                $(".box-loader").show();
                $(".card-recebe").html("")
            },
            success: function(data) {
                console.log(data)
                $(".card-recebe").html(data["html-card-recebe"])
                $(".box-loader").hide();
            },
            error: function(error) {
                $(".mensagem-erro").text(
                    error.status + " " + error.message + " "
                    + "- entre em contato com o administrador do aplicativo."
                );
                $("html, body").scrollTop(0);
                $(".box-loader").hide();
                mostraMensagemErro()
                console.log(error)
            },
        });
    });
    
    /* Versão Nova */
    $(document).on("submit", "#js-gera-pagamentos", function(event) {
        event.preventDefault();
        $.ajax({
            type: "POST",
            url: "/minutas/gera_pagamentos",
            data: $(this).serialize(),
            beforeSend: function() {
                $(".box-loader").show();
                $(".card-minuta").html("");
                $(".card-checklist").html("");
                $(".html-form-paga").html("");
            },
            success: function(data) {
                $(".card-minuta").html(data["html_card_minuta"]);
                $(".card-checklist").html(data["html_card_checklist"]);
                $(".html-form-paga").html(data["html_card_pagamentos"]);
                verificaCheckboxPaga();
                verificaCheckboxRecebe();
                mostraChecklist();
                formatMask();
                somaReceitas();
                somaPagamentos();
                $("html, body").scrollTop(0);
                $(".box-loader").hide();
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Versão Nova //
    $(document).on("click", ".estorna-pagamentos-ajudantes", function(event) {
        var idminuta = $(this).attr("idMinuta")
        $.ajax({
            type: "GET",
            url: "/minutas/estorna_pagamentos_ajudantes",
            data: {
                idminuta: idminuta,
            },
            beforeSend: function() {
                $(".box-loader").show();
            },
            success: function(data) {
                $(".card-minuta").html(data["html_card_minuta"]);
                $(".card-checklist").html(data["html_card_checklist"]);
                $(".html-form-paga").html(data["html_card_pagamentos"]);
                verificaCheckboxPaga();
                verificaCheckboxRecebe();
                mostraChecklist();
                formatMask();
                somaReceitas();
                somaPagamentos();
                $("html, body").scrollTop(0);
                $(".box-loader").hide();
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Última atualização 13/08/2024
    $(document).on("click", ".js-alterar-status-minuta", function(event) {
        var id_minuta = $(this).data("id_minuta")
        var proximo_status = $(this).data("proximo-status")
        $.ajax({
            type: "GET",
            url: "/minutas/alterar_status_minuta",
            data: {
                id_minuta: id_minuta,
                proximo_status: proximo_status,
            },
            beforeSend: function() {
                $(".box-loader").show();
            },
            success: function(data) {
                $(".card-checklist").html(data["html_checklist"]);
                mostraChecklist();
                $(".box-loader").hide();
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Versão Nova //
    $(document).on("click", ".estorna-pagamentos-motorista", function(event) {
        var idminuta = $(this).attr("idMinuta")
        $.ajax({
            type: "GET",
            url: "/minutas/estorna_pagamentos_motorista",
            data: {
                idminuta: idminuta,
            },
            beforeSend: function() {
                $(".box-loader").show();
            },
            success: function(data) {
                $(".card-minuta").html(data["html_card_minuta"]);
                $(".card-checklist").html(data["html_card_checklist"]);
                $(".html-form-paga").html(data["html_card_pagamentos"]);
                verificaCheckboxPaga();
                verificaCheckboxRecebe();
                mostraChecklist();
                formatMask();
                somaReceitas();
                somaPagamentos();
                $("html, body").scrollTop(0);
                $(".box-loader").hide();
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Versão Nova //
    $(document).on("click", ".js-estorna-faturamento", function(event) {
        var idminuta = $(this).data("idminuta")
        $.ajax({
            type: "GET",
            url: "/minutas/estorna_faturamento",
            data: {
                idminuta: idminuta,
            },
            beforeSend: function() {
                $(".box-loader").show();
            },
            success: function(data) {
                $(".card-minuta").html(data["html_card_minuta"]);
                $(".card-checklist").html(data["html_card_checklist"]);
                $(".html-form-paga").html(data["html_card_pagamentos"]);
                $(".card-recebe").html(data["html-card-recebe"])
                verificaCheckboxPaga();
                verificaCheckboxRecebe();
                mostraChecklist();
                formatMask();
                somaReceitas();
                somaPagamentos();
                $("html, body").scrollTop(0);
                $(".box-loader").hide();
            },
            error: function(error) {
                console.log(error)
            }
        });
    });


    // Última atualização 06/08/2024
    $(document).on("click", ".js-excluir-colaborador-minuta", function() {
        var id_minuta = $(this).data("id_minuta")
        var id_minuta_colaborador = $(this).data("id_minuta_colaborador")
        var cargo = $(this).data("cargo")
        $.ajax({
            type: "GET",
            url: "/minutas/excluir_colaborador_minuta",
            data: {
                id_minuta: id_minuta,
                id_minuta_colaborador: id_minuta_colaborador,
                cargo: cargo,
            },
            beforeSend: function() {
                $(".box-loader").show()
            },
            success: function(data) {
                $(".card-minuta").html(data["html-card-minuta"]);
                $(".card-checklist").html(data["html_checklist"]);
                $(".box-loader").hide();
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Versão Nova //
    $(document).on("click", ".js-excluir-despesa-minuta", function(event) {
        var id_minuta = localStorage.getItem("idminuta")
        var id_minuta_itens = $(this).data("id_minuta_itens")
        $.ajax({
            type: "GET",
            url: "/minutas/excluir_despesa",
            data: {
                id_minuta_itens: id_minuta_itens,
                id_minuta: id_minuta,
            },
            beforeSend: function() {
                $(".box-loader").show()
            },
            success: function(data) {
                $(".card-despesa").hide()
                $(".card-despesa").html(data["html_card_despesas"]);
                $(".card-despesa").show()
                $(".box-loader").hide()
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Versão Nova //

    $("#MyModal").on("shown.bs.modal", function() {
        setTimeout(function() { // Delay para função loadCubagem, após janela estar carregada
            $("#id_Propriedade").focus(); // Configura o foco inicial
        }, 800);
        $(".form-radio").click(function() {
            var filtro = $(this).val()
            $.ajax({
                type: "GET",
                url: "/minutas/filtraveiculoescolhido",
                data: {
                    idobj: $("#idminuta").attr("idminuta"),
                    idPessoal: $("#idpessoal").attr("idpessoal"),
                    Filtro: filtro,
                },
                beforeSend: function() {
                    $("#id_veiculo").html("")
                },
                success: function(data) {
                    $("#id_veiculo").html(data["html_filtro"])
                },
                error: function(error) {
                    console.log(error)
                }
            });
        });
    });


    $(".switch").each(function() {
        mostravalores($(this));
    });

    $(".switch").change(function() {
        mostravalores($(this));
    });

    
    $(".demonstrativo-input").change(function() {
        if ($(this).attr("type") != "time") {
            if ($(this).attr("id") == "ta-seguro-recebe") {
                $(this).val(parseFloat($(this).val()).toFixed(3))
            } else {
                $(this).val(parseFloat($(this).val()).toFixed(2))
            }
        };
    });

    $(".demonstrativo-input").change(function() {
        var elemento_alterado = "#sw" + $(this).attr("id").substring(2, 50)
        var obj = $("input").filter(elemento_alterado)
        mostravalores(obj);
    });

    // Versão Antiga //
    $("#mi-ajudante-paga").attr("readonly", "readonly");
    $(".js-criaminuta").click(loadForm);
    $(".js-editaminuta").click(loadForm);
    $(".js-imprimeminuta").click(loadForm);
    $(".js-fechaminuta").click(loadForm);
    $(".js-criaminutamotorista").click(loadForm);
    $(".js-excluiminutamotorista").click(loadForm);
    $(".js-criaminutaajudante").click(loadForm);
    $(".js-excluiminutaajudante").click(loadForm);
    $(".js-editaminutaveiculo").click(loadForm);
    $(".js-criaminutaparametrodespesa").click(loadForm);
    $(".js-excluiminutadespesa").click(loadForm);
    $(".js-criaminutaentrega").click(loadForm);
    $(".js-editaminutaentrega").click(loadForm);
    $(".js-excluiminutaentrega").click(loadForm);
});

function openMyModal(event) {
    var modal = initModalDialog(event, "#MyModal");
    var url = $(event.target).data("action");
    $.ajax({
        type: "GET",
        url: url,
        data: {
            idobj: $(event.target).data("idminuta"),
            idPessoal: $(event.target).data("idpessoal"),

            // Usado no módulo minuta - card_despesa
            id_minuta_itens: $(event.target).data("id_minuta_itens"),
            // Usado no módulo minuta - card entrega
            id_minuta_nota: $(event.target).data("id_minuta_nota"),
        }
    }).done(function(data, textStatus, jqXHR) {
        modal.find(".modal-body").html(data.modal_html);
        modal.modal("show");
        // Usado no módulo minuta - Modal Entrega
        if ($(event.target).action="{% url 'adicionar_entrega' %}") {
            if ($("#chk-perimetro").is(":checked")) {
                $(".js-perimetro-hide").hide();
            }
        }
        formAjaxSubmit(modal, url, null, null);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        $(".mensagem-erro").text(errorThrown);
        mostraMensagemErro()
    });
}

function initModalDialog(event, modal_element) {
    var modal = $(modal_element);
    var target = $(event.target);
    var title = target.data("title") || "";
    var subtitle = target.data("subtitle") || "";
    var dialog_class = (target.data("dialog-class") || "") + " modal-dialog";
    var icon_class = (target.data("icon") || "fa-laptop") + " fa modal-icon";
    var button_save_label = target.data("button-save-label") || "Save changes";
    modal.find(".modal-dialog").attr("class", dialog_class);
    modal.find(".modal-title").text(title);
    modal.find(".modal-subtitle").text(subtitle);
    modal.find(".modal-header .title-wrapper i").attr("class", icon_class);
    modal.find(".modal-footer .btn-save").text(button_save_label);
    modal.find(".modal-body").html("");
    modal.data("target", target);
    return modal;
}

function formAjaxSubmit(modal, action, cbAfterLoad, cbAfterSuccess) {
    var form = modal.find(".modal-body form");
    var header = $(modal).find(".modal-header");
    var btn_save = modal.find(".modal-footer .btn-save");
    if (btn_save) {
        modal.find(".modal-body form .form-submit-row").hide();
        btn_save.off().on("click", function(event) {
            modal.find(".modal-body form").submit();
        });
    }
    if (cbAfterLoad) {
        cbAfterLoad(modal);
    }
    modal.find("form input:visible").first().focus();
    title = modal.find(".modal-title").text();
    $(form).on("submit", function(event) {
        event.preventDefault();
        header.addClass("loading");
        var url = $(this).attr("action") || action;
        $.ajax({
            type: $(this).attr("method"),
            url: url,
            idobj: $(this).attr("idobj"),
            data: $(this).serialize(),
            beforeSend: function() {
                $(".box-loader").show();
            },
            success: function(xhr, ajaxOptions, thrownError) {
                $(modal).find(".modal-body").html(xhr["html_form"]);
                if ($(xhr["html_form"]).find(".errorlist").length > 0) {
                    formAjaxSubmit(modal, url, cbAfterLoad, cbAfterSuccess);
                } else {
                    $(modal).modal("hide");
                    recarregaFinanceiro(xhr["html_pagamento"], xhr["html_recebimento"])
                    $(".card-minuta").hide()
                    $(".card-minuta").html(xhr["html-card-minuta"])
                    $(".card-minuta").show()
                    $(".card-despesa").hide()
                    $(".card-despesa").html(xhr["html_card_despesas"])
                    $(".card-despesa").show()
                    $(".card-entrega").hide()
                    $(".card-entrega").html(xhr["html_card_entregas"])
                    $(".card-entrega").show()
                    $(".card-checklist").hide()
                    $(".card-checklist").html(xhr["html_checklist"])

                    mostraChecklist();
                    if (xhr["link"]) {
                        window.location.href = xhr["link"]
                    } else if (xhr["c_view"] == "edita_minuta") {
                        $(".mensagem-sucesso").text(xhr["html_mensagem"]);
                        mostraMensagemSucesso()
                        $(".html-cliente-data").hide()
                        $(".html-cliente-data").html(xhr["html_cliente_data"]);
                        $(".html-cliente-data").delay(1000).slideDown(500)
                    } else if (xhr["c_view"] == "insere_minuta_despesa") {
                        $(".mensagem-sucesso").text(xhr["html_mensagem"]);
                        mostraMensagemSucesso()
                        $(".html-despesa").hide()
                        $(".html-despesa").html(xhr["html_despesa"]);
                        $(".html-despesa").delay(1000).slideDown(500)
                        verificaTotalKms()
                    } else if (xhr["c_view"] == "insere_minuta_entrega") {
                        $(".mensagem-sucesso").text(xhr["html_mensagem"]);
                        mostraMensagemSucesso()
                        $(".card-entrega").hide()
                        $(".card-entrega").html(xhr["html_entrega"]);
                        $(".card-entrega").delay(1000).slideDown(500)
                        verificaTotalKms()
                    }
                    if (cbAfterSuccess) { cbAfterSuccess(modal); }
                    $(".box-loader").hide();
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                $(".box-loader").hide();
                $(".mensagem-erro").text(thrownError);
                mostraMensagemErro()
            },
            complete: function() {
                header.removeClass("loading");
            }
        });
    });
}

// DAQUI PARA BAIXO
// ESTÁ EM ORDEM ALFABETICA E CATALOGADA 19/04/2023

// Utilizado no Card-Entrega (Formulário Modal)
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

// Utilizado no Card-Entrega (Formulário Modal)
$(document).on("click", "#chk-saida", function(event) {
    if ($("#chk-saida").is(":checked")) {
        $("#nota").val($("#label-chk-saida").data("saida"))
        $("#valor_nota").focus();
    } else {
        $("#nota").val("")
        $("#nota").focus();
    }
});

// Utilizado no card-consulta
$(document).on("click", ".filtro-consulta", function(event) {
    var filtro = $(this).attr("data-filtro")
    var filtro_consula = $(this).data("filtro-consulta")
    var meses = $(this).data("meses")
    var anos = $(this).data("anos")
    $.ajax({
        type: "GET",
        url: "/minutas/filtraminuta",
        data: {
            Filtro: filtro,
            FiltroConsulta: filtro_consula,
            Meses: meses,
            Anos: anos,
        },
        beforeSend: function() {
            $(".box-loader").show()
            $(".filtro-lista").each(function() {
                $(this).addClass("i-button")
            });
            $(this).removeClass("filtro-consulta")
            $(this).removeClass("i-button")
            $(this).addClass("i-button-null")
            $(".card-minutas-abertas").hide();
            $(".card-minutas-concluidas").hide();
            $(".card-minutas-fechadas").hide();
        },                
        success: function(data) {
            $(".card-minutas-consulta").html(data["html_filtra_minuta"])
            $(".card-minutas-consulta").show()
            $(".box-loader").hide()
        },
        error: function(error) {
            console.log(error)
        }
    });
});

// Utilizado no card-minutas-consulta
$(document).on("click", ".filtro-periodo", function(event) {
    var filtro = $(this).data("filtro")
    var filtro_consula = $(this).data("filtro-consulta")
    var meses = $(this).data("meses")
    var anos = $(this).data("anos")
    var menu_selecionado = $(this)
    $.ajax({
        type: "GET",
        url: "/minutas/filtraminuta",
        data: {
            Filtro: filtro,
            FiltroConsulta: filtro_consula,
            Meses: meses,
            Anos: anos,
        },
        beforeSend: function() {
            $(".box-loader").show()
            $(".filtro-periodo").each(function() {
                if ($(this).text() == menu_selecionado.text()) {
                    $(this).removeClass("i-button")
                } else {
                    $(this).addClass("i-button")
                }
            });
        },
        success: function(data) {
            $(".card-minutas-consulta").html(data["html_filtra_minuta"])
            $(".box-loader").hide()
        },
        error: function(error) {
            console.log(error)
        }
    })
});

// Utilizada no Card-Minuta - para atualizar data de fechamento da minuta
$(document).on("click", ".js-editar-minuta-hora-final", function() {
    var id_minuta = localStorage.getItem("idminuta")
    var hora_final = $("#id_hora_final").val()
    $.ajax({
        type: "GET",
        url: "/minutas/editar_minuta_hora_final",
        data: {
            id_minuta: id_minuta,
            hora_final: hora_final,           
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-minuta").html(data["html-card-minuta"])
            $(".card-checklist").html(data["html_checklist"])
            $(".mensagem p").removeClass("mensagem-color")
            $(".mensagem p").removeClass("mensagem-error-color")
            $(".mensagem p").addClass("mensagem-success-color")
            exibirMensagem(data["mensagem"])
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

// Utilizada no Card-Minuta - para atualizar km inicial da minuta
$(document).on("click", ".js-editar-minuta-km-inicial", function() {
    var id_minuta = localStorage.getItem("idminuta")
    var km_inicial = $("#id_km_inicial").val()
    $.ajax({
        type: "GET",
        url: "/minutas/editar_minuta_km_inicial",
        data: {
            id_minuta: id_minuta,
            km_inicial: km_inicial,           
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-minuta").html(data["html-card-minuta"])
            $(".card-checklist").html(data["html_checklist"])
            $(".mensagem p").removeClass("mensagem-color")
            $(".mensagem p").removeClass("mensagem-error-color")
            $(".mensagem p").addClass("mensagem-success-color")
            exibirMensagem(data["mensagem"])
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

// Utilizada no Catd-Minuta
// para atualizar km final da minuta
$(document).on("click", ".js-editar-minuta-km-final", function() {
    var id_minuta = localStorage.getItem("idminuta")
    var km_inicial = $("#id_km_inicial").val()
    var km_final = $("#id_km_final").val()

    $.ajax({
        type: "GET",
        url: "/minutas/editar_minuta_km_final",
        data: {
            id_minuta: id_minuta,
            km_inicial: km_inicial,
            km_final: km_final,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-minuta").html(data["html-card-minuta"])
            $(".card-checklist").html(data["html_checklist"])
            $(".mensagem p").removeClass("mensagem-color")
            $(".mensagem p").removeClass("mensagem-error-color")
            $(".mensagem p").addClass("mensagem-success-color")
            exibirMensagem(data["mensagem"])
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

// Utilizado no Card-Receitas e no Card-Pagamentos
// aplica , e . de milhar pt-BR
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

// Utilizado no Card-Receitas e no Card-Pagamentos
// remove , e . de milhar pt-BR
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

// Card Entregas e Card Romaneio
// Última atualização 16/08/2024
$(document).on("click", ".js-gerenciar-romaneio-minuta", function() {
    var id_romaneio = $(this).data("id_romaneio")
    var id_minuta = $(this).data("id_minuta")
    var acao = $(this).data("acao")
    $.ajax({
        type: "GET",
        url: "/minutas/gerenciar_romaneio_minuta",
        data: {
            id_romaneio: id_romaneio,
            id_minuta: id_minuta,
            acao: acao,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-romaneio").html(data["html_card_romaneios"])
            $(".card-romaneio").show()
            $(".card-entrega").html(data["html_card_entregas"])
            $(".card-entrega").show()
            $(".box-loader").hide()
            exibirMensagem(data["mensagem"])
        },
    });
});

// Utilizado no Card-Pagamentos
// Mudança de estado do checkbox
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
    somaPhkescPagamentos();
    somaPagamentos();
})

// Utilizado no Card-Receitas
// Mudança de estado do checkbox
$(document).on("change", ".js-checkbox-recebe", function() {
    var div_mostra = $(this).attr("id").replace("check", "#js");
    var visible = $(div_mostra).is(":visible")
    var input_tabela = $(this).attr("id").replace("check", "#tabela");
    var input_valor = $(this).attr("id").replace("check", "#valor");
    $(div_mostra).slideToggle(500)
    if (visible) {
        $(input_valor).val("0,00")
    } else {
        var valor_digitado = $(input_tabela).val()
        calculosMudarInputRecebe(input_tabela.replace("#", ""), valor_digitado)
        $(input_tabela).select()
    }
    somaPhkescReceitas();
    somaReceitas();
})

// Card Entregas e Card Romaneio
// Atualizado 16/08/2024
$(document).on("click", ".js-remover-entrega-minuta", function(event) {
    var id_minuta = localStorage.getItem("idminuta")
    var id_minuta_notas = $(this).data("id_minuta_notas")
    $.ajax({
        type: "GET",
        url: "/minutas/remover_entrega",
        data: {
            id_minuta: id_minuta,
            id_minuta_notas: id_minuta_notas,
        },
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-entrega").html(data["html_card_entregas"]);
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

// Card Entregas e Card Romaneio
$(document).on("click", ".js-remove-romaneio-minuta", function() {
    var romaneio = $(this).data("romaneio")
    var idminuta = $(this).data("idminuta")
    var idcliente = $(this).data("idcliente")
    $.ajax({
        type: "GET",
        url: "/minutas/remove_romaneio_minuta",
        data: {
            romaneio: romaneio,
            idminuta: idminuta,
            idcliente: idcliente,
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

// Utilizado no card-consulta
// Mostra lista de filtro
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

// Utilizado no card-checklist
// Mostra os itens necessários no checklist
function mostraChecklist() {
    $(".card-checklist").slideDown(500)
    $(".chk-red").each(function() {
        $(".js-conclui-minuta").slideUp(500)
    })
    $(".chk-red-gera-paga").each(function() {
        $(".js-conclui-minuta").slideUp(500)
    });
}

// Mostra a div de mensagem com a mensagem
function exibirMensagem(mensagem) {
    $('.mensagem p').text(mensagem);
    $('.mensagem p').animate({bottom: '0'}, 1000);
    setTimeout(function() {
        $('.mensagem p').animate({bottom: '60px'}, 1000); 
        $('.mensagem p').animate({bottom: '-30px'}, 0);
    }, 5000);
}

// Mostra a div de mensagem com a mensagem de erro
function mostraMensagemErro() {
    $('.mensagem p').animate({bottom: '0'}, 500); /* duração da animação */
    setTimeout(function() {
        $('.mensagem p').animate({bottom: '60px'}, 500); /* duração da animação */
        $('.mensagem p').animate({bottom: '-30px'}, 0); /* duração da animação */
    }, 5000); /* tempo em que a mensagem fica na tela */
}

// Mostra a div de mensagem com a mensagem de sucesso
function mostraMensagemSucesso() {
    $(".div-sucesso").slideDown(500)
    $(".div-sucesso").delay(5000).slideUp(500)
}


// Utilizada no Card-Pagamentps
// Soma valor do motorista
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

// Utilizada no Card-Pagamentos
// Soma total dos pagamentos
function somaPagamentos() {
    var valor_paga = 0.00;
    $(".total-paga").each(function() {
        valor_paga += parseFloat($(this).val().replace(".", "").replace(",", "."))
    });
    $("#total-pagamentos").text(valor_paga.toFixed(2))
    $("#total-pagamentos").unmask()
    $("#total-pagamentos").mask("#.##0,00", { reverse: true })
    $(text_total).unmask()
    $(text_total).mask("#.##0,00", { reverse: true })
    var text_total = $("#total-pagamentos").text();
    var text_total = "R$ " + text_total
    $("#total-pagamentos").text(text_total)
    somaMotorista();
}

// Utilizada no Card-Receitas
// Soma total phkesc pagamentos
function somaPhkescPagamentos() {
    var valor_phkesc = 0.00;
    $(".total-phkesc-paga").each(function() {
        valor_phkesc += parseFloat($(this).val().replace(".", "").replace(",", "."))
    });
    $("#minuta-perimetro-paga").val(valor_phkesc.toFixed(2))
    $("#minuta-perimetro-paga").unmask()
    $("#minuta-perimetro-paga").mask("#.##0,00", { reverse: true })
    if ($("#check-perimetro-paga").is(":checked")) {
        $("#valor-perimetro-paga").val(
            calculaPorcentagem(
                $("#tabela-perimetro-paga").val(),
                $("#minuta-perimetro-paga").val()
            )
        )
    } else {
        $("#valor-perimetro-paga").val("0.00")
    }
    $("#valor-perimetro-paga").unmask()
    $("#valor-perimetro-paga").mask("#.##0,00", { reverse: true })
    $("#minuta-pernoite-paga").val(valor_phkesc.toFixed(2))
    $("#minuta-pernoite-paga").unmask()
    $("#minuta-pernoite-paga").mask("#.##0,00", { reverse: true })
    if ($("#check-perimetro-paga").is(":checked")) {
        $("#valor-pernoite-paga").val(
            calculaPorcentagem(
                $("#tabela-pernoite-paga").val(),
                $("#minuta-pernoite-paga").val()
            )
        )
    } else {
        $("#valor-perimetro-paga").val("0.00")
    }
    $("#valor-pernoite-paga").unmask()
    $("#valor-pernoite-paga").mask("#.##0,00", { reverse: true })
}

// Utilizada no Card-Receitas
// Soma total phkesc receitas
function somaPhkescReceitas() {
    var valor_phkesc = 0.00;
    $(".total-phkesc-recebe").each(function() {
        valor_phkesc += parseFloat($(this).val().replace(".", "").replace(",", "."))
    });
    $("#minuta-perimetro-recebe").val(valor_phkesc.toFixed(2))
    $("#minuta-perimetro-recebe").unmask()
    $("#minuta-perimetro-recebe").mask("#.##0,00", { reverse: true })
    if ($("#check-perimetro-recebe").is(":checked")) {
        $("#valor-perimetro-recebe").val(
            calculaPorcentagem(
                $("#tabela-perimetro-recebe").val(),
                $("#minuta-perimetro-recebe").val()
            )
        )
    } else {
        $("#valor-perimetro-recebe").val("0.00")
    }
    $("#valor-perimetro-recebe").unmask()
    $("#valor-perimetro-recebe").mask("#.##0,00", { reverse: true })
    $("#minuta-pernoite-recebe").val(valor_phkesc.toFixed(2))
    $("#minuta-pernoite-recebe").unmask()
    $("#minuta-pernoite-recebe").mask("#.##0,00", { reverse: true })
    if ($("#check-pernoite-recebe").is(":checked")) {
        $("#valor-pernoite-recebe").val(
            calculaPorcentagem(
                $("#tabela-pernoite-recebe").val(),
                $("#minuta-pernoite-recebe").val()
            )
        )
    } else {
        $("#valor-pernoite-recebe").val("0.00")
    }
    $("#valor-pernoite-recebe").unmask()
    $("#valor-pernoite-recebe").mask("#.##0,00", { reverse: true })
}

// Utilizada no Card-Receitas
// Soma total das receitas
function somaReceitas() {
    var valor_recebe = 0.00;
    $(".total-recebe").each(function() {
        valor_recebe += parseFloat($(this).val().replace(".", "").replace(",", "."))
    });
    $("#total-receitas").text(valor_recebe.toFixed(2))
    $("#total-receitas").unmask()
    $("#total-receitas").mask("#.##0,00", { reverse: true })
    var text_total = $("#total-receitas").text();
    var text_total = "R$ " + text_total
    $("#total-receitas").text(text_total)
}

// Utilizado no Card-Pagamentos
// Mostra inputs dos itens de acordo com o estado do checkbox
function verificaCheckboxPaga() {
    $(".total-paga").each(function() {
        check_altera = $(this).attr("name").replace("valor", "#check");
        div_mostra = $(this).attr("name").replace("valor", "#js");
        if (parseFloat($(this).val()) > parseFloat(0.00)) {
            $(check_altera).prop("checked", true)
            $(div_mostra).slideDown(500)
        } else {
            $(check_altera).prop("checked", false)
            $(div_mostra).slideUp(500)
        }
    });
};

// Utilizado no Card-Pagamentos
// Mostra inputs dos itens de acordo com o estado do checkbox
function verificaCheckboxRecebe() {
    $(".total-recebe").each(function() {
        check_altera = $(this).attr("name").replace("valor", "#check");
        div_mostra = $(this).attr("name").replace("valor", "#js");
        check_true = $(check_altera).attr("checked");
        if (check_true == "checked") {
            if (parseFloat($(this).val()) > parseFloat(0.00)) {
                $(check_altera).prop("checked", true)
                $(div_mostra).slideDown(500)
            } else {
                $(check_altera).prop("checked", false)
                $(div_mostra).slideUp(500)
            }
        } else {
            $(this).val(0.00)
            $(check_altera).prop("checked", false)
            $(div_mostra).slideUp(500)
        }
    });
};

// Utilizada no Card-Minuta
// Mostrra o calculo de horas
function verificaTotalHoras() {
    if ($(".total-horas").text() == "00:00 Hs") {
        $(".calcula-horas").hide()
        $("#id_HoraFinal").val("00:00")
    } else {
        $(".calcula-horas").show()
    }
}

// Utilizada no Card-Minuta
// Mostrra o calculo de Kms
function verificaTotalKms() {
    if ($(".total-kms").text() == "0 KMs") {
        $(".calcula-kms").hide()
        $("#id_KMFinal").val(0)
    } else {
        $(".calcula-kms").show()
    }
}

// Utilizada no Card-Relatorio
// Atualiza parametro href ao alterar data inicial
$(document).on("input", "#periodo-inicial", function(event) {
    $("#print-minutas-periodo").prop('href', function() {
        var href = $("#print-minutas-periodo").prop('href');
        var url = new URL(href);
        url.searchParams.set('inicial', $("#periodo-inicial").val());
        $("#print-minutas-periodo").attr("href", url.toString());
    });
});

// Utilizada no Card-Relatorio
// Atualiza parametro href ao alterar data final
$(document).on("input", "#periodo-final", function(event) {
    $("#print-minutas-periodo").prop('href', function() {
        var href = $("#print-minutas-periodo").prop('href');
        var url = new URL(href);
        url.searchParams.set('final', $("#periodo-final").val());
        $("#print-minutas-periodo").attr("href", url.toString());
    });
});

// Utilizada no Card-Relatorio
// Atualiza parametro href ao alterar o cliente
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
    calculaTotais(padrao)
});
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
