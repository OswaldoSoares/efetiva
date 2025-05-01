if (typeof idPessoal !== "undefined") {
    idPessoal = null; // Redefine para null se já existir
} else {
    let idPessoal = null; // Declara como null na primeira carga
}

if (typeof mes !== "undefined") {
    mes = null; // Redefine para null se já existir
} else {
    let mes = null; // Declara como null na primeira carga
}

if (typeof ano !== "undefined") {
    ano = null; // Redefine para null se já existir
} else {
    let ano = null; // Declara como null na primeira carga
}

if (typeof mesAno !== "undefined") {
    mesAno = null; // Redefine para null se já existir
} else {
    let mesAno = null; // Declara como null na primeira carga
}

$(document).on('keydown', 'input.js-decimal, input.js-inteiro', function(e) {
    // Permitir: backspace, delete, setas (esquerda e direita), tab
    if ($.inArray(e.keyCode, [8, 9, 37, 39, 46]) !== -1) {
        return;
    }

    // Se o input possui a classe js-decimal, permitir a vírgula
    if ($(this).hasClass('js-decimal') && e.keyCode == 188) {
        return;
    }

    // Permitir números de 0 a 9
    if ((e.keyCode >= 48 && e.keyCode <= 57) || (e.keyCode >= 96 && e.keyCode <= 105)) {
        return;
    }

    // Impedir qualquer outro caractere
    e.preventDefault();
});

$(".div-sucesso").hide()
$(".div-erro").hide()
$(".box-loader").hide()

// Adiciona ou remove falta do cartão de ponto do colaborador
$(document).on("click", ".js-alterar-falta", function() {
    idCartaoPonto = $(this).data("id_cartao_ponto")

    executarAjax("/pessoas/alterar_falta_colaborador", "GET", {
        id_pessoal: idPessoal,
        id_cartao_ponto: idCartaoPonto,
        mes: mes,
        ano: ano,
    }, function(data) {
        $(".card-cartao-ponto-colaborador").html(data["html-card-cartao-ponto-colaborador"]);
        exibirMensagem(data["mensagem"])
        $('.box-loader').hide()
    });
});

// Adiciona ou remove condução do cartão de ponto do colaborador
$(document).on("click", ".js-alterar-conducao", function() {
    idCartaoPonto = $(this).data("id_cartao_ponto")

    executarAjax("/pessoas/alterar_conducao_colaborador", "GET", {
        id_pessoal: idPessoal,
        id_cartao_ponto: idCartaoPonto,
        mes: mes,
        ano: ano,
    }, function(data) {
        $(".card-cartao-ponto-colaborador").html(data["html-card-cartao-ponto-colaborador"]);
        exibirMensagem(data["mensagem"])
        $('.box-loader').hide()
    });
});

// Abona ou desabona falta do cartão de ponto do colaborador
$(document).on("click", ".js-abonar-falta", function() {
    idCartaoPonto = $(this).data("id_cartao_ponto")

    executarAjax("/pessoas/abonar_falta_colaborador", "GET", {
        id_pessoal: idPessoal,
        id_cartao_ponto: idCartaoPonto,
        mes: mes,
        ano: ano,
    }, function(data) {
        $(".card-cartao-ponto-colaborador").html(data["html-card-cartao-ponto-colaborador"]);
        exibirMensagem(data["mensagem"])
        $('.box-loader').hide()
    });
});


function openMyModal(event) {
    const modal = initModalDialog(event, '#MyModal');
    const url = $(event.target).data('action');
    let requestData = {
        title: $(event.target).data("title"),
        id_pessoal: idPessoal,
        mes_ano: mesAno,
    }

    // Verifica se o id_documento está presente
    const idDocumento = $(event.target).data("id_documento");
    if (typeof idDocumento !== "undefined") {
        requestData.id_documento = idDocumento;
    }

    // Verifica se o id_telefone está presente
    const idTelefone = $(event.target).data("id_telefone");
    if (typeof idTelefone !== "undefined") {
        requestData.id_telefone = idTelefone;
    }

    // Verifica se o id_conta está presente
    const idConta = $(event.target).data("id_conta");
    if (typeof idConta !== "undefined") {
        requestData.id_conta = idConta;
    }

    // Verifica se o id_vale está presente
    const idVale = $(event.target).data("id_vale");
    if (typeof idVale !== "undefined") {
        requestData.id_vale = idVale;
    }

    // Verifica se o id_cartao_ponto está presente
    const idCartaoPonto = $(event.target).data("id_cartao_ponto");
    if (typeof idCartaoPonto !== "undefined") {
        requestData.id_cartao_ponto = idCartaoPonto;
        requestData.mes = mes;
        requestData.ano = ano;
    }

    // Verifica se o id_salario está presente
    const idSalario = $(event.target).data("id_salario");
    if (typeof idSalario !== "undefined") {
        requestData.id_salario = idSalario;
    }

    // Verifica se o id_transporte está presente
    const idTransporte = $(event.target).data("id_transporte");
    if (typeof idTransporte !== "undefined") {
        requestData.id_transporte = idTransporte;
    }

    // Verifica se o id_contra_cheque está presente
    const idContraCheque = $(event.target).data("id_contra_cheque");
    if (typeof idContraCheque !== "undefined") {
        requestData.id_contra_cheque = idContraCheque;
    }

    // Caso seja para criar um novo colaborador oculta cards
    if ($(event.target).data("title") == "ADICIONAR COLABORADOR") {
        $(".card-foto-colaborador").hide();
        $(".card-cartao-ponto-colaborador").hide();
        $(".card-contra-cheque-colaborador").hide();
        $(".card-rescisao-colaborador").hide();
        $(".card-eventos-rescisorios-colaborador").hide();
        $(".card-vales-colaborador").hide();
        $(".card-decimo-terceiro-colaborador").hide();
        $(".card-ferias-colaborador").hide();
        $(".card-docs-colaborador").hide();
        $(".card-fones-colaborador").hide();
        $(".card-contas-colaborador").hide();
        $(".card-salario-colaborador").hide();
    }

    executarAjax(url, "GET", requestData, function(data) {
        modal.find(".modal-body").html(data.modal_html);
        modal.modal("show");

        formAjaxSubmit(modal, url);
    }, function(errorThrown) {
        console.log(errorThrown)
    });
}

function initModalDialog(event, modal_element) {
    var modal = $(modal_element);
    var target = $(event.target);
    var title = target.data('title') || '';
    var subtitle = target.data('subtitle') || '';
    var dialog_class = (target.data('dialog-class') || '') + ' modal-dialog';
    var icon_class = (target.data('icon') || 'fa-laptop') + ' fa modal-icon';
    var button_save_label = target.data('button-save-label') || 'Save changes';
    modal.find('.modal-dialog').attr('class', dialog_class);
    modal.find('.modal-title').text(title);
    modal.find('.modal-subtitle').text(subtitle);
    modal.find('.modal-header .title-wrapper i').attr('class', icon_class);
    modal.find('.modal-footer .btn-save').text(button_save_label);
    modal.find('.modal-body').html('');
    modal.data('target', target);
    return modal;
}

function atualizarInterfaceComDados(xhr) {
    $(".card-colaboradores").html(xhr["html-card-colaboradores"]);
    $(".card-foto-colaborador").html(xhr["html-card-foto-colaborador"]);
    $(".card-cartao-ponto-colaborador").html(xhr["html-card-cartao-ponto-colaborador"]);
    $(".card-vales-colaborador").html(xhr["html-card-vales-colaborador"]);
    $(".card-docs-colaborador").html(xhr["html-card-docs-colaborador"]);
    $(".card-fones-colaborador").html(xhr["html-card-fones-colaborador"]);
    $(".card-contas-colaborador").html(xhr["html-card-contas-colaborador"]);
    $(".card-salario-colaborador").html(xhr["html-card-salario-colaborador"]);
    $(".card-vale-transporte-colaborador").html(xhr["html-card-vale-transporte-colaborador"]);
    // Nos módulos Pessoal e Pagamentos
    $(".card-contra-cheque-colaborador").html(xhr["html-card-contra-cheque-colaborador"]);
    $(".card-contra-cheque-colaborador").show();
}

function formAjaxSubmit(modal, action, cbAfterLoad, cbAfterSuccess) {
    var form = modal.find('.modal-body form');
    var header = $(modal).find('.modal-header');
    var btn_save = modal.find('.modal-footer .btn-save');
    if (btn_save) {
        modal.find('.modal-body form .form-submit-row').hide();
        btn_save.off().on('click', function(event) {
            modal.find('.modal-body form').submit();
        });
    }
    if (cbAfterLoad) { cbAfterLoad(modal); }
    modal.find('form input:visible').first().focus();
    $(form).on('submit', function(event) {
        event.preventDefault();
        header.addClass('loading');
        var url = $(this).attr('action') || action;
        var formData = new FormData($('.rows').get(0));  
        console.log(formData)      
        $.ajax({
            type: $(this).attr('method'),
            url: url,
            formData: formData,
            data: $(this).serialize(),
            beforeSend: function() {
                $(".box-loader").show()
            },
            success: function(xhr, ajaxOptions, thrownError) {
                $(modal).find('.modal-body').html(xhr['html_form']);
                if ($(xhr['html_form']).find('.errorlist').length > 0) {
                    formAjaxSubmit(modal, url, cbAfterLoad, cbAfterSuccess);
                } else {
                    $(modal).modal('hide');
                    console.log(xhr)
                    if (xhr["html_card_folha_pagamento"]) {
                        $(".card-folha-pagamento").html(xhr["html_card_folha_pagamento"])
                    }
                    if (xhr["html_cartao_ponto"]) {
                        $(".card-cartao-ponto").html(xhr["html_cartao_ponto"])
                        $(".card-contra-cheque").hide()
                        $(".body-funcionario-pagamento").hide()
                    }
                    if (xhr["html_vales_colaborador"]) {
                        $(".card-vales-colaborador").html(xhr["html_vales_colaborador"])
                    }
                    if (xhr["html_contra_cheque"]) {
                        $(".card-contra-cheque").html(xhr["html_contra_cheque"])
                        $(".card-contra-cheque").show()
                        $("#submit-contracheque").hide()
                    }
                    if (xhr["html_files_contra_cheque"]) {
                        $(".card-files-contra-cheque").html(xhr["html_files_contra_cheque"])
                        $(".card-files-contra-cheque").show()
                    }
                    if (xhr["html_agenda"]) {
                        $(".card-agenda").html(xhr["html_agenda"])
                        $(".card-agenda").show()
                        $(".submit-agenda").hide();
                    }
                    if (cbAfterSuccess) { 
                        cbAfterSuccess(modal);
                    }
                }
                $('.box-loader').hide()
            },
            error: function(xhr, ajaxOptions, thrownError) {
                // $(".mensagem-erro").text(thrownError);
                // mostraMensagemErro()
            },
            complete: function() {
                header.removeClass('loading');
            }
        });
    });
}

if ($(window).width() <= 800) {
    $(".menu-nav-icons").css('display', 'none')
    $(".menu-dots").css('display', 'block')
    $(".container").css('margin-top', '0')
} else {
    $(".container").css('margin-top', '79px')
};

$(document).on('click', '#menu-dots', function() {
    if ($(".menu-nav-icons").is(':visible')) {
        $(".menu-nav-icons").css('display', 'none')
    } else {
        $(".menu-nav-icons").css('display', 'block')
    };
});

// Função para salvar arquivo de contra-cheque (Módulo Pagamento e Modulo Pessoal)
$(document).on('submit', '.js-file-contra-cheque', function(event) {
    event.preventDefault();
    var formData = new FormData();
    var arquivo = $("#file-contracheque").get(0).files[0]
    var csrf_token = $('input[name="csrfmiddlewaretoken"]').val()
    var mes_ano = localStorage.getItem("mes_ano")
    var idpessoal = localStorage.getItem("idpessoal")
    var idcontracheque = $('input[name="idcontracheque"').val()
    formData.append("arquivo", arquivo);
    formData.append("csrfmiddlewaretoken", csrf_token);
    formData.append("mes_ano", mes_ano);
    formData.append("idpessoal", idpessoal);
    formData.append("idcontracheque", idcontracheque);
    $.ajax({
        type: $(this).attr('method'),
        url: '/pessoas/arquiva_contra_cheque',
        data: formData,
        cache: false,
        processData: false,
        contentType: false,
        enctype: 'multipart/form-data',
        beforeSend: function() {
            $('.box-loader').show()
            $(".card-contra-cheque").hide()
            $(".card-files-contra-cheque").hide()
        },
        success: function(data) {
            $(".card-contra-cheque").html(data["html_contra_cheque"])
            $(".card-contra-cheque").show()
            $('.box-loader').hide()
        },
    });
});

$(document).on('change', '#file-contracheque', function() {
    $("#submit-contracheque").attr('title', "Upload Arquivo: " + $(this).val().match(/[\/\\]([\w\d\s\.\-\(\)]+)$/)[1]);
    $("#label-contracheque").hide()
    $("#submit-contracheque").show()
});

var selecionarValesToggle = function() {
    $(".js-vales-toggle-selecionar").toggleClass("invisivel")
    $(".js-vales-toggle-excluir").toggleClass("invisivel")
    $(".js-adicionar-vale-no-contra-cheque").each(function() {
        const valor = parseFloat($(this).data("valor").replace(",", "."));
        const saldo = parseFloat(String($("#saldo").data("saldo")).replace(",", "."));
        if (valor > saldo) {
            $(this).addClass("disabled")
        } else {
            $(this).removeClass("disabled")
        }
    });
}

$(document).on('click', '.js-adicionar-vale-no-contra-cheque', function() {
    const idVale = $(this).data("id_vale")

    if (idContraCheque) {
        executarAjax("/pessoas/adicionar_vale_no_contra_cheque", "GET", {
            id_vale: idVale,
            //  Variáveis globais
            id_pessoal: idPessoal,
            id_contra_cheque: idContraCheque,
        }, function(data) {
            $(".card-contra-cheque-colaborador").html(
                data["html-card-contra-cheque-colaborador"]
            )
            $(".card-vales-colaborador").html(data["html-card-vales-colaborador"]);
            selecionarValesToggle()
            $(".box-loader").hide()
            exibirMensagem(data["mensagem"])
        });
    }
});

$(document).on('click', '.js-excluir-vale-do-contra-cheque', function() {
    const idContraChequeItem = $(this).data("id_contra_cheque_item")

    if (idContraCheque) {
        executarAjax("/pessoas/excluir_vale_do_contra_cheque", "GET", {
            id_contra_cheque_item: idContraChequeItem,
            //  Variáveis globais
            id_pessoal: idPessoal,
            id_contra_cheque: idContraCheque,
        }, function(data) {
            $(".card-contra-cheque-colaborador").html(
                data["html-card-contra-cheque-colaborador"]
            )
            $(".card-vales-colaborador").html(data["html-card-vales-colaborador"]);
            selecionarValesToggle()
            $(".box-loader").hide()
            exibirMensagem(data["mensagem"])
        });
    }
});

$(document).on("click", ".js-fechar-card-contra-cheque", function() {
    idContraCheque = null
    selecionarValesToggle()
    $(".card-contra-cheque-colaborador").hide()
});
