$(document).ready(function() {
    CarregaMask()
    $(".body-multa").hide()
    $(".js-oculta-body-multa").hide()
})

var CarregaMask = function() {
    $("#linha1").mask('#####.##### #####.###### #####.######');
    $("#linha2").mask('# ##############');
    $("#linhasp1").mask('###########.# ###########.#');
    $("#linhasp2").mask('###########.# ###########.#');
}

$(document).on('submit', '.js-gera-multas', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: '/despesas/adiciona_multa',
        data: $(this).serialize(),
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-multas").html(data.html_form_multas)
            $(".card-multas-pagar").html(data.html_multas_pagar)
            $('.card-minutas-multa').html('')
            CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-filtro-motorista', function() {
    var idpessoal = $("#select-motorista").val()
    $.ajax({
        type: "GET",
        url: "/despesas/filtro_motorista",
        data: {
            idpessoal: idpessoal,
        },
        beforeSend: function() {
            $(".box-loader").hide();
        },
        success: function(data) {
            $(".box-loader").show();
        },
    });
});

$(document).on('submit', '.js-gera-despesas', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: '/despesas/adiciona_despesa',
        data: $(this).serialize(),
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-despesas").html(data.html_form_despesas)
                // $(".card-multas-pagar").html(data.html_multas_pagar)
                // $('.card-minutas-multa').html('')
            CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('submit', '.js-gera-categorias', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: '/despesas/adiciona_categoria',
        data: $(this).serialize(),
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-categoria").html(data.html_form_categorias)
                // $(".card-multas-pagar").html(data.html_multas_pagar)
                // $('.card-minutas-multa').html('')
            CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('submit', '.js-gera-subcategorias', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: '/despesas/adiciona_subcategoria',
        data: $(this).serialize(),
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-subcategoria").html(data.html_form_subcategorias)
                // $(".card-multas-pagar").html(data.html_multas_pagar)
                // $('.card-minutas-multa').html('')
            CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('change', '.js-categoria', function() {
    var _id_categoria = $(this).val()
    $.ajax({
        type: 'GET',
        url: '/despesas/carrega_subcategoria',
        data: {
            idcategoria: _id_categoria,
        },
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(data) {
            $("#subcategoria").html(data.html_choice_subcategorias)
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-edita-multas', function() {
    var _id_multa = $(this).data('idmulta')
    $.ajax({
        type: 'GET',
        url: '/despesas/edita_multa',
        data: {
            idMulta: _id_multa,
        },
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-multas").html(data.html_form_multas)
            $(".card-multas-pagar").html(data.html_multas_pagar)
            $('.card-minutas-multa').html(data.html_minutas_multa)
            CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-exclui-multas', function() {
    var _id_multa = $(this).data('idmulta')
    $.ajax({
        type: 'GET',
        url: '/despesas/exclui_multa',
        data: {
            idMulta: _id_multa,
        },
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".card-multas-pagar").html(data.html_multas_pagar)
            $('.box-loader').hide()

        },
    });
});

$(document).on('focusout', '#hora', function() {
    var _id_veiculo = $("#veiculo option:selected").val();
    var _date = $('#data').val();
    var _hora = $('#hora').val();
    if (_id_veiculo != '') {
        $.ajax({
            type: 'GET',
            url: '/despesas/minutas_multa',
            data: {
                idveiculo: _id_veiculo,
                date: _date,
                hora: _hora,
            },
            beforeSend: function() {
                $('.card-minutas-multa').fadeOut(10)
            },
            success: function(data) {
                $('#idpessoal').val(data.idpessoal)
                $('.card-minutas-multa').html(data.html_minutas_multa)
                $('.card-minutas-multa').fadeIn(10)
            },
        });
    }
});


function openMyModal(event) {
    var modal = initModalDialog(event, '#MyModal');
    var url = $(event.target).data('action');
    $.ajax({
        type: "GET",
        url: url,
        data: {}
    }).done(function(data, textStatus, jqXHR) {
        modal.find('.modal-body').html(data.html_form);
        modal.modal('show');
        formAjaxSubmit(modal, url, null, null);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        alert("SERVER ERROR: " + errorThrown);
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
        $.ajax({
            type: $(this).attr('method'),
            url: url,
            idobj: $(this).attr('idobj'),
            data: $(this).serialize(),
            success: function(xhr, ajaxOptions, thrownError) {
                $(modal).find('.modal-body').html(xhr['html_form']);
                if ($(xhr['html_form']).find('.errorlist').length > 0) {
                    formAjaxSubmit(modal, url, cbAfterLoad, cbAfterSuccess);
                } else {
                    $(modal).modal('hide');
                    $(".fp-base").html(xhr.html_folha)
                    $(".fp-contracheque").html("");
                    $(".fp-contracheque").html(xhr.html_contracheque);
                    $(".fp-cartaoponto").html("");
                    $(".fp-cartaoponto").html(xhr.html_cartaoponto);
                    $(".fp-adiantamento").html("");
                    $(".fp-adiantamento").html(xhr.html_formccadianta);
                    $(".fp-minutas").html("");
                    $(".fp-minutas").html(xhr.html_minutascontracheque);
                    $(".fp-vales").html("");
                    $(".fp-vales").html(xhr.html_vales);
                    if (xhr.html_adiantamento == true) {
                        $(".fp-adiantamento").hide();
                    }
                    if (cbAfterSuccess) { cbAfterSuccess(modal); }
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                console.log('SERVER ERROR: ' + thrownError);
            },
            complete: function() {
                header.removeClass('loading');
            }
        });
    });
}

$(document).on('click', '.js-mostra-body-multa', function() {
    $(".body-multa").show()
    $(".js-mostra-body-multa").hide()
    $(".js-oculta-body-multa").show()
})

$(document).on('click', '.js-oculta-body-multa', function() {
    $(".body-multa").hide()
    $(".js-mostra-body-multa").show()
    $(".js-oculta-body-multa").hide()
        // LimpaFormNota()
})