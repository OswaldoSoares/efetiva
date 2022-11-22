$(document).on('click', ".js-seleciona-colaborador", function() {
    var id_pessoal = $(this).data("idpessoal");
    $.ajax({
        type: "GET",
        url: "/pessoas/consulta_pessoa",
        data: {
            id_pessoal: id_pessoal,
        },
        beforeSend: function() {
            $(".card-dados-colaborador").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('click', ".js-salva-foto", function(event) {
    event.preventDefault();
    var _formData = new FormData();
    var _arquivo = $("#file_foto").get(0).files[0]
    var _csrf_token = $('input[name="csrfmiddlewaretoken"]').val()
    var _idpessoal = $("#idpessoal").val()
    _formData.append("arquivo", _arquivo);
    _formData.append("csrfmiddlewaretoken", _csrf_token);
    _formData.append("idpessoal", _idpessoal);
    $.ajax({
        type: 'POST',
        url: '/pessoas/salva_foto',
        data: _formData,
        cache: false,
        processData: false,
        contentType: false,
        enctype: 'multipart/form-data',
        beforeSend: function() {
            $(".card-dados-colaborador").hide()
            $('.box-loader').show()
        },
        success: function(data) {
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            $('.box-loader').hide()
        },
    });
});

$(document).on('change', '.js-carrega-foto', function() {
    $(".js-salva-foto").click()
});