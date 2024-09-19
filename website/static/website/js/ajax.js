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
            console.log("Thrwon", errorThrown)
        },
    });
}
