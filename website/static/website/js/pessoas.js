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
            $(".card-decimo-terceiro").hide()
            $(".card-form-colaborador").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            $(".card-decimo-terceiro").html(data.html_decimo_terceiro)
            $(".card-decimo-terceiro").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('submit', ".js-salva-foto", function(event) {
    event.preventDefault();
    var _formData = new FormData();
    var _arquivo = $("#file_foto").get(0).files[0]
    var _csrf_token = $('input[name="csrfmiddlewaretoken"]').val()
    var _idpessoal = $("#idpessoal").val()
    _formData.append("arquivo", _arquivo);
    _formData.append("csrfmiddlewaretoken", _csrf_token);
    _formData.append("idpessoal", _idpessoal);
    console.log(_arquivo, _idpessoal, _csrf_token)
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
                // $('.box-loader').show()
        },
        success: function(data) {
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            $('.box-loader').hide()
            console.log("oi")
            console.log(data)
        },
        errorThrown: function(data) {
            console.log(data)
        },
    });
});

// $(document).on('change', '.js-carrega-foto', function() {
//     $(".js-salva-foto").click()
// });

$(document).on('click', '.js-atualiza-decimo-terceiro', function() {
    $.ajax({
        type: "GET",
        url: "/pessoas/atualiza_decimo_terceiro",
        data: {},
        beforeSend: function() {
            $(".card-lista-colaboradores").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-lista-colaboradores").html(data.html_lista_colaboradores_ativo)
            $(".card-lista-colaboradores").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('click', '.js-adiciona-documento-colaborador', function() {
    var idpessoal = $(this).data('idobj')
    $.ajax({
        type: "GET",
        url: "/pessoas/adiciona_documento_colaborador",
        data: {
            idpessoal: idpessoal,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_documento_colaborador)
            $(".card-form-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('submit', '.js-gera-documento', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: "/pessoas/salva_documento_colaborador",
        data: $(this).serialize(),
        beforeSend: function() {
            $('.card-dados-colaborador').hide()
            $('.card-form-colaborador').hide()
            $('.box-loader').show()
        },
        success: function(data) {
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            if (data.html_form_documento_colaborador) {
                $('.card-form-colaborador').html(data.html_form_documento_colaborador)
                $('.card-form-colaborador').show()
            }
            console.log(data)
            $('.box-loader').hide()
        },
    });
});

$(document).on('click', '.js-fecha-formulario', function() {
    $('.card-form-colaborador').hide();
});

$(document).on('click', '.js-adiciona-telefone-colaborador', function() {
    var idpessoal = $(this).data('idobj')
    $.ajax({
        type: "GET",
        url: "/pessoas/atualiza_decimo_terceiro",
        data: {
            idpessoal: idpessoal,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-lista-colaboradores").html(data.html_lista_colaboradores_ativo)
            $(".card-lista-colaboradores").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('click', '.js-adiciona-conta-colaborador', function() {
    var idpessoal = $(this).data('idobj')
    $.ajax({
        type: "GET",
        url: "/pessoas/atualiza_decimo_terceiro",
        data: {
            idpessoal: idpessoal,
        },
        beforeSend: function() {
            $(".card-lista-colaboradores").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-lista-colaboradores").html(data.html_lista_colaboradores_ativo)
            $(".card-lista-colaboradores").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});