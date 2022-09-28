$(document).on('submit', '.js-seleciona-cliente', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: '/romaneios/seleciona_cliente',
        data: $(this).serialize(),
        beforeSend: function() {
            $(".card-romaneios-cliente").hide()
            $(".card-lista-notas-cliente").hide()
            $(".card-lista-notas-romaneio").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            if (data.html_form_seleciona_cliente) {
                $(".card-romaneios-cliente").html(data.html_form_seleciona_cliente)
                $(".card-romaneios-cliente").show()
            } else {
                $(".card-form-notas-cliente").html(data.html_form_notas_cliente)
                $(".card-form-notas-cliente").show()
                $(".card-form-romaneios").html(data.html_form_romaneios)
                $(".card-form-romaneios").show()
                $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
                $(".card-lista-notas-cliente").show()
                $(".card-lista-romaneios").html(data.html_lista_romaneios)
                $(".card-lista-romaneios").show()
                $(".card-quantidade-notas").html(data.html_quantidade_notas)
                $(".card-quantidade-notas").show()
                $(".card-filtro-notas-romaneios").html(data.html_filtro_notas_romaneios)
                $(".card-filtro-notas-romaneios").show()
                $(".mostra-body-nota").show()
                $(".body-nota").hide()
                $(".js-oculta-body-nota").hide()
                $(".file-body").hide()
                $(".mostra-body-romaneio").show()
                $(".body-romaneio").hide()
                $(".js-oculta-body-romaneio").hide()
                $(".js-adiciona-nota-romaneio").hide()
                $(".js-envia-telegram-relatorio").hide()
            }
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-seleciona-romaneio', function() {
    var _id_romaneio = $(this).data("idromaneio")
    var _id_cliente = $(this).data("idcliente")
    $.ajax({
        type: 'GET',
        url: '/romaneios/seleciona_romaneio',
        data: {
            idRomaneio: _id_romaneio,
            idCliente: _id_cliente,
        },
        beforeSend: function() {
            $(".card-lista-romaneios").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-notas-romaneio").html(data.html_lista_notas_romaneio)
            $(".card-lista-notas-romaneio").show()
            $(".js-adiciona-nota-romaneio").show()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-nota-pendente', function() {
    var _id_nota_clientes = $(this).data("idnotaclientes")
    var _status = $("#select-status").val()
    var id_cliente = $("#id_cliente").val()
    $.ajax({
        type: 'GET',
        url: '/romaneios/nota_deposito',
        data: {
            idNotaClientes: _id_nota_clientes,
            status: _status,
            cliente: id_cliente,
        },
        beforeSend: function() {
            $(".card-lista-notas-cliente").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente_reduzida)
            $(".card-lista-notas-cliente").show()
            $(".card-lista-romaneios").show()
            $(".js-adiciona-nota-romaneio").hide()
            $(".box-loader").hide()
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
    LimpaFormNota()
})

$(document).on('click', '.js-mostra-body-romaneio', function() {
    $(".body-romaneio").show()
    $(".js-mostra-body-romaneio").hide()
    $(".js-oculta-body-romaneio").show()
});

$(document).on('click', '.js-oculta-body-romaneio', function() {
    $(".body-romaneio").hide()
    $(".js-mostra-body-romaneio").show()
    $(".js-oculta-body-romaneio").hide()
    LimpaFormRomaneio()
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
            $(".card-form-romaneios").html(data.html_form_romaneios)
            $(".card-form-romaneios").show()
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
                //CarregaMask()
            $(".box-loader").hide();
        },
    });
});


$(document).on('click', '.js-print-relatorio', function() {
    $('.js-envia-telegram-relatorio').show()
});

$(document).on('click', '.js-filtro-status', function() {
    var _status = $("#select-status").val()
    var id_cliente = $(this).data("idcliente")
    $.ajax({
        type: 'GET',
        url: '/romaneios/filtra_status',
        data: {
            status: _status,
            cliente: id_cliente,
        },
        beforeSend: function() {
            $(".card-lista-notas-cliente").hide()
            $(".card-lista-ocorrencia").hide()
            $(".card-lista-romaneios").hide()
            $(".card-lista-notas-romaneio").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente_reduzida)
            $(".card-lista-notas-cliente").show()
            $(".card-lista-romaneios").show()
            $(".js-adiciona-nota-romaneio").hide()
            $(".js-envia-telegram-relatorio").hide()
            $(".box-loader").hide()
        },
    });
});

$(document).on('click', '.js-imprime-notas-status', function() {
    var _status = $("#select-status").val()
    var id_cliente = $("#id_cliente").val()
    $.ajax({
        type: 'GET',
        url: '/romaneios/filtra_status',
        data: {
            status: _status,
            cliente: id_cliente,
        },
        beforeSend: function() {
            $(".card-lista-notas-cliente").hide()
            $(".card-lista-romaneios").hide()
            $(".card-lista-notas-romaneio").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente_reduzida)
            $(".card-lista-notas-cliente").show()
            $(".card-lista-romaneios").show()
            $(".js-adiciona-nota-romaneio").hide()
            $(".box-loader").hide()
        },
    });
});

$(document).on('click', '.js-filtra-nota', function() {
    var anr_visible = $(".card-lista-notas-romaneio").is(":visible")
    var nota = $(".filtra-nota").val()
    var id_cliente = $("#id_cliente").val()
    $.ajax({
        type: 'GET',
        url: '/romaneios/filtra_nota_cliente',
        data: {
            nota: nota,
            cliente: id_cliente,
        },
        beforeSend: function() {
            $(".card-lista-notas-cliente").hide()
            $(".card-lista-romaneios").hide()
            $(".card-lista-notas-romaneio").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
            if (data.id_rom) {
                $(".card-lista-notas-romaneio").html(data.html_lista_notas_romaneio)
                $(".card-lista-notas-romaneio").show()
                $(".js-adiciona-nota-romaneio").hide()
            } else {
                if (anr_visible) {
                    $(".js-adiciona-nota-romaneio").show()
                    $(".card-lista-notas-romaneio").show()
                } else {
                    $(".js-adiciona-nota-romaneio").hide()
                    $(".card-lista-romaneios").show()
                }
            }
            $(".box-loader").hide()
        },
    });
});

$(document).on('submit', '.js-gera-ocorrencia', function(event) {
    event.preventDefault();
    var lnr_visible = $(".card-lista-notas-romaneio").is(":visible")
    $.ajax({
        type: $(this).attr('method'),
        url: '/romaneios/adiciona_ocorrencia',
        data: $(this).serialize(),
        beforeSend: function() {
            if (lnr_visible) {
                $(".card-lista-notas-romaneio").hide()
            }
            $(".card-lista-ocorrencia").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-ocorrencia").html(data.html_lista_ocorrencia)
            $(".card-lista-ocorrencia").show()
            if (lnr_visible) {
                $(".card-lista-notas-romaneio").html(data.html_lista_notas_romaneio)
                $(".card-lista-notas-romaneio").show()
            }
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
            $(".card-lista-romaneios").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-romaneios").html(data.html_lista_romaneios)
            $(".card-lista-romaneios").show()
                //CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-ocorrencia-notas-cliente', function() {
    var _id_nota = $(this).data("idnota")
    var _id_cliente = $(this).data("idcliente")
    var _id_romaneio = ""
    $.ajax({
        type: 'GET',
        url: '/romaneios/ocorrencia_nota_cliente',
        data: {
            idNota: _id_nota,
            idCliente: _id_cliente,
            idRomaneio: _id_romaneio,
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

$(document).on('click', '.js-envia-telegram-romaneio', function() {
    var _romaneio = $(this).data("romaneio")
    $.ajax({
        type: 'GET',
        url: '/romaneios/envia_telegram_romaneio',
        data: {
            Romaneio: _romaneio,
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

$(document).on('click', '.js-envia-telegram-relatorio', function() {
    var _status = $("#select-status").val()
    $(this).hide()
    $.ajax({
        type: 'GET',
        url: '/romaneios/envia_telegram_relatorio',
        data: {
            status: _status,
        },
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(data) {
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

$(document).on('click', '.js-filtra-romaneio', function() {
    var id_romaneio = $(".filtra-romaneio").val()
    var id_cliente = $("#id_cliente").val()
    $.ajax({
        type: 'GET',
        url: '/romaneios/seleciona_romaneio',
        data: {
            idRomaneio: id_romaneio,
            idCliente: id_cliente,
        },
        beforeSend: function() {
            $(".card-lista-romaneios").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-notas-romaneio").html(data.html_lista_notas_romaneio)
            $(".card-lista-notas-romaneio").show()
            $(".js-adiciona-nota-romaneio").show()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-adiciona-nota-romaneio', function() {
    var _id_nota = $(this).data("idnota")
    var _id_romaneio = $('#id_romaneio').val()
    var _id_cliente = $(this).data("idcliente")
    $(this).hide()
    $.ajax({
        type: 'GET',
        url: '/romaneios/adiciona_nota_romaneio',
        data: {
            idNota: _id_nota,
            idRomaneio: _id_romaneio,
            idCliente: _id_cliente,
        },
        beforeSend: function() {
            $(".card-lista-notas-romaneio").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-lista-notas-romaneio").html(data.html_lista_notas_romaneio)
            $(".card-lista-notas-romaneio").show()
            $(".box-loader").hide()
        },
    });
});

$(document).on('click', '.js-exclui-nota-romaneio', function() {
    var _id_romaneio_nota = $(this).data("idromaneionotas")
    var _id_romaneio = $('#id_romaneio').val()
    var _id_nota = $(this).data("idnota")
    $.ajax({
        type: 'GET',
        url: '/romaneios/exclui_nota_romaneio',
        data: {
            idRomaneioNota: _id_romaneio_nota,
            idRomaneio: _id_romaneio,
            idNota: _id_nota,
        },
        beforeSend: function() {
            $(".card-lista-notas-romaneio").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-lista-notas-romaneio").html(data.html_lista_notas_romaneio)
            $(".card-lista-notas-romaneio").show()
            $(".box-loader").hide()
        },
    });
});

$(document).on('click', '.js-retorna-lista-romaneio', function() {
    $(".box-loader").show();
    $(".js-adiciona-nota-romaneio").hide()
    $(".card-lista-notas-romaneio").hide()
    $(".card-lista-romaneios").show()
    window.setTimeout(function() {
        $(".box-loader").hide();
    }, 500);
});

$(document).on('click', '.js-exclui-notas-cliente', function() {
    var _id_nota = $(this).data("idnota")
    var _id_cliente = $(this).data("idcliente")
    if ($("#reduzida-exist").length) {
        var _card_reduzida = true
        var _div_nota = "#nota-" + _id_nota
        $(_div_nota).hide()
    } else {
        var _card_reduzida = false
    }
    $.ajax({
        type: 'GET',
        url: '/romaneios/exclui_nota_cliente',
        data: {
            idNota: _id_nota,
            idCliente: _id_cliente,
        },
        beforeSend: function() {
            if (_card_reduzida == false) {
                $(".card-lista-notas-cliente").hide()
            }
            $(".box-loader").show();
        },
        success: function(data) {
            if (_card_reduzida == false) {
                $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
                $(".card-lista-notas-cliente").show()
            }
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

$(document).on('click', '.js-fecha-romaneio', function() {
    var _id_romaneio = $(this).data("idromaneio")
    $.ajax({
        type: 'GET',
        url: '/romaneios/fecha_romaneio',
        data: {
            idRomaneio: _id_romaneio,
        },
        beforeSend: function() {
            $(".card-lista-romaneios").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-romaneios").html(data.html_lista_romaneios)
            $(".card-lista-romaneios").show()
                //CarregaMask()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-sort-notas', function() {
    var anr_hidden = $(".js-adiciona-nota-romaneio").is(":hidden")
    var _status = $("#select-status").val()
    var _tipo_sort = $(".js-tipo-sort").val()
    var _id_cliente = $(this).data("idcliente")
    var _sort = $(this).data("sort")
    $.ajax({
        type: 'GET',
        url: '/romaneios/orderna_notas',
        data: {
            cliente: _id_cliente,
            sort: _sort,
            tipo_sort: _tipo_sort,
            status: _status,
        },
        beforeSend: function() {
            $(".card-lista-notas-cliente").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente_reduzida)
            $(".card-lista-notas-cliente").show()
            $(".js-envia-telegram-relatorio").hide()
            if (anr_hidden) {
                $(".js-adiciona-nota-romaneio").hide()
            }
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
            $("#contato").val(data["telefone"])
            $("#informa").val(data["informa"])
            $("#volume").val(data["volume"])
            $("#peso").val(data["peso"])
            $("#valor").val(data["valor"])
        },
    });
});

var LimpaFormNota = function() {
    hoje = Hoje()
    $("#localcoleta").val("")
    $("#datacoleta").val(hoje)
    $("#numeronota").val("")
    $("#destinatario").val("")
    $("#endereco").val("")
    $("#bairro").val("")
    $("#cep").val("")
    $("#cidade").val("SÃO PAULO")
    $("#estado").val("SP")
    $("#contato").val("")
    $("#informa").val("")
    $("#volume").val("0")
    $("#peso").val("0.00")
    $("#valor").val("0.00")
}

var LimpaFormRomaneio = function() {
    hoje = Hoje()
    $("#data_romaneio").val(hoje)
    $("#motorista").val("")
    $("#veiculo").val("")
}

var Hoje = function() {
    var hoje = new Date();
    var dd = String(hoje.getDate()).padStart(2, '0');
    var mm = String(hoje.getMonth() + 1).padStart(2, '0'); //January is 0!
    var yyyy = hoje.getFullYear();
    hoje = yyyy + '-' + mm + '-' + dd;
    return hoje
}