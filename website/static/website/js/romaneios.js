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
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
                //CarregaMask()
            $(".box-loader").hide();
        },
    });
});

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
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
                //CarregaMask()
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
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
                // CarregaMask()
            $(".box-loader").hide();
        },
    });
});