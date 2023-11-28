$(".div-sucesso").hide()
$(".div-erro").hide()
$(".box-loader").hide()

function openMyModal(event) {
    var modal = initModalDialog(event, '#MyModal');
    var url = $(event.target).data('action');
    var idpessoal = localStorage.getItem("idpessoal");
    var confirma = $(event.target).data("confirma")
    var idconfirma = $(event.target).data("idconfirma")
    $.ajax({
        type: "GET",
        url: url,
        data : {
            idpessoal: idpessoal,
            confirma: confirma,
            idconfirma: idconfirma,
        }
    }).done(function(data, textStatus, jqXHR) {
        modal.find('.modal-body').html(data.html_modal);
        $('.box-loader').hide()
        modal.modal('show');
        formAjaxSubmit(modal, url, null, null);
    }).fail(function(jqXHR, textStatus, errorThrown) {

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
                    if (xhr["html_vales_colaborador"]) {
                        $(".card-vales-colaborador").html(xhr["html_vales_colaborador"])
                    }
                    $(".box-loader").hide()
                    if (cbAfterSuccess) { 
                        cbAfterSuccess(modal);
                    }
                }
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
