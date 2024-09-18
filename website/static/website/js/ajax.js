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
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log(error);
            $(".box-loader").hide();
        }
    });
}
