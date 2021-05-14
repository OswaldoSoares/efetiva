$(document).ready(function(){

});

$('.switch').change(function() {
    $('.pagamento-base-itens').html("");
    nome = $(this).attr('id');

    $.ajax({
        type: 'GET',
        url: 'teste',
        data: {
            nome: nome,
        },
        success: function(data) {
            $('.pagamento-base-itens').html(data.html_form);
        },
    });

   
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
            console.log('OK Também')
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
            if (data.html_adiantamento == true) {
                $(".fp-adiantamento").hide();
            }
        },
        error: function(error, data) {
            console.log(data.html_cartaoponto)
            console.log(error)
        }
    });
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