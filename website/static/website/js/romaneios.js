$(document).on('submit', '.js-seleciona-cliente', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: '/romaneios/seleciona_cliente',
        data: $(this).serialize(),
        beforeSend: function() {
            $(".card-romaneios-cliente").hide()
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
                $("#select-status").val("PENDENTE")
                $(".card-filtro-notas-romaneios").show()
                $(".js-mostra-form-nota").slideToggle(500)
                $(".js-mostra-form-romaneio").slideToggle(500)
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
            $(".box-loader").show();
            $(".card-lista-notas-cliente").hide()
            $(".card-quantidade-notas").hide()
        },
        success: function(data) {
            $(".card-lista-notas-cliente").html(data.html_card_lista_notas_cliente)
            $(".js-notas-filtro").html("NOTAS CADASTRADAS")
            $(".card-lista-notas-cliente").show()
            $(".card-lista-romaneios").show()
            $(".js-adiciona-nota-romaneio").hide()
            $(".card-quantidade-notas").html(data.html_quantidade_notas)
            $(".card-quantidade-notas").show()
            $(".box-loader").hide()
        },
    });
});

$(document).on('click', '.js-mostra-oculta-form-nota', function() {
    mostraBodyFormNota();
    $(".btn-pasta-arquivos-xml").hide()
})

var mostraBodyFormNota = function() {
    $(".js-mostra-form-nota").slideToggle(500)
    $(".js-mostra-oculta-form-nota").toggleClass("bi-chevron-up");
}

$(document).on('click', '.js-mostra-oculta-form-romaneio', function() {
    mostraBodyFormRomaneio();
})

var mostraBodyFormRomaneio = function() {
    $(".js-mostra-form-romaneio").slideToggle(500)
    $(".js-mostra-oculta-form-romaneio").toggleClass("bi-chevron-up");
}

$(document).on('submit', '.js-gera-notas-cliente', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: '/romaneios/adiciona_nota_cliente',
        data: $(this).serialize(),
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-form-notas-cliente").html(data.html_form_notas_cliente)
            $(".js-mostra-oculta-form-nota").toggleClass("bi-chevron-up")
            $(".card-form-notas-cliente").show()
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".js-notas-filtro").html("NOTAS CADASTRADAS")
            $(".card-lista-notas-cliente").show()
            $(".card-quantidade-notas").html(data.html_quantidade_notas)
            $(".card-quantidade-notas").show()
            $(".box-loader").hide();
            $(window).scrollTop(0)
        },
    });
});


$(document).on('click', '.js-print-relatorio', function() {
    $('.js-envia-telegram-relatorio').show()
});

$(document).on('click', '.js-filtro-status', function() {
    $('#filtro').val($("#select-status").val())
    var status = $("#select-status").val()
    var id_cliente = $(this).data("idcliente")
    if (status != "") {
        $.ajax({
            type: 'GET',
            url: '/romaneios/filtra_status',
            data: {
                status: status,
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
                $(".card-lista-notas-cliente").html(data.html_card_lista_notas_cliente)
                $(".js-notas-filtro").html("NOTAS " + status)
                $(".card-lista-notas-cliente").show()
                $(".card-lista-romaneios").show()
                $(".js-adiciona-nota-romaneio").hide()
                $(".js-envia-telegram-relatorio").hide()
                $(".box-loader").hide()
            },
        });
    }
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
            $(".card-lista-notas-cliente").html(data.html_card_lista_notas_cliente)
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
            $(".box-loader").show()
            $(".card-lista-notas-cliente").hide()
            $(".card-lista-romaneios").hide()
            $(".card-lista-notas-romaneio").hide()
            $(".filtra-nota").val("")
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
            $(".box-loader").show();
            if (lnr_visible) {
                $(".card-lista-notas-romaneio").hide()
            }
            $(".card-lista-ocorrencia").hide()
            $(".card-quantidade-notas").hide()
        },
        success: function(data) {
            $(".card-lista-ocorrencia").html(data.html_lista_ocorrencia)
            $(".card-lista-ocorrencia").show()
            if (lnr_visible) {
                $(".card-lista-notas-romaneio").html(data.html_lista_notas_romaneio)
                $(".card-lista-notas-romaneio").show()
            }
            $(".card-quantidade-notas").html(data.html_quantidade_notas)
            $(".card-quantidade-notas").show()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-exclui-ocorrencia', function() {
    var idnotasocorrencia = $(this).data('idnotasocorrencia');
    var idnota = $(this).data('idnota');
    var idcliente = $('#idcliente').val();
    var lnr_visible = $(".card-lista-notas-romaneio").is(":visible")
    $.ajax({
        type: 'GET',
        url: '/romaneios/exclui_ocorrencia',
        data: {
            idnotasocorrencia: idnotasocorrencia,
            idnota: idnota,
            idcliente: idcliente,
        },
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-ocorrencia").html(data.html_lista_ocorrencia)
            $(".card-lista-ocorrencia").show()
            if (lnr_visible) {
                $(".card-lista-notas-romaneio").html(data.html_lista_notas_romaneio)
                $(".card-lista-notas-romaneio").show()
            }
            $(".card-quantidade-notas").html(data.html_quantidade_notas)
            $(".card-quantidade-notas").show()
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
            mostraBodyFormRomaneio();
            LimpaFormRomaneio();
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
            $(window).scrollTop(0)
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
            $(".js-mostra-oculta-form-nota").toggleClass("bi-chevron-up");
            $(".card-form-notas-cliente").show()
            $(".box-loader").hide();
            $('#filtro').val($("#select-status").val())
            $(window).scrollTop(0)
        },
    });
});

$(document).on('blur', '#emitente', function() {
    if ($("#emitente").val() != "") {
        local = $("#emitente").val()
        $.ajax({
            type: "GET",
            url: "/romaneios/busca_local_nota",
            data: {
                local: local,
            },
            beforeSend: function() {},
            success: function(data) {
                $("#endereco_emi").val(data.endereco.endereco)
                $("#bairro_emi").val(data.endereco.bairro)
                $("#cep_emi").val(data.endereco.cep)
                $("#cidade_emi").val(data.endereco.cidade)
                $("#estado_emi").val(data.endereco.estado)
                if (data.mensagem) {
                    console.log(data.mensagem)
                    $(".mensagem p").removeClass("mensagem-color")
                    $(".mensagem p").removeClass("mensagem-success-color")
                    $(".mensagem p").addClass("mensagem-error-color")
                    exibirMensagem(data.mensagem);
                }
            },
        });
    }
});

// Mostra a div de mensagem com a mensagem de erro
function exibirMensagem(mensagem) {
    $('.mensagem p').text(mensagem);
    $('.mensagem p').animate({bottom: '0'}, 1000);
    setTimeout(function() {
        $('.mensagem p').animate({bottom: '60px'}, 1000); 
        $('.mensagem p').animate({bottom: '-30px'}, 0);
    }, 3000);
}

$(document).on('blur', '#destinatario', function() {
    if ($("#destimatario").val() != "") {
        local = $("#destinatario").val()
        $.ajax({
            type: "GET",
            url: "/romaneios/busca_local_nota",
            data: {
                local: local,
            },
            beforeSend: function() {},
            success: function(data) {
                $("#endereco").val(data.endereco.endereco)
                $("#bairro").val(data.endereco.bairro)
                $("#cep").val(data.endereco.cep)
                $("#cidade").val(data.endereco.cidade)
                $("#estado").val(data.endereco.estado)
                if (data.mensagem) {
                    console.log(data.mensagem)
                    $(".mensagem p").removeClass("mensagem-color")
                    $(".mensagem p").removeClass("mensagem-success-color")
                    $(".mensagem p").addClass("mensagem-error-color")
                    exibirMensagem(data.mensagem);
                }
            },
        });
    }
});

$(document).on('click', '.js-envia-telegram-romaneio', function() {
    var romaneio = $(this).data("romaneio")
    var idcliente = $(this).data("idcliente")
    $.ajax({
        type: 'GET',
        url: '/romaneios/envia_telegram_romaneio',
        data: {
            Romaneio: romaneio,
            idCliente: idcliente,
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
    var status = $("#select-status").val()
    var idcliente = $(this).data("idcliente")
    $(this).hide()
    $.ajax({
        type: 'GET',
        url: '/romaneios/envia_telegram_relatorio',
        data: {
            status: status,
            idCliente: idcliente,
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
    var idromaneio = $(this).data("idromaneio")
    var idcliente = $(this).data("idcliente")
    $.ajax({
        type: 'GET',
        url: '/romaneios/edita_romaneio',
        data: {
            idRomaneio: idromaneio,
            idCliente: idcliente,
        },
        beforeSend: function() {
            $(".card-form-romaneios").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            console.log(data)
            $(".card-form-romaneios").html(data.html_form_romaneios)
            $(".js-mostra-oculta-form-romaneio").toggleClass("bi-chevron-up");
            $(".card-form-romaneios").show()
            $(".box-loader").hide();
            $(window).scrollTop(0)
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
            $(".box-loader").show();
            $(".card-lista-romaneios").hide()
            $(".filtra-romaneio").val("");
        },
        success: function(data) {
            $(".card-lista-notas-romaneio").html(data.html_lista_notas_romaneio)
            $(".card-lista-notas-romaneio").show()
            $(".js-adiciona-nota-romaneio").show()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-filtra-emitente', function() {
    var emitente = $(".filtra-emitente").val()
    var idcliente = $("#id_cliente").val()
    $.ajax({
        type: 'GET',
        url: '/romaneios/seleciona_filtro_emitente',
        data: {
            emitente: emitente,
            idcliente: idcliente,
        },
        beforeSend: function() {
            $(".box-loader").show();
            $(".card-lista-notas-cliente").hide()
            $(".filtra-romaneio").val("");
        },
        success: function(data) {
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-filtra-destinatario', function() {
    var destinatario = $(".filtra-destinatario").val()
    var idcliente = $("#id_cliente").val()
    $.ajax({
        type: 'GET',
        url: '/romaneios/seleciona_filtro_destinatario',
        data: {
            destinatario: destinatario,
            idcliente: idcliente,
        },
        beforeSend: function() {
            $(".box-loader").show();
            $(".card-lista-notas-cliente").hide()
            $(".filtra-romaneio").val("");
        },
        success: function(data) {
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
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
            $(".box-loader").show()
            $(".carddquintisadt-notas-noaideromaneio").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-lista-notas-romaneio").html(data.html_lista_notas_romaneio)
            $(".card-lista-notas-romaneio").show()
            $(".card-quantidade-notas").html(data.html_quantidade_notas)
            $(".card-quantidade-notas").show()
            $(".box-loader").hide()
        },
    });
});

$(document).on('click', '.js-exclui-nota-romaneio', function() {
    var idromaneionotas = $(this).data("idromaneionotas")
    var idromaneio = $('#id_romaneio').val()
    var idnota = $(this).data("idnota")
    var idcliente = $(this).data("idcliente")
    var status = $("#select-status").val()
    $.ajax({
        type: 'GET',
        url: '/romaneios/exclui_nota_romaneio',
        data: {
            idRomaneioNota: idromaneionotas,
            idRomaneio: idromaneio,
            idNota: idnota,
            idCliente: idcliente,
            status: status,
        },
        beforeSend: function() {
            $(".box-loader").show()
            $(".card-lista-notas-cliente").hide()
            $(".card-lista-notas-romaneio").hide()
            $(".card-lista-ocorrencia").hide()
            $(".card-quantidade-notas").hide()
        },
        success: function(data) {
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
            $(".card-lista-notas-romaneio").html(data.html_lista_notas_romaneio)
            $(".card-lista-notas-romaneio").show()
            $(".card-quantidade-notas").html(data.html_quantidade_notas)
            $(".card-quantidade-notas").show()
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
    var idnota = $(this).data("idnota")
    var idcliente = $(this).data("idcliente")
    var filtro = $("#select-status").val()
    $.ajax({
        type: 'GET',
        url: '/romaneios/exclui_nota_cliente',
        data: {
            idNota: idnota,
            idCliente: idcliente,
            filtro: filtro,
        },
        beforeSend: function() {
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-notas-cliente").html(data.html_lista_notas_cliente)
            $(".card-lista-notas-cliente").show()
            $(".card-quantidade-notas").html(data.html_quantidade_notas)
            $(".card-quantidade-notas").show()
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
    var idromaneio = $(this).data("idromaneio")
    var idcliente = $(this).data("idcliente")
    $.ajax({
        type: 'GET',
        url: '/romaneios/fecha_romaneio',
        data: {
            idRomaneio: idromaneio,
            idCliente: idcliente,
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

$(document).on('click', '.js-reabre-romaneio', function() {
    var idromaneio = $(this).data("idromaneio")
    var idcliente = $(this).data("idcliente")
    $.ajax({
        type: 'GET',
        url: '/romaneios/reabre_romaneio',
        data: {
            idRomaneio: idromaneio,
            idCliente: idcliente,
        },
        beforeSend: function() {
            $(".card-lista-romaneios").hide()
            $(".card-lista-notas-romaneio").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-romaneios").html(data.html_lista_romaneios)
            $(".card-lista-romaneios").show()
            $(".box-loader").hide();
        },
    });
});

$(document).on('click', '.js-sort-notas', function() {
    var anr_hidden = $(".js-adiciona-nota-romaneio").is(":hidden")
    var status = $("#select-status").val()
    var tipo_sort = $(".js-tipo-sort").val()
    var idcliente = $(this).data("idcliente")
    var sort = $(this).data("sort")
    $.ajax({
        type: 'GET',
        url: '/romaneios/orderna_notas',
        data: {
            cliente: idcliente,
            sort: sort,
            tipo_sort: tipo_sort,
            status: status,
        },
        beforeSend: function() {
            $(".card-lista-notas-cliente").hide()
            $(".box-loader").show();
        },
        success: function(data) {
            $(".card-lista-notas-cliente").html(data.html_card_lista_notas_cliente)
            $(".js-notas-filtro").html("NOTAS " + status)
            $(".card-lista-notas-cliente").show()
            $(".js-envia-telegram-relatorio").hide()
            if (anr_hidden) {
                $(".js-adiciona-nota-romaneio").hide()
            }
            $(".js-print-relatorio").prop('href', function() {
                var href = $(".js-print-relatorio").prop('href');
                var url = new URL(href);
                url.searchParams.set('ordem', sort);
                $(".js-print-relatorio").attr("href", url.toString());
            });
            $(".box-loader").hide();
        },
    });
});

$(document).on('change', $('.js-file-xml'), function() {
    if ($('.js-file-xml').val()) {
        $('.js-xmlTxt').text($('.js-file-xml').val().match(/[\/\\]([\w\d\s\.\-\(\)]+)$/)[1]);
        $('.js-xmlTxt').text($('.js-xmlTxt').text().substring(0, 28) + '...');
    } else {
        $('.js-xmlTxt').text('Selecionar XML.');
    }
});

$(document).on('change', $('.js-directory-xml'), function() {
    $('#btn-pasta-arquvios-xml').hide()
    var input = document.getElementById('directory-xml');
    var files = input.files
    var xmlFiles = [];
    $.each(files, function(index, value) {
        if (value.name.endsWith('.xml')) {
            xmlFiles.push(value);
        }
    });
    var xmlFiles_length = xmlFiles.length
    if (xmlFiles.length == 0) {
        $(".btn-pasta-arquivos-xml").hide()
        $(".btn-extra-pasta-arquivos-xml").show()
    } else {
        $(".btn-pasta-arquivos-xml").show()
        $(".btn-extra-pasta-arquivos-xml").hide()
    }
    $('.js-total-xml').text(xmlFiles_length + ' Arquivos XML')
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
            $("#emitente").val(data["emitente"])
            $("#endereco_emi").val(data["endereco_emi"])
            $("#bairro_emi").val(data["bairro_emi"])
            $("#cep_emi").val(data["cep_emi"])
            $("#cidade_emi").val(data["cidade_emi"])
            $("#estado_emi").val(data["estado_emi"])
            $("#datanota").val(data["data_nf"])
            $("#serienota").val(data["serie_nf"])
            $("#numeronota").val(data["numero_nf"])
            $("#destinatario").val(data["destinatario"])
            $("#cnpj").val(data["cnpj"])
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

$(document).on('submit', '.js-carrega-pasta-xml', function(event) {
    event.preventDefault();
    var formData = new FormData()
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    var local_coleta = $("#localcoleta-pasta").val();
    var id_cliente = $("#id_cliente").val();
    formData.append("csrfmiddlewaretoken", csrftoken);
    formData.append("local_coleta", local_coleta);
    formData.append("id_cliente", id_cliente);
    var input = document.getElementById('directory-xml');
    var files = input.files
    var xmlFiles = [];
    $.each(files, function(index, value) {
        if (value.name.endsWith('.xml')) {
            formData.append('xml_files', value)
        }
    });
    var xmlFiles_length = xmlFiles.length
    $('.js-total-xml').text(xmlFiles_length + ' Arquivos XML')
    $.ajax({
        type: $(this).attr('method'),
        url: '/romaneios/carrega_pasta_xml',
        processData: false,
        contentType: false,
        data: formData,
        beforeSend: function() {
            $(".text-loader").text("Aguarde, Salvando " + xmlFiles_length + " arquivos XML");
            $(".box-loader").show();
            $(".card-lista-notas-cliente").hide()
            $(".card-quantidade-notas").hide()
        },
        success: function(data) {
            $(".text-loader").text("Aguarde...");
            $(".card-lista-notas-cliente").html(data.html_card_lista_notas_cliente)
            $(".js-notas-filtro").html("NOTAS CADASTRADAS")
            $(".card-lista-notas-cliente").show()
            $(".card-lista-romaneios").show()
            $(".js-adiciona-nota-romaneio").hide()
            $(".card-quantidade-notas").html(data.html_quantidade_notas)
            $(".card-quantidade-notas").show()
            $(".box-loader").hide()
            $(window).scrollTop(0)
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
