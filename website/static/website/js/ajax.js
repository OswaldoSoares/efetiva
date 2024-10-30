function executarAjax(url, type, data, sucessoCallback) {
    $.ajax({
        type: type,
        url: url,
        data: data,
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(response) {
            sucessoCallback(response);
            $("html, body").scrollTop(0);
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log("ERROR: ", error);
            $(".box-loader").hide();
        }
    });
}

function enviarRequisicaoAjax(url, form, sucessoCallback) {
    $.ajax({
        type: form.attr("method"),
        url: url,
        idobj: form.attr("idobj"),
        data: form.serialize(),
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(response) {
            sucessoCallback(response);
            $(".box-loader").hide();
        },
        error: function(errorThrown) {
            $(".box-loader").hide();
            console.log(errorThrown)
            $(".thrown-error").text(errorThrown.responseJSON["error"])
            $(".thrown-error").removeClass("invisivel")
        },
    });
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

function exibirMensagem(mensagem) {
    $('.mensagem p').text(mensagem);
    $('.mensagem p').animate({bottom: '0'}, 1000);
    setTimeout(function() {
        $('.mensagem p').animate({bottom: '60px'}, 1000); 
        $('.mensagem p').animate({bottom: '-30px'}, 0);
    }, 5000);
}
