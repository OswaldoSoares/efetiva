$(document).ready(function(){
    $(".down-folha").hide();
    $(".down-avulso").hide();
    $('[data-toggle="tooltip"]').tooltip();
});

$(document).on('change', '#id_MesReferencia', function(event) {
    $(".fp-contrachequeitens").html("");
    $(".fp-folha-contracheque").html("");
    $(".fp-adiantamento").html("");
    $(".fp-adiantamento").hide();
});

$(document).on('change', '#id_AnoReferencia', function(event) {
    $(".fp-contrachequeitens").html("");
    $(".fp-folha-contracheque").html("");
    $(".fp-adiantamento").html("");
    $(".fp-adiantamento").hide();
});

$(document).on('change', '.switchmini', function(event) {
    var idpessoal = '#vale_' + $(this).attr('idPessoal')
    valeselect(idpessoal);
    somavales();
});

$(document).on('submit', '#form-seleciona-folha', function(event) {
    event.preventDefault();
    var url = $(this).attr('action') || action;
    $.ajax({
        type: $(this).attr('method'),
        url: url,
        data: $(this).serialize(),
        beforeSend: function(){
            $(".fp-folha-contracheque").html("");
            $(".fp-adiantamento").hide();
        },
        success: function(data){
            $(".fp-folha-contracheque").html(data.html_folha);
            $(".fp-contrachequeitens").html("");
            $(".fp-adiantamento").hide();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('submit', '.form-cria-contrachequeitens', function(event) {
    event.preventDefault();
    var url = $(this).attr('action') || action;
    $.ajax({
        type: $(this).attr('method'),
        url: url,
        data: $(this).serialize(),
        success: function(data){
            $(".fp-folha-contracheque").html("");
            $(".fp-folha-contracheque").html(data.html_folha)
            $(".fp-contracheque").html("");
            $(".fp-contracheque").html(data.html_contracheque);
            $(".fp-cartaoponto").html("");
            $(".fp-cartaoponto").html(data.html_cartaoponto);
            $(".fp-contrachequeitens").html("");
            $(".fp-contrachequeitens").html(data.html_formccitens);
            $(".fp-adiantamento").html("");
            $(".fp-adiantamento").html(data.html_formccadianta);
            $(".fp-minutas").html("");
            $(".fp-minutas").html(data.html_minutascontracheque);
            $(".fp-vales").html("");
            $(".fp-vales").html(data.html_vales);
            if (data.html_adiantamento == true) {
                $(".fp-adiantamento").hide();
            }
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('submit', '#form-seleciona-periodo', function(event) {
    event.preventDefault();
    var url = $(this).attr('action') || action;
    $.ajax({
        type: $(this).attr('method'),
        url: url,
        data: $(this).serialize(),
        beforeSend: function(){
            
        },
        success: function(data){
          /*  $(".pa-saldo").html("");*/
            $(".pa-saldo-minutas").html(data.html_saldoavulso);
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('submit', '#form-vale', function(event) {
    event.preventDefault();
    var url = $(this).attr('action') || action;
    $.ajax({
        type: $(this).attr('method'),
        url: url,
        data: $(this).serialize(),
        success: function(data){
            if (data.html_vales) {
                $(".fp-vales").html(data.html_vales);
            }
            if (data.html_valesavulso) {
                $(".pa-vales").html(data.html_valesavulso);
            }
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('click', '.remove-item', function(event) {
    var url = $(this).attr('data-url')
    var idcontracheque = $(this).attr('idcontracheque')
    var descricao = $(this).attr('descricao')
    var registro = $(this).attr('registro')
    var mesreferencia = $(this).attr('mesreferencia')
    var anoreferencia = $(this).attr('anoreferencia')
    var idpessoal = $(this).attr('idpessoal')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            idContraCheque: idcontracheque,
            Descricao: descricao,
            Registro: registro,
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        },
        success: function(data){
            $(".fp-folha-contracheque").html("");
            $(".fp-folha-contracheque").html(data.html_folha)
            $(".fp-contracheque").html("");
            $(".fp-contracheque").html(data.html_contracheque);
            $(".fp-cartaoponto").html("");
            $(".fp-cartaoponto").html(data.html_cartaoponto);
            $(".fp-contrachequeitens").html("");
            $(".fp-contrachequeitens").html(data.html_formccitens);
            $(".fp-adiantamento").html("");
            $(".fp-adiantamento").html(data.html_formccadianta);
            $(".fp-minutas").html("");
            $(".fp-minutas").html(data.html_minutascontracheque);
            $(".fp-vales").html("");
            $(".fp-vales").html(data.html_vales);
            if (data.html_adiantamento == true) {
                $(".fp-adiantamento").hide();
            }
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('click', '#gerar-folha', function(event) {
    var url = $(this).attr('data-url')
    var mesreferencia = $(this).attr('mesreferencia')
    var anoreferencia = $(this).attr('anoreferencia')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
        },
        beforeSend: function(){
            $(".fp-folha-contracheque").html("");
            $(".fp-adiantamento").hide();
        },
        success: function(data){
            $(".fp-folha-contracheque").html(data.html_folha);
            $(".fp-adiantamento").hide();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('click', '.selecionar-contracheque', function(event) {
    var url = $(this).attr('data-url')
    var mesreferencia = $(this).attr('mesreferencia')
    var anoreferencia = $(this).attr('anoreferencia')
    var idpessoal = $(this).attr('idpessoal')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        },
        beforeSend: function(){
            $(".fp-contrachequeitens").html("");
            $(".fp-contracheque").html("");
            $(".fp-adiantamento").html("");
            $(".fp-adiantamento").hide();
            $(".fp-cartaoponto").html("");
        },
        success: function(data){
            $(".fp-contrachequeitens").html(data.html_formccitens);
            $(".fp-contracheque").html(data.html_contracheque);
            if (data.html_adiantamento == true) {
                $(".fp-adiantamento").hide();
            } else {
                $(".fp-adiantamento").show();
            }
            $(".fp-adiantamento").html(data.html_formccadianta);
            $(".fp-cartaoponto").html(data.html_cartaoponto);
            $(".fp-minutas").html(data.html_minutascontracheque);
            $(".fp-vales").html("");
            $(".fp-vales").html(data.html_vales);
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('click', '.altera-falta', function(event) {
    var url = $(this).attr('data-url')
    var mesreferencia = $(this).attr('mesreferencia')
    var anoreferencia = $(this).attr('anoreferencia')
    var idpessoal = $(this).attr('idpessoal')
    var idcartaoponto = $(this).attr('idcartaoponto')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
            idCartaoPonto: idcartaoponto,
        },
        success: function(data){
            $(".fp-folha-contracheque").html("");
            $(".fp-folha-contracheque").html(data.html_folha)
            $(".fp-contracheque").html("");
            $(".fp-contracheque").html(data.html_contracheque);
            $(".fp-cartaoponto").html("");
            $(".fp-cartaoponto").html(data.html_cartaoponto);
            $(".fp-adiantamento").html("");
            $(".fp-adiantamento").html(data.html_formccadianta);
            $(".fp-minutas").html("");
            $(".fp-minutas").html(data.html_minutascontracheque);
            $(".fp-vales").html("");
            $(".fp-vales").html(data.html_vales);
            if (data.html_adiantamento == true) {
                $(".fp-adiantamento").hide();
            }
        },
        error: function(error, data) {
            console.log(error)
        }
    });
});

$(document).on('click', '.selecionar-saldoavulso', function(event) {
    var url = $(this).attr('data-url')
    var datainicial = $(this).attr('datainicial')
    var datafinal = $(this).attr('datafinal')
    var idpessoal = $(this).attr('idpessoal')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            DataInicial: datainicial,
            DataFinal: datafinal,
            idPessoal: idpessoal,
        },
        success: function(data){
            $(".pa-minutas").html(data.html_minutas);
            $(".pa-vales").html(data.html_valesavulso);
            valeselect('#vale_' + idpessoal);
            somavales();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(".div-fade-folha").click(function(){  
    if ($("#fp-main").is(':hidden')) {
        $("#fp-main").slideDown("fast");
        $(".up-folha").show()
        $(".down-folha").hide()
    } else {
        $(".up-folha").hide()
        $(".down-folha").show()
        $("#fp-main").slideUp("fast");
    }
});

$(".div-fade-avulso").click(function(){  
    if ($("#pa-main").is(':hidden')) {
        $("#pa-main").slideDown("fast");
        $(".up-avulso").show()
        $(".down-avulso").hide()
    } else {
        $(".up-avulso").hide()
        $(".down-avulso").show()
        $("#pa-main").slideUp("fast");
    }
});

function openMyModal(event) {
    var modal = initModalDialog(event, '#MyModal');
    var url = $(event.target).data('action');
    var idcartaoponto = $(event.target).data('idcartaoponto');
    var mesreferencia = $(event.target).data('mesreferencia');
    var anoreferencia = $(event.target).data('anoreferencia');
    var idpessoal = $(event.target).data('idpessoal');
    $.ajax({
        type: "GET",
        url: url,
        data : {
            idCartaoPonto: idcartaoponto,
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        }
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
                    $(".fp-folha-contracheque").html("");
                    $(".fp-folha-contracheque").html(xhr.html_folha)
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

function valeselect(idpessoal) {
    var total = 0.00
    $('.switchmini').each(function() {
        if ($(this).is(":checked") && $(this).attr('idPessoal') == idpessoal.substring(6)) {
            total += parseFloat($(this).attr('valorvale').replace(',', '.'))
        }
        $(idpessoal).text('R$ ' + total.toFixed(2).replace('.', ','));
    });
}

function somavales() {
    var total = 0.00
    $('.saldovale').each(function() {
        total += parseFloat($(this).text().replace('R$ ', '').replace(',', '.'))
    });
    $('#totalvales').text('R$ ' + total.toFixed(2).replace('.', ','))    
}