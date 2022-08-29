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
            $(".card-lista-romaneios").html(data.html_lista_romaneios)
            $(".card-lista-romaneios").show()
            $(".mostra-body-nota").show()
            $(".body-nota").hide()
            $(".js-oculta-body-nota").hide()
            $(".file-body").hide()
            $(".mostra-body-romaneio").show()
            $(".body-romaneio").hide()
            $(".js-oculta-body-romaneio").hide()
            $(".js-adiciona-nota-romaneio").hide()
                //CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-mostra-body-nota', function() {
    $(".body-nota").show()
    $(".js-mostra-body-nota").hide()
    $(".js-oculta-body-nota").show()
    $(".file-body").show()
})

$(document).on('click', '.js-oculta-body-nota', function() {
    $(".body-nota").hide()
    $(".js-mostra-body-nota").show()
    $(".js-oculta-body-nota").hide()
    $(".file-body").hide()
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

$(document).on('click', '.js-edita-romaneio', function() {
    var _id_romaneio = $(this).data("idromaneio")
    $.ajax({
        type: 'GET',
        url: '/romaneios/edita_romaneio',
        data: {
            idRomaneio: _id_romaneio,
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

$(document).on('click', '.js-seleciona-romaneio', function() {
    var _id_romaneio = $(this).data("idromaneio")
    $.ajax({
        type: 'GET',
        url: '/romaneios/seleciona_romaneio',
        data: {
            idRomaneio: _id_romaneio,
        },
        beforeSend: function() {
            $(".card-lista-romaneios").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-notas-romaneio").html(data.html_lista_notas_romaneio)
            $(".card-lista-notas-romaneio").show()
            $(".js-adiciona-nota-romaneio").show()
                // CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-adiciona-nota-romaneio', function() {
    var _id_nota = $(this).data("idnota")
    var _id_romaneio = $('#id_romaneio').val()
    $.ajax({
        type: 'GET',
        url: '/romaneios/adiciona_nota_romaneio',
        data: {
            idNota: _id_nota,
            idRomaneio: _id_romaneio
        },
        beforeSend: function() {

        },
        success: function(data) {

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
            $(".js-adiciona-nota-romaneio").hide()
                //CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('change', $('.js-file-xml'), function() {
    if ($('.js-file-xml').val()) {
        $('.js-xmlTxt').text($('.js-file-xml').val().match(/[\/\\]([\w\d\s\.\-\(\)]+)$/)[1]);
        $('.js-xmlTxt').text($('.js-xmlTxt').text().substring(0, 23) + '...');
    } else {
        $('.js-xmlTxt').text('Selecionar XML.');
    }
});

$(document).on('submit', '.js-carrega-xml', function(event) {
    event.preventDefault();
    var formData = new FormData($(this)[0])
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    formData.append('csrfmiddlewaretoken', csrftoken);
    $.ajax({
        type: $(this).attr('method'),
        url: '/romaneios/carrega_xml',
        processData: false,
        contentType: false,
        data: formData,
        beforeSend: function() {
            //$(".card-lista-ocorrencia").hide()
            //$(".box-loader").show();
        },
        success: function(data) {
            $("#numeronota").val(data["numero_nf"])
            $("#destinatario").val(data["destinatario"])
            $("#endereco").val(data["endereco"])
            $("#bairro").val(data["bairro"])
            $("#cep").val(data["cep"])
            $("#cidade").val(data["cidade"])
            $("#estado").val(data["estado"])
            $("#telefone").val(data["telefone"])
            $("#informa").val(data["informa"])
            $("#volume").val(data["volume"])
            $("#peso").val(data["peso"])
            $("#valor").val(data["valor"])
        },
    });
});