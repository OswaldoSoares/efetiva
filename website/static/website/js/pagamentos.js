$(document).ready(function() {
    $(".card-cartao-ponto").hide()
    $(".card-folha").hide()
    $(".card-funcionario-pagamento").hide()
    $(".card-contra-cheque").hide()
    $(".card-minutas-pagamento").hide()
    $(".card-vales-colaborador").hide()
});

// Seleciona mês e ano para pagamento de colaboradores mensalistas
$(document).on("click", ".js-seleciona-mes-ano", function(event) {
    mes_ano = $(".select-mes-ano option:selected").text();
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/pagamentos/seleciona_mes_ano",
        data: {
            mes_ano: mes_ano,
        },
        beforeSend: function() {
            localStorage.setItem("mes_ano", mes_ano)
            $(".card-periodo-avulso").hide();
            $('.box-loader').show();
        },
        success: function(data) {
            $(".card-folha").html(data.html_folha);
            $(".card-folha").show();
            // $(".s-saldo").html(data.html_saldo);
            $('.box-loader').hide()
        },
    });
});

// Seleciona funcionário mensalista
$(document).on("click", ".js-seleciona-funcionario", function(event) {
    v_mes_ano = $(".select-mes-ano option:selected").text();
    v_idpessoal = $(this).data("idpessoal");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/pagamentos/seleciona_funcionario",
        data: {
            mes_ano: v_mes_ano,
            idpessoal: v_idpessoal,
        },
        beforeSend: function() {
            $('.box-loader').show();
        },
        success: function(data) {
            $(".card-cartao-ponto").html(data.html_cartao_ponto);
            $(".card-funcionario-pagamento").html(data.html_funcionario);
            $(".card-minutas-pagamento").html(data.html_minutas);
            $(".card-vales-colaborador").html(data.html_vales);
            // $(".js-lista-vales").html(data.html_vales_pagamento);
            // $(".js-files-pagamento").html(data.html_files_pagamento);
            // $(".js-agenda-pagamento").html(data.html_agenda_pagamento);
            // $(".js-itens-agenda-pagamento").html(data.html_itens_agenda_pagamento);
            $(".card-cartao-ponto").show()
            $(".card-funcionario-pagamento").show()
            // $(".body-funcionario-pagamento").hide()
            $(".card-minutas-pagamento").show();
            // $(".body-minutas-pagamento").hide()
            $(".card-vales-colaborador").show()
            localStorage.setItem("idcontracheque", $("#idcontracheque").data("idcontracheque"))
            localStorage.setItem("idpessoal", v_idpessoal)
            $('.box-loader').hide();
        },
    });
});

var maxHeight = 0;
var topPosition = 0;

var tamanho_body_saldo_avulso;

var tamanhoCardBodyAvulso = function() {
    var saldo_avulso_top = $('.js-body-saldo-avulso').position().top
    var saldo_avulso_height = $('.js-body-saldo-avulso').height()
    var saldo_avulso_area = saldo_avulso_top + saldo_avulso_height
    var minutas_avulso_top = $('.js-body-minutas-avulso').position().top
    var minutas_avulso_height = $('.js-body-minutas-avulso').height()
    var minutas_avulso_area = minutas_avulso_top + minutas_avulso_height
    var recibos_avulso_top = $('.js-body-recibos-avulso').position().top
    var recibos_avulso_height = $('.js-body-recibos-avulso').height()
    var recibos_avulso_area = recibos_avulso_top + recibos_avulso_height
    var areas = [saldo_avulso_area, minutas_avulso_area, recibos_avulso_area]
    maior = Math.max(...areas)
    $('.js-body-saldo-avulso').height(maior - saldo_avulso_top)
    $('.js-body-minutas-avulso').height(maior - minutas_avulso_top)
    $('.js-body-recibos-avulso').height(maior - recibos_avulso_top)
}



$(document).on("change", ".select-mes-ano", function(event) {
    $(".js-folha").html('');
    $(".js-saldo").html('');
    $(".js-adiantamento").html('')
    $(".js-funcionario-pagamento").html('');
    $(".js-cartao-ponto").html('');
    $(".js-itens-contra-cheque").html('');
    $(".js-contra-cheque").html('');
    $(".js-cria-vales").html('')
    $(".js-minutas-pagamento").html('')
    $(".js-lista-vales").html('')
    $(".js-files-pagamento").html('')
    $(".js-agenda-pagamento").html('')
    $(".js-itens-agenda-pagamento").html('');
});



$(document).on("click", ".js-altera-falta", function(event) {
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    var v_idcartaoponto = $(this).data("idcartaoponto");
    var v_idpessoal = $(this).data("idpessoal");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/pagamentos/ausencia_falta",
        data: {
            mes_ano: v_mes_ano,
            idcartaoponto: v_idcartaoponto,
            idpessoal: v_idpessoal,
        },
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-cartao-ponto").html(data.html_cartao_ponto);
            $(".js-funcionario-pagamento").html(data.html_funcionario);
            $(".js-contra-cheque").html(data.html_contra_cheque);
            $(".js-saldo").html(data.html_saldo);
            $('.box-loader').hide()
        },
        error: function(error, data) {
            console.log(error);
        },
    });
});

$(document).on("click", ".js-altera-carro-empresa", function(event) {
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    var v_idcartaoponto = $(this).data("idcartaoponto");
    var v_idpessoal = $(this).data("idpessoal");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/pagamentos/carro_empresa",
        data: {
            mes_ano: v_mes_ano,
            idcartaoponto: v_idcartaoponto,
            idpessoal: v_idpessoal,
        },
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-cartao-ponto").html(data.html_cartao_ponto);
            $(".js-funcionario-pagamento").html(data.html_funcionario);
            $(".js-contra-cheque").html(data.html_contra_cheque);
            $(".js-saldo").html(data.html_saldo);
            $('.box-loader').hide()
        },
        error: function(error, data) {
            console.log(error);
        },
    });
});

$(document).on("click", ".js-atestada", function(event) {
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    var v_idcartaoponto = $(this).data("idcartaoponto");
    var v_idpessoal = $(this).data("idpessoal");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/pagamentos/atestada",
        data: {
            mes_ano: v_mes_ano,
            idcartaoponto: v_idcartaoponto,
            idpessoal: v_idpessoal
        },
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-cartao-ponto").html(data.html_cartao_ponto);
            $(".js-funcionario-pagamento").html(data.html_funcionario);
            $(".js-contra-cheque").html(data.html_contra_cheque);
            $(".js-saldo").html(data.html_saldo);
            $('.box-loader').hide();
        },
        error: function(error, data) {
            console.log(error);
        },
    });
});

$(document).on('submit', '.js-gera-adiantamento', function(event) {
    event.preventDefault();
    var v_mes_ano = $('#mes_ano_adiantamento').val();
    $.ajax({
        type: $(this).attr('method'),
        url: '/pagamentos/adiantamento',
        data: $(this).serialize(),
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $('.box-loader').hide()
        },
    });
});


$(document).on('click', '.js-gera-adiantamento-automatico', function() {
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    $.ajax({
        type: $(this).attr('method'),
        url: '/pagamentos/adiantamento_automatico',
        data: {
            mes_ano: v_mes_ano,
        },
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-folha").html(data.html_folha);
            $(".js-saldo").html(data.html_saldo);
            $(".js-adiantamento").html(data.html_adiantamento);
            $(".js-funcionario-pagamento").html('');
            $(".js-cartao-ponto").html('');
            $(".js-itens-contra-cheque").html('');
            $(".js-contra-cheque").html('');
            $(".js-cria-vales").html('')
            $(".js-minutas-pagamento").html('')
            $(".js-lista-vales").html('')
            $(".js-files-pagamento").html('')
            $(".js-agenda-pagamento").html('')
            $(".js-itens-agenda-pagamento").html('');
            $('.box-loader').hide()
        },
    });
});

$(document).on('submit', '.js-gera-contra-cheque-itens', function(event) {
    event.preventDefault();
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    $.ajax({
        type: $(this).attr('method'),
        url: '/pagamentos/adiciona_contra_cheque_itens',
        data: $(this).serialize(),
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-contra-cheque").html(data.html_contra_cheque);
            $(".js-saldo").html(data.html_saldo);
            $('.box-loader').hide()
        },
    });
});

$(document).on('submit', '.js-gera-agenda', function(event) {
    event.preventDefault();
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    $.ajax({
        type: $(this).attr('method'),
        url: '/pagamentos/adiciona_agenda',
        data: $(this).serialize(),
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-agenda-pagamento").html(data.html_agenda_pagamento)
            $(".js-itens-agenda-pagamento").html(data.html_itens_agenda_pagamento)
            $('.box-loader').hide()
        },
    });
});

$(document).on('click', '.js-carrega-agenda', function() {
    var _idagenda = $(this).data('idagenda')
    var _mes_ano = $(".select-mes-ano option:selected").text();
    var _idpessoal = $(this).data("idpessoal");
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: '/pagamentos/carrega_agenda',
        data: {
            idagenda: _idagenda,
            mes_ano: _mes_ano,
            idpessoal: _idpessoal
        },
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-agenda-pagamento").html(data.html_agenda_pagamento)
            $('.box-loader').hide()
        }
    })

})

$(document).on('click', '.js-exclui-agenda', function() {
    var _idagenda = $(this).data('idagenda')
    var _mes_ano = $(".select-mes-ano option:selected").text();
    var _idpessoal = $(this).data("idpessoal");
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: '/pagamentos/exclui_agenda',
        data: {
            idagenda: _idagenda,
            mes_ano: _mes_ano,
            idpessoal: _idpessoal
        },
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-itens-agenda-pagamento").html(data.html_itens_agenda_pagamento)
            $('.box-loader').hide()
        }
    })

})

$(document).on('click', '.js-exclui-contra-cheque-itens', function(event) {
    var v_idcontrachequeitens = $(this).data('idcontrachequeitens')
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    var v_idpessoal = $(this).data("idpessoal");
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: '/pagamentos/remove_contra_cheque_itens',
        data: {
            idcontrachequeitens: v_idcontrachequeitens,
            mes_ano: v_mes_ano,
            idpessoal: v_idpessoal,
        },
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-contra-cheque").html(data.html_contra_cheque);
            $(".js-saldo").html(data.html_saldo);
            $(".js-lista-vales").html(data.html_vales_pagamento)
            $('.box-loader').hide()
        },
    });
});

$(document).on('submit', '.js-gera-vales', function(event) {
    event.preventDefault();
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    $.ajax({
        type: $(this).attr('method'),
        url: '/pagamentos/adiciona_vales',
        data: $(this).serialize(),
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-cria-vales").html(data.html_vales)
            $(".js-lista-vales").html(data.html_vales_pagamento)
            $('.box-loader').hide()
        },
    });
});

$(document).on('click', '.js-seleciona-vale', function(event) {
    var v_idvales = $(this).data('idvales')
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    var v_idpessoal = $(this).data("idpessoal");
    var v_idcontracheque = $(this).data('idcontracheque')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: '/pagamentos/seleciona_vales',
        data: {
            idvales: v_idvales,
            mes_ano: v_mes_ano,
            idpessoal: v_idpessoal,
            idcontracheque: v_idcontracheque
        },
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-contra-cheque").html(data.html_contra_cheque);
            $(".js-saldo").html(data.html_saldo);
            $(".js-lista-vales").html(data.html_vales_pagamento);
            $('.box-loader').hide()
        },
    })
});

$(document).on('click', '.js-exclui-vale', function(event) {
    var v_idvales = $(this).data('idvales')
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    var v_idpessoal = $(this).data("idpessoal");
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: '/pagamentos/remove_vales',
        data: {
            idvales: v_idvales,
            mes_ano: v_mes_ano,
            idpessoal: v_idpessoal,
        },
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-lista-vales").html(data.html_vales_pagamento)
            $('.box-loader').hide()
        },
    })
});

$(document).on('change', '.js-file-contracheque', function() {
    if ($('.js-file-contracheque').val()) {
        $('.js-contrachequeTxt').text($('.js-file-contracheque').val().match(/[\/\\]([\w\d\s\.\-\(\)]+)$/)[1]);
    } else {
        $('.js-contrachequeTxt').text('Selecionar comprovante.');
    }
});

$(document).on('change', '.js-file-adiantamento', function() {
    if ($('.js-file-adiantamento').val()) {
        $('.js-adiantamentoTxt').text($('.js-file-adiantamento').val().match(/[\/\\]([\w\d\s\.\-\(\)]+)$/)[1]);
    } else {
        $('.js-adiantamentoTxt').text('Selecionar comprovante.');
    }
});

$(document).on('change', '.js-file-diversos', function() {
    if ($('.js-file-diversos').val()) {
        $('.js-diversosTxt').text($('.js-file-diversos').val().match(/[\/\\]([\w\d\s\.\-\(\)]+)$/)[1]);
    } else {
        $('.js-diversosTxt').text('Selecionar comprovante.');
    }
});

$(document).on('submit', '.js-salva-file', function(event) {
    event.preventDefault();
    var _formData = new FormData();
    var _tipo_comprovante = $(this).data('tipo');
    var _arquivo = $("#file_" + _tipo_comprovante).get(0).files[0]
    var _csrf_token = $('input[name="csrfmiddlewaretoken"]').val()
    var _nome_curto = $("#id_nome_curto").val()
    var _mes_ano = $(".select-mes-ano option:selected").text();
    var _idpessoal = $("#idpessoal").val()
    _formData.append("arquivo", _arquivo);
    _formData.append("csrfmiddlewaretoken", _csrf_token);
    _formData.append("nome_curto", _nome_curto);
    _formData.append("mes_ano", _mes_ano);
    _formData.append("idpessoal", _idpessoal);
    _formData.append("tipo_comprovante", _tipo_comprovante);
    $.ajax({
        type: $(this).attr('method'),
        url: '/pagamentos/salva_file',
        data: _formData,
        cache: false,
        processData: false,
        contentType: false,
        enctype: 'multipart/form-data',
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-files-pagamento").html(data.html_files_pagamento)
            $('.box-loader').hide()
        },
    });
});

$(document).on('click', '.js-delete-file', function() {
    var _idfileupload = $(this).data('idfileupload')
    var _mes_ano = $(".select-mes-ano option:selected").text();
    var _idpessoal = $(this).data('idpessoal')
    $.ajax({
        url: '/pagamentos/delete_file',
        type: 'GET',
        data: {
            idfileupload: _idfileupload,
            mes_ano: _mes_ano,
            idpessoal: _idpessoal,
        },
        beforeSend: function() {
            $('.box-loader').show()
        },
        success: function(data) {
            $(".js-files-pagamento").html(data.html_files_pagamento)
            $('.box-loader').hide()
        }
    });
});


// Seleciona periodo de pagamento para colaboradores avulso
$(document).on("click", ".js-periodo-avulso", function(event) {
    var _data_inicial = $("#data_inicial").val()
    var _data_final = $("#data_final").val()
    $.ajax({
        type: "GET",
        dataType: "JSON",
        url: '/pagamentos/seleciona_periodo_avulso',
        data: {
            DataInicial: _data_inicial,
            DataFinal: _data_final,
        },
        beforeSend: function() {
            $(".box-loader").show();
            $(".div-um").hide()
            $(".div-dois").hide()
            $(".div-tres").hide()
            $(".div-quatro").hide()
            $(".card-minutas-avulso").hide()
            $(".card-recibos-avulso").hide()
            $(".js-body-saldo-avulso").height(tamanho_body_saldo_avulso)
        },
        success: function(data) {
            $(".card-saldo-avulso").html(data.html_saldoavulso);
            tamanho_body_saldo_avulso = $('.js-body-saldo-avulso').height()
            $(".div-seis").show();
            $(".div-sete").show();
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log(error);
        }
    });
});

$(document).on("submit", "#form-vale", function(event) {
    event.preventDefault();
    var url = $(this).attr("action") || action;
    $.ajax({
        type: $(this).attr("method"),
        url: url,
        data: $(this).serialize(),
        success: function(data) {
            if (data.html_vales) {
                $(".fp-vales").html(data.html_vales);
            }
            if (data.html_valesavulso) {
                $(".pa-vales").html(data.html_valesavulso);
            }
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("click", ".estorna-recibo", function(event) {
    var idrecibo = $(this).data("idrecibo");
    var idpessoal = $(this).data("idpessoal");
    var data_inicial = $('#data_inicial').val();
    var data_final = $('#data_final').val();
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/pagamentos/excluirecibo",
        data: {
            idrecibo: idrecibo,
            idpessoal: idpessoal,
            data_inicial: data_inicial,
            data_final: data_final,
        },
        beforeSend: function() {
            $(".box-loader").show()
            $(".card-minutas-avulso").hide();
            $(".card-recibos-avulso").hide();
        },
        success: function(data) {
            $(".card-saldo-avulso").html(data.html_saldoavulso);
            tamanho_body_saldo_avulso = $('.js-body-saldo-avulso').height()
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("click", ".js-form-paga-recibo", function(event) {
    var idrecibo = $(this).data("idrecibo");
    var idpessoal = $(this).data("idpessoal");
    var recibo = $(this).data("recibo");
    var valor_recibo = $(this).data("valor");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/pagamentos/form_paga_recibo",
        data: {
            idrecibo: idrecibo,
            idpessoal: idpessoal,
            recibo: recibo,
            valor_recibo: valor_recibo,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_paga_recibo_colaborador);
            $(".card-form-colaborador").show()
            tamanho_body_saldo_avulso = $('.js-body-saldo-avulso').height()
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("submit", ".js-paga-recibo-colaborador", function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr("method"),
        url: "/pagamentos/paga_recibo",
        data: $(this).serialize(),
        beforeSend: function() {
            $('.card-recibos-colaborador').hide()
            $('.card-form-colaborador').hide()
            $('.box-loader').show()
        },
        success: function(data) {
            $(".card-recibos-colaborador").html(data.html_vales);
            $(".card-recibos-colaborador").show();
            $('.box-loader').hide()
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("click", ".js-gera-pagamento-avulso", function(event) {
    var idpessoal = $(this).data("idpessoal");
    var datainicial = $(this).data("datainicial");
    var datafinal = $(this).data("datafinal");
    var zerado = $(this).data("zerado");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: '/pagamentos/gera_pagamento_avulso',
        data: {
            idPessoal: idpessoal,
            DataInicial: datainicial,
            DataFinal: datafinal,
            Zerado: zerado,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-saldo-avulso").html(data.html_saldoavulso);
            tamanho_body_saldo_avulso = $('.js-body-saldo-avulso').height()
            $(".card-minutas-avulso").html(data.html_minutas);
            $(".card-recibos-avulso").html(data.html_recibos);
            $(".js-recibo-novo").get(0).click();
            tamanhoCardBodyAvulso();
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("click", ".js-seleciona-colaborador-avulso", function(event) {
    var datainicial = $(this).data("datainicial");
    var datafinal = $(this).data("datafinal");
    var idpessoal = $(this).data("idpessoal");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: '/pagamentos/seleciona_colaborador_avulso',
        data: {
            DataInicial: datainicial,
            DataFinal: datafinal,
            idPessoal: idpessoal,
        },
        beforeSend: function() {
            $(".box-loader").show()
            $(".js-body-saldo-avulso").height(tamanho_body_saldo_avulso)
            $(".card-saldo-avulso").hide()
            $(".card-minutas-avulso").hide()
            $(".card-recibos-avulso").hide()
        },
        success: function(data) {
            $(".card-minutas-avulso").html(data.html_minutas);
            $(".card-recibos-avulso").html(data.html_recibos);
            $(".card-saldo-avulso").show();
            $(".card-minutas-avulso").show();
            $(".card-recibos-avulso").show();
            $(".js-recibo-avulso-zerado").hide();
            tamanhoCardBodyAvulso();
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log(error);
        },
    });
});


function openMyModal(event) {
    var modal = initModalDialog(event, "#MyModal");
    var url = $(event.target).data("action");
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    var v_idcartaoponto = $(event.target).data("idcartaoponto");
    alert(modal)
    alert(url)
    alert(v_mes_ano)
    alert(v_idcartaoponto)
    $.ajax({
            type: "GET",
            url: url,
            data: {
                mes_ano: v_mes_ano,
                idcartaoponto: v_idcartaoponto,
            },
        })
        .done(function(data, textStatus, jqXHR) {
            alert(data)
            modal.find(".modal-body").html(data.html_modal);
            modal.modal("show");
            formAjaxSubmit(modal, url, null, null);
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            alert("SERVER ERROR: " + errorThrown);
        });
}

function initModalDialog(event, modal_element) {
    var modal = $(modal_element);
    var target = $(event.target);
    var title = target.data("title") || "";
    var subtitle = target.data("subtitle") || "";
    var dialog_class = (target.data("dialog-class") || "") + " modal-dialog";
    var icon_class = (target.data("icon") || "fa-laptop") + " fa modal-icon";
    var button_save_label = target.data("button-save-label") || "Save changes";
    modal.find(".modal-dialog").attr("class", dialog_class);
    modal.find(".modal-title").text(title);
    modal.find(".modal-subtitle").text(subtitle);
    modal.find(".modal-header .title-wrapper i").attr("class", icon_class);
    modal.find(".modal-footer .btn-save").text(button_save_label);
    modal.find(".modal-body").html("");
    modal.data("target", target);
    return modal;
}

function formAjaxSubmit(modal, action, cbAfterLoad, cbAfterSuccess) {
    var form = modal.find(".modal-body form");
    var header = $(modal).find(".modal-header");
    var btn_save = modal.find(".modal-footer .btn-save");
    if (btn_save) {
        modal.find(".modal-body form .form-submit-row").hide();
        btn_save.off().on("click", function(event) {
            modal.find(".modal-body form").submit();
        });
    }
    if (cbAfterLoad) {
        cbAfterLoad(modal);
    }
    modal.find("form input:visible").first().focus();
    $(form).on("submit", function(event) {
        event.preventDefault();
        header.addClass("loading");
        var url = $(this).attr("action") || action;
        $.ajax({
            type: $(this).attr("method"),
            url: url,
            idobj: $(this).attr("idobj"),
            data: $(this).serialize(),
            success: function(xhr, ajaxOptions, thrownError) {
                $(modal).find(".modal-body").html(xhr["html_form"]);
                if ($(xhr["html_form"]).find(".errorlist").length > 0) {
                    formAjaxSubmit(modal, url, cbAfterLoad, cbAfterSuccess);
                } else {
                    $(modal).modal("hide");
                    $(".js-cartao-ponto").html(xhr.html_cartao_ponto);
                    $(".js-contra-cheque").html(xhr.html_contra_cheque);
                    $(".js-saldo").html(xhr.html_saldo);
                    if (cbAfterSuccess) {
                        cbAfterSuccess(modal);
                    }
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                console.log("SERVER ERROR: " + thrownError);
            },
            complete: function() {
                header.removeClass("loading");
            },
        });
    });
}

function valeselect(idpessoal) {
    var data = [];
    var total = 0.0;
    $(".switchmini").each(function() {
        if (
            $(this).is(":checked") &&
            $(this).data("idPessoal") == idpessoal.substring(6)
        ) {
            total += parseFloat($(this).data("valorvale").replace(",", "."));
            data.push($(this).data("id"));
        }
        $(idpessoal).text("R$ " + total.toFixed(2).replace(".", ","));
    });
    return data;
}

function somavales() {
    var total = 0.0;
    $(".saldovale").each(function() {
        total += parseFloat($(this).text().replace("R$ ", "").replace(",", "."));
    });
    $("#totalvales").text("R$ " + total.toFixed(2).replace(".", ","));
}

function estadoswitchmini(idpessoal) {
    estado_switchmini = "Manual-";
    $(".switchmini").each(function() {
        if ($(this).is(":checked")) {
            if ($(this).data("idpessoal") == idpessoal) {
                estado_switchmini += $(this).data("idvales") + "-";
            }
        }
    });
    return estado_switchmini;
}

document.addEventListener("keydown", function(event) {
    if (event.altKey && event.code === "KeyT") {
        $(".js-gera-pagamento-avulso").hide();
        $(".js-recibo-avulso-zerado").show();
        event.preventDefault();
    }
});


$(document).on('click', '.js-pessoas-seleciona-vale', function() {
    var idvale = $(this).data("idvale")
    var idpessoal = localStorage.getItem("idpessoal")
    var idcontracheque = localStorage.getItem("idcontracheque")
    if (idcontracheque != "") {
        $.ajax({
            type: "GET",
            url: "/pessoas/adiciona_vale_contra_cheque",
            data: {
                idvale: idvale,
                idpessoal: idpessoal,
                idcontracheque: idcontracheque,
            },
            beforeSend: function() {
                $(".box-loader").show()
            },
            success: function(data) {
                $(".card-contra-cheque").html(data.html_card_contra_cheque_colaborador)
                $(".card-contra-cheque").show()
                $(".card-vales-colaborador").html(data.html_vales_colaborador)
                $(".card-vales-colaborador").show()
                $(".box-loader").hide()
            },
        });
    }
});

$(document).on('click', '.js-pessoas-exclui-contra-cheque-item', function () {
    var idpessoal = localStorage.getItem("idpessoal")
    var idcontracheque = $(this).data("idcontracheque")
    var idcontrachequeitens = $(this).data("idcontrachequeitens")
    $.ajax({
        type: "GET",
        url: "/pessoas/exclui_contra_cheque_item",
        data: {
            idpessoal: idpessoal,
            idcontracheque: idcontracheque,
            idcontrachequeitens: idcontrachequeitens,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-contra-cheque").html(data.html_card_contra_cheque_colaborador)
            $(".card-contra-cheque").show()
            $(".card-vales-colaborador").html(data.html_vales_colaborador)
            $(".card-vales-colaborador").show()
            $(".box-loader").hide()
        },
    });
});


$(document).on('click', '.js-contra-cheque-pagamento', function() {
    var idpessoal = localStorage.getItem("idpessoal")
    var mes_ano = localStorage.getItem("mes_ano")
    var descricao = "PAGAMENTO"
    $.ajax({
        type: "GET",
        url: "/pagamentos/seleciona_contra_cheque",
        data: {
            idpessoal: idpessoal,
            mes_ano: mes_ano,
            descricao:  descricao,
        },
        beforeSend: function() {
            $(".box-loader").show()
            $(".card-contra-cheque-colaborador").hide()
            localStorage.setItem("idcontracheque", "")
        },
        success: function(data) {
            $(".card-contra-cheque").html(data.html_contra_cheque)
            $(".card-contra-cheque").show()
            localStorage.setItem("idcontracheque", $("#idcontracheque").data("idcontracheque"))
            $(".box-loader").hide()
        },
    });
});

