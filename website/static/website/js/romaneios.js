$(document).on('submit', '.js-seleciona-cliente', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: '/romaneios/seleciona_cliente',
        data: $(this).serialize(),
        beforeSend: function() {
            $(".card-romaneios-cliente").hide()
            $(".card-lista-notas-cliente").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-form-notas-cliente").html(data.html_form_notas_cliente)
            $(".card-form-notas-cliente").show()
            $(".card-form-romaneios").html(data.html_form_romaneios)
            $(".card-form-romaneios").show()
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
            $(".mostra-body-nota").show()
            $(".body-nota").hide()
            $(".js-oculta-body-nota").hide()
            $(".mostra-body-romaneio").show()
            $(".body-romaneio").hide()
            $(".js-oculta-body-romaneio").hide()
                //CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-mostra-body-nota', function() {
    $(".body-nota").show()
    $(".js-mostra-body-nota").hide()
    $(".js-oculta-body-nota").show()
})

$(document).on('click', '.js-oculta-body-nota', function() {
    $(".body-nota").hide()
    $(".js-mostra-body-nota").show()
    $(".js-oculta-body-nota").hide()
})

$(document).on('click', '.js-mostra-body-romaneio', function() {
    $(".body-romaneio").show()
    $(".js-mostra-body-romaneio").hide()
    $(".js-oculta-body-romaneio").show()
})

$(document).on('click', '.js-oculta-body-romaneio', function() {
    $(".body-romaneio").hide()
    $(".js-mostra-body-romaneio").show()
    $(".js-oculta-body-romaneio").hide()
})

$(document).on('submit', '.js-gera-notas-cliente', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: '/romaneios/adiciona_nota_cliente',
        data: $(this).serialize(),
        beforeSend: function() {
            $(".card-romaneios-cliente").hide()
            $(".card-lista-notas-cliente").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-form-notas-cliente").html(data.html_form_notas_cliente)
            $(".card-form-notas-cliente").show()
            $(".card-form-romaneios").html(data.html_form_romaneios)
            $(".card-form-romaneios").show()
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
                //CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('submit', '.js-gera-ocorrencia', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: '/romaneios/adiciona_ocorrencia',
        data: $(this).serialize(),
        beforeSend: function() {
            $(".card-lista-ocorrencia").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-ocorrencia").html(data.html_lista_ocorrencia)
            $(".card-lista-ocorrencia").show()
                //CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('submit', '.js-gera-romaneios', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: '/romaneios/adiciona_romaneio',
        data: $(this).serialize(),
        beforeSend: function() {
            $(".card-lista-ocorrencia").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-ocorrencia").html(data.html_lista_ocorrencia)
            $(".card-lista-ocorrencia").show()
                //CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-ocorrencia-notas-cliente', function() {
    var _id_nota = $(this).data("idnota")
    var _id_cliente = $(this).data("idcliente")
    $.ajax({
        type: 'GET',
        url: '/romaneios/ocorrencia_nota_cliente',
        data: {
            idNota: _id_nota,
            idCliente: _id_cliente,
        },
        beforeSend: function() {
            $(".card-lista-notas-cliente").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-ocorrencia").html(data.html_lista_ocorrencia)
            $(".card-lista-ocorrencia").show()
                // CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-edita-notas-cliente', function() {
    var _id_nota = $(this).data("idnota")
    var _id_cliente = $(this).data("idcliente")
    $.ajax({
        type: 'GET',
        url: '/romaneios/edita_nota_cliente',
        data: {
            idNota: _id_nota,
            idCliente: _id_cliente,
        },
        beforeSend: function() {
            $(".card-form-notas-cliente").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-form-notas-cliente").html(data.html_form_notas_cliente)
            $(".card-form-notas-cliente").show()
            $(".card-form-romaneios").html(data.html_form_romaneios)
            $(".card-form-romaneios").show()
                // CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-exclui-notas-cliente', function() {
    var _id_nota = $(this).data("idnota")
    var _id_cliente = $(this).data("idcliente")
    $.ajax({
        type: 'GET',
        url: '/romaneios/exclui_nota_cliente',
        data: {
            idNota: _id_nota,
            idCliente: _id_cliente,
        },
        beforeSend: function() {
            $(".card-form-notas-cliente").hide()
            $(".card-lista-notas-cliente").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-form-notas-cliente").html(data.html_form_notas_cliente)
            $(".card-form-notas-cliente").show()
            $(".card-form-romaneios").html(data.html_form_romaneios)
            $(".card-form-romaneios").show()
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
                // CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-retorna-lista-notas', function() {
    var _id_cliente = $(this).data("idcliente")
    $.ajax({
        type: 'GET',
        url: '/romaneios/seleciona_cliente',
        data: {
            cliente: _id_cliente,
        },
        beforeSend: function() {
            $(".card-lista-ocorrencia").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
                //CarregaMask()
            $(".box-loader").hide();
        },
    });
});