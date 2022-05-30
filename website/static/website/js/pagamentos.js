$(document).ready(function() {
    window.MesReferencia = "";
    window.AnoReferencia = "";
    window.idpessoal = "";
    $(".down-folha").hide();
    $(".down-avulso").hide();
    $('[data-toggle="tooltip"]').tooltip();
    $('#id_data').val('2022-05-18');
    tamanhoCardBody();
});

$(document).on("change", "#id_MesReferencia", function(event) {
    $(".fp-base").html("");
    $(".fp-contrachequeitens").html("");
    $(".fp-adiantamento").html("");
    $(".fp-adiantamento").hide();
});

$(document).on("change", "#id_AnoReferencia", function(event) {
    $(".fp-base").html("");
    $(".fp-contrachequeitens").html("");
    $(".fp-adiantamento").html("");
    $(".fp-adiantamento").hide();
});

var maxHeight = 0;
var topPosition = 0;
var tamanhoCardBody = function() {
    var topPosition = $('.card-mes-ano').position().top
    var cci_top = $('.js-itens-contra-cheque').position().top
    var fil_top = $('.js-files-pagamento').position().top
    var fil_hei = $('.js-body-files-pagamento').height()
    var fil_area = fil_top + fil_hei
        // var adi_top = $('.js-adiantamento').position().top
    var fun_top = $('.js-funcionario-pagamento').position().top
    var fun_hei = $('.js-body-funcionario').height()
    var fun_area = fun_top + fun_hei
    var car_top = $('.js-cartao-ponto').position().top
    var car_hei = $('.js-body-cartao-ponto').height()
    var car_area = car_top + car_hei
    var coc_top = $('.js-contra-cheque').position().top
    var coc_hei = $('.js-body-contra-cheque').height()
    var coc_area = coc_top + coc_hei
    var min_top = $('.js-minutas-pagamento').position().top
    var min_hei = $('.js-body-minutas-pagamento').height()
    var min_area = min_top + min_hei
    var val_top = $('.js-vales-pagamento').position().top
    var val_hei = $('.js-body-vales-pagamento').height()
    var val_area = val_top + val_hei

    if (car_top == topPosition && cci_top == topPosition && fil_top == topPosition) {
        var areas = [fun_area, car_area, coc_area, val_area]
        maior = Math.max(...areas)
        $('.js-body-funcionario').height(maior - fun_top)
        $('.js-body-cartao-ponto').height(maior - car_top)
        $('.js-body-contra-cheque').height(maior - coc_top)
        $('.js-body-vales-pagamento').height(maior - val_top)
    }

    if (fil_top != topPosition) {
        if (car_top == topPosition && cci_top == topPosition) {
            var areas = [fun_area, car_area, coc_area]
            maior = Math.max(...areas)
            $('.js-body-funcionario').height(maior - fun_top)
            $('.js-body-cartao-ponto').height(maior - car_top)
            $('.js-body-contra-cheque').height(maior - coc_top)
        }
    }

    if ($(window).width() < 1590) {
        var areas = [fil_area, min_area, val_area]
        maior = Math.max(...areas)
        $('.js-body-files-pagamento').height(maior - fil_top)
        $('.js-body-minutas-pagamento').height(maior - min_top)
        $('.js-body-vales-pagamento').height(maior - val_top)
    }
}

$(document).on("click", ".js-seleciona-mes-ano", function(event) {
    v_mes_ano = $(".select-mes-ano option:selected").text();
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/pagamentos/seleciona_mes_ano",
        data: {
            mes_ano: v_mes_ano,
        },
        beforeSend: function() {
            $(".js-folha").fadeOut(10);
            EscondeCards();
        },
        success: function(data) {
            $(".js-folha").html(data.html_folha);
            $(".js-folha").fadeIn(10);
        },
    });
});

$(document).on("change", ".select-mes-ano", function(event) {
    $(".js-folha").fadeOut(10);
    EscondeCards();
});

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
            EscondeCards();
        },
        success: function(data) {
            MostraCards(data, v_mes_ano);
        },
    });
});

function EscondeCards() {
    $(".js-funcionario-pagamento").fadeOut(10);
    $(".js-cartao-ponto").fadeOut(10);
    $(".js-itens-contra-cheque").fadeOut(10);
    $(".js-contra-cheque").fadeOut(10);
    $(".js-vales").fadeOut(10)
    $(".js-adiantamento").fadeOut(10)
    $(".js-minutas-pagamento").fadeOut(10)
    $(".js-vales-pagamento").fadeOut(10)
    $(".js-files-pagamento").fadeOut(10)
}

function MostraCards(data, v_mes_ano) {
    $(".js-funcionario-pagamento").html(data.html_funcionario);
    $(".js-funcionario-pagamento").fadeIn(10);
    $(".js-cartao-ponto").html(data.html_cartao_ponto);
    $(".js-cartao-ponto").fadeIn(10);
    $(".js-itens-contra-cheque").html(data.html_itens_contra_cheque);
    $(".js-itens-contra-cheque").fadeIn(10);
    $(".js-contra-cheque").html(data.html_contra_cheque);
    $(".js-contra-cheque").fadeIn(10);
    $(".js-vales").html(data.html_vales)
    $(".js-vales").fadeIn(10)
    $(".js-adiantamento").html(data.html_adiantamento)
    $(".js-adiantamento").fadeIn(10)
    $(".js-minutas-pagamento").html(data.html_minutas)
    $(".js-minutas-pagamento").fadeIn(10)
    $(".js-vales-pagamento").html(data.html_vales_pagamento)
    $(".js-vales-pagamento").fadeIn(10)
    $(".js-files-pagamento").html(data.html_files_pagamento)
    $(".js-files-pagamento").fadeIn(10)
    $('#mes_ano').val(v_mes_ano)
    $('#mes_ano_adiantamento').val(v_mes_ano)
    tamanhoCardBody();
}

$(document).on("click", ".js-altera-falta", function(event) {
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    var v_idcartaoponto = $(this).attr("idcartaoponto");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/pagamentos/ausencia_falta",
        data: {
            mes_ano: v_mes_ano,
            idcartaoponto: v_idcartaoponto,
        },
        beforeSend: function() {
            EscondeCards();
        },
        success: function(data) {
            MostraCards(data, v_mes_ano);
        },
        error: function(error, data) {
            console.log(error);
        },
    });
});

$(document).on("click", ".js-altera-carro-empresa", function(event) {
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    var v_idcartaoponto = $(this).attr("idcartaoponto");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/pagamentos/carro_empresa",
        data: {
            mes_ano: v_mes_ano,
            idcartaoponto: v_idcartaoponto,
        },
        beforeSend: function() {
            EscondeCards();
        },
        success: function(data) {
            MostraCards(data, v_mes_ano);
        },
        error: function(error, data) {
            console.log(error);
        },
    });
});

$(document).on("click", ".js-atestada", function(event) {
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    var v_idcartaoponto = $(this).attr("idcartaoponto");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: "/pagamentos/atestada",
        data: {
            mes_ano: v_mes_ano,
            idcartaoponto: v_idcartaoponto,
        },
        beforeSend: function() {
            EscondeCards();
        },
        success: function(data) {
            MostraCards(data, v_mes_ano);
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
            EscondeCards();
        },
        success: function(data) {
            MostraCards(data, v_mes_ano);
        },
    });
});

$(document).on('submit', '.js-gera-contra-cheque-itens', function(event) {
    event.preventDefault();
    var v_mes_ano = $('#mes_ano').val();
    $.ajax({
        type: $(this).attr('method'),
        url: '/pagamentos/adiciona_contra_cheque_itens',
        data: $(this).serialize(),
        beforeSend: function() {
            EscondeCards();
        },
        success: function(data) {
            MostraCards(data, v_mes_ano);
        },
    });
});

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
            EscondeCards();
        },
        success: function(data) {
            MostraCards(data, v_mes_ano);
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
            EscondeCards();
        },
        success: function(data) {
            MostraCards(data, v_mes_ano);
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
            EscondeCards();
        },
        success: function(data) {
            MostraCards(data, v_mes_ano);
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
            EscondeCards();
        },
        success: function(data) {
            MostraCards(data, v_mes_ano);
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
            EscondeCards();
        },
        success: function(data) {
            MostraCards(data, v_mes_ano);
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
            EscondeCards()
        },
        success: function(data) {
            MostraCards(data, _mes_ano)
        }
    });
});

// TODO Excluir daqui para baixo após terminar refatoração
$(document).on("change", ".switchmini", function(event) {
    var idpessoalconcatenado = "#vale_" + $(this).attr("idpessoal");
    if ($(this).attr("tipopgto") == "mensalista") {
        if ($(this).is(":checked")) {
            var url = "criacontrachequeitensvale";
        } else {
            var url = "excluicontrachequeitensvale";
        }
        var idpessoal = $(this).attr("idpessoal");
        var idvales = $(this).attr("idvales");
        var idcontracheque = $(this).attr("idcontracheque");
        var mesreferencia = window.MesReferencia;
        var anoreferencia = window.AnoReferencia;
        var estado_switchmini = estadoswitchmini(idpessoal);
        $.ajax({
            type: "GET",
            dateType: "json",
            url: url,
            data: {
                idPessoal: idpessoal,
                idVales: idvales,
                idContraCheque: idcontracheque,
                MesReferencia: mesreferencia,
                AnoReferencia: anoreferencia,
                EstadoSwitchMini: estado_switchmini,
            },
            success: function(data) {
                $(".fp-base").html(data.html_folha);
                $(".fp-contracheque").html(data.html_contracheque);
                $(".fp-minutas").html(data.html_minutascontracheque);
                $(".fp-vales").html(data.html_vales);
                $(".fp-contrachequeitens").html(data.html_formccitens);
                if (data.html_adiantamento == true) {
                    $(".fp-adiantamento").hide();
                } else {
                    $(".fp-adiantamento").show();
                }
                $(".fp-adiantamento").html(data.html_formccadianta);
                $(".fp-contracheque").html(data.html_contracheque);
                $(".fp-cartaoponto").html(data.html_cartaoponto);
            },
        });
    }
    valeselect(idpessoalconcatenado);
    somavales();
});

$(document).on("submit", "#form-seleciona-folha", function(event) {
    event.preventDefault();
    var url = $(this).attr("action") || action;
    window.MesReferencia = $("#id_MesReferencia").val();
    window.AnoReferencia = $("#id_AnoReferencia").val();
    $.ajax({
        type: $(this).attr("method"),
        url: url,
        data: $(this).serialize(),
        success: function(data) {
            $(".fp-base").html(data.html_folha);
            $(".fp-contrachequeitens").html("");
            $(".fp-adiantamento").hide();
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("submit", ".form-cria-contrachequeitens", function(event) {
    event.preventDefault();
    var url = $(this).attr("action") || action;
    $.ajax({
        type: $(this).attr("method"),
        url: url,
        data: $(this).serialize(),
        success: function(data) {
            $(".fp-base").html(data.html_folha);
            $(".fp-minutas").html(data.html_minutascontracheque);
            $(".fp-vales").html(data.html_vales);
            $(".fp-contrachequeitens").html(data.html_formccitens);
            $(".fp-adiantamento").html(data.html_formccadianta);
            if (data.html_adiantamento == true) {
                $(".fp-adiantamento").hide();
            }
            $(".fp-contracheque").html(data.html_contracheque);
            $(".fp-cartaoponto").html(data.html_cartaoponto);
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("submit", "#form-seleciona-periodo", function(event) {
    event.preventDefault();
    var url = $(this).attr("action") || action;
    $.ajax({
        type: $(this).attr("method"),
        url: url,
        data: $(this).serialize(),
        beforeSend: function() {},
        success: function(data) {
            /*  $(".pa-saldo").html("");*/
            $(".pa-saldo-minutas").html(data.html_saldoavulso);
        },
        error: function(error) {
            console.log(error);
        },
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

$(document).on("click", ".selecionar-contracheque", function(event) {
    var url = $(this).attr("data-url");
    var mesreferencia = window.MesReferencia;
    var anoreferencia = window.AnoReferencia;
    var idpessoal = $(this).attr("idpessoal");
    window.idPessoal = $(this).attr("idpessoal");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: url,
        data: {
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        },
        success: function(data) {
            $(".fp-minutas").html(data.html_minutascontracheque);
            $(".fp-vales").html(data.html_vales);
            $(".fp-contrachequeitens").html(data.html_formccitens);
            if (data.html_adiantamento == true) {
                $(".fp-adiantamento").hide();
            } else {
                $(".fp-adiantamento").show();
            }
            $(".fp-adiantamento").html(data.html_formccadianta);
            $(".fp-contracheque").html(data.html_contracheque);
            $(".fp-cartaoponto").html(data.html_cartaoponto);
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("click", ".remove-item", function(event) {
    var url = $(this).attr("data-url");
    var idcontracheque = $(this).attr("idcontracheque");
    var descricao = $(this).attr("descricao");
    var registro = $(this).attr("registro");
    var mesreferencia = window.MesReferencia;
    var anoreferencia = window.AnoReferencia;
    var idpessoal = $(this).attr("idpessoal");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: url,
        data: {
            idContraCheque: idcontracheque,
            Descricao: descricao,
            Registro: registro,
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        },
        success: function(data) {
            $(".fp-base").html(data.html_folha);
            $(".fp-contracheque").html("");
            $(".fp-contracheque").html(data.html_contracheque);
            $(".fp-cartaoponto").html("");
            $(".fp-cartaoponto").html(data.html_cartaoponto);
            $(".fp-contrachequeitens").html("");
            $(".fp-contrachequeitens").html(data.html_formccitens);
            $(".fp-adiantamento").html("");
            $(".fp-adiantamento").html(data.html_formccadianta);
            $(".fp-minutas").html("");
            $(".fp-minutas").html(data.html_minutascontracheque);
            $(".fp-vales").html("");
            $(".fp-vales").html(data.html_vales);
            if (data.html_adiantamento == true) {
                $(".fp-adiantamento").hide();
            }
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("click", ".remove-vale", function(event) {
    var url = $(this).attr("data-url");
    var idvales = $(this).attr("idvales");
    var mesreferencia = window.MesReferencias;
    var anoreferencia = window.AnoReferencia;
    var idpessoal = window.idPessoal;

    $.ajax({
        type: "GET",
        dataType: "json",
        url: url,
        data: {
            idVales: idvales,
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        },
        success: function(data) {
            $(".fp-base").html(data.html_folha);
            $(".fp-contracheque").html("");
            $(".fp-contracheque").html(data.html_contracheque);
            $(".fp-cartaoponto").html("");
            $(".fp-cartaoponto").html(data.html_cartaoponto);
            $(".fp-contrachequeitens").html("");
            $(".fp-contrachequeitens").html(data.html_formccitens);
            $(".fp-adiantamento").html("");
            $(".fp-adiantamento").html(data.html_formccadianta);
            $(".fp-minutas").html("");
            $(".fp-minutas").html(data.html_minutascontracheque);
            $(".fp-vales").html("");
            $(".fp-vales").html(data.html_vales);
            if (data.html_adiantamento == true) {
                $(".fp-adiantamento").hide();
            }
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("click", ".estorna-recibo", function(event) {
    var url = $(this).attr("data-url");
    var idrecibo = $(this).attr("idrecibo");
    var mesreferencia = window.MesReferencias;
    var anoreferencia = window.AnoReferencia;
    var idpessoal = window.idPessoal;

    $.ajax({
        type: "GET",
        dataType: "json",
        url: url,
        data: {
            idRecibo: idrecibo,
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        },
        success: function(data) {
            $(".pa-saldo-minutas").html(data.html_saldoavulso);
            $(".pa-minutas").html(data.html_minutas);
            $(".pa-vales").html(data.html_valesavulso);
            $(".pa-recibos").html(data.html_recibos);
            valeselect("#vale_" + idpessoal);
            somavales();
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("click", "#gerar-folha", function(event) {
    var url = $(this).attr("data-url");
    var mesreferencia = $(this).attr("mesreferencia");
    var anoreferencia = $(this).attr("anoreferencia");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: url,
        data: {
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
        },
        beforeSend: function() {
            $(".fp-base").html("");
            $(".fp-adiantamento").hide();
        },
        success: function(data) {
            $(".fp-base").html(data.html_folha);
            $(".fp-adiantamento").hide();
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("click", "#gerar-pagamento", function(event) {
    var url = $(this).attr("data-url");
    var idpessoal = $(this).attr("idpessoal");
    var datainicial = $(this).attr("datainicial");
    var datafinal = $(this).attr("datafinal");
    var valesselecionados = valeselect("#vale_" + $(this).attr("idpessoal"));
    $.ajax({
        type: "GET",
        dataType: "json",
        url: url,
        data: {
            idPessoal: idpessoal,
            DataInicial: datainicial,
            DataFinal: datafinal,
            ValesSelecionados: valesselecionados,
        },
        success: function(data) {
            $(".pa-saldo-minutas").html(data.html_saldoavulso);
            $(".pa-minutas").html(data.html_minutas);
            $(".pa-vales").html(data.html_valesavulso);
            $(".pa-recibos").html(data.html_recibos);
            valeselect("#vale_" + idpessoal);
            somavales();
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(document).on("click", ".altera-falta", function(event) {
    var url = $(this).attr("data-url");
    var mesreferencia = $(this).attr("mesreferencia");
    var anoreferencia = $(this).attr("anoreferencia");
    var idpessoal = $(this).attr("idpessoal");
    var idcartaoponto = $(this).attr("idcartaoponto");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: url,
        data: {
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
            idCartaoPonto: idcartaoponto,
        },
        success: function(data) {
            $(".fp-base").html(data.html_folha);
            $(".fp-contracheque").html("");
            $(".fp-contracheque").html(data.html_contracheque);
            $(".fp-cartaoponto").html("");
            $(".fp-cartaoponto").html(data.html_cartaoponto);
            $(".fp-adiantamento").html("");
            $(".fp-adiantamento").html(data.html_formccadianta);
            $(".fp-minutas").html("");
            $(".fp-minutas").html(data.html_minutascontracheque);
            $(".fp-vales").html("");
            $(".fp-vales").html(data.html_vales);
            if (data.html_adiantamento == true) {
                $(".fp-adiantamento").hide();
            }
        },
        error: function(error, data) {
            console.log(error);
        },
    });
});

$(document).on("click", ".selecionar-saldoavulso", function(event) {
    var url = $(this).attr("data-url");
    var datainicial = $(this).attr("datainicial");
    var datafinal = $(this).attr("datafinal");
    var idpessoal = $(this).attr("idpessoal");
    $.ajax({
        type: "GET",
        dataType: "json",
        url: url,
        data: {
            DataInicial: datainicial,
            DataFinal: datafinal,
            idPessoal: idpessoal,
        },
        success: function(data) {
            $(".pa-minutas").html(data.html_minutas);
            $(".pa-vales").html(data.html_valesavulso);
            $(".pa-recibos").html(data.html_recibos);
            valeselect("#vale_" + idpessoal);
            somavales();
        },
        error: function(error) {
            console.log(error);
        },
    });
});

$(".div-fade-folha").click(function() {
    if ($("#fp-main").is(":hidden")) {
        $("#fp-main").slideDown("fast");
        $(".up-folha").show();
        $(".down-folha").hide();
    } else {
        $(".up-folha").hide();
        $(".down-folha").show();
        $("#fp-main").slideUp("fast");
    }
});

$(".div-fade-avulso").click(function() {
    if ($("#pa-main").is(":hidden")) {
        $("#pa-main").slideDown("fast");
        $(".up-avulso").show();
        $(".down-avulso").hide();
    } else {
        $(".up-avulso").hide();
        $(".down-avulso").show();
        $("#pa-main").slideUp("fast");
    }
});

function openMyModal(event) {
    var modal = initModalDialog(event, "#MyModal");
    var url = $(event.target).data("action");
    var v_mes_ano = $(".select-mes-ano option:selected").text();
    var v_idcartaoponto = $(event.target).data("idcartaoponto");
    $.ajax({
            type: "GET",
            url: url,
            data: {
                mes_ano: v_mes_ano,
                idcartaoponto: v_idcartaoponto,
            },
        })
        .done(function(data, textStatus, jqXHR) {
            modal.find(".modal-body").html(data.html_form);
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
                    $(".js-cartao-ponto").fadeIn(10);
                    $(".js-contra-cheque").html(xhr.html_contra_cheque);
                    $(".js-contra-cheque").fadeIn(10);

                    $(".fp-base").html(xhr.html_folha);
                    $(".fp-contracheque").html("");
                    $(".fp-contracheque").html(xhr.html_contracheque);
                    $(".fp-cartaoponto").html("");
                    $(".fp-cartaoponto").html(xhr.html_cartaoponto);
                    $(".fp-adiantamento").html("");
                    $(".fp-adiantamento").html(xhr.html_formccadianta);
                    $(".fp-minutas").html("");
                    $(".fp-minutas").html(xhr.html_minutascontracheque);
                    $(".fp-vales").html("");
                    $(".fp-vales").html(xhr.html_vales);
                    if (xhr.html_adiantamento == true) {
                        $(".fp-adiantamento").hide();
                    }
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
            $(this).attr("idPessoal") == idpessoal.substring(6)
        ) {
            total += parseFloat($(this).attr("valorvale").replace(",", "."));
            data.push($(this).attr("id"));
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
            if ($(this).attr("idpessoal") == idpessoal) {
                estado_switchmini += $(this).attr("idvales") + "-";
            }
        }
    });
    return estado_switchmini;
}