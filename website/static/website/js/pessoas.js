$(document).ready(function() {
    $(".button-demissao").hide();
});


$(document).on('click', ".js-seleciona-colaborador", function() {
    var id_pessoal = $(this).data("idpessoal");
    $.ajax({
        type: "GET",
        url: "/pessoas/consulta_pessoa",
        data: {
            id_pessoal: id_pessoal,
        },
        beforeSend: function() {
            $(".card-foto-colaborador").hide()
            $(".card-info-colaborador").hide()
            $(".card-dados-colaborador").hide()
            $(".card-ferias-colaborador").hide()
            $(".card-multas-colaborador").hide()
            $(".card-decimo-terceiro").hide()
            $(".card-form-colaborador").hide()
            $(".card-recibos-colaborador").hide()
            $(".card-verbas-rescisoria").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-foto-colaborador").html(data.html_card_foto_colaborador)
            $(".card-info-colaborador").html(data.html_card_info_colaborador)
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-foto-colaborador").show()
            $(".card-info-colaborador").show()
            $(".card-dados-colaborador").show()
            var url = $(".foto").attr("src");
            // Força o recarregamento da foto sem utilizar o cache
            $(".foto").attr("src", url + `?v=${new Date().getTime()}`);
            $(".card-ferias-colaborador").html(data.html_ferias_colaborador)
            $(".card-decimo-terceiro").html(data.html_decimo_terceiro)
            $(".card-recibos-colaborador").html(data.html_recibos_colaborador)
            if (data.tipo_pgto == "MENSALISTA") {
                $(".button-demissao").show()
                $(".card-decimo-terceiro").show()
                $(".card-ferias-colaborador").show()
            } else {
                $(".card-recibos-colaborador").show()
                $(".button-demissao").hide()
            }
            $(".card-multas-colaborador").html(data.html_multas_colaborador)
            $(".js-mostra-dados-multa").hide()
            $(".card-multas-colaborador").show()
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
            var url = $(".foto").attr("src");
            // Força o recarregamento da foto sem utilizar o cache
            $(".foto").attr("src", url + `?v=${new Date().getTime()}`);
            $('.box-loader').hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        },
    });
});

$(document).on('change', '.js-carrega-foto', function() {
    $(".js-salva-foto").click()
});

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

$(document).on('click', '.js-demissao', function() {
    var idpessoal = $("#idpessoal").val();
    $.ajax({
        type: "GET",
        url: "/pessoas/demissao_colaborador",
        data: {
            idpessoal: idpessoal,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_demissao_colaborador)
            $(".card-form-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('click', '.js-periodo-ferias', function() {
    var idpessoal = $("#idpessoal").val();
    var idaquisitivo = $(this).data("idaquisitivo");
    $.ajax({
        type: "GET",
        url: "/pessoas/periodo_ferias",
        data: {
            idpessoal: idpessoal,
            idaquisitivo: idaquisitivo,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_periodo_ferias)
            $(".card-form-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('click', '.js-adiciona-documento-colaborador', function() {
    var idpessoal = $(this).data('idpessoal')
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

$(document).on('click', '.js-altera-documento-colaborador', function() {
    var iddocpessoal = $(this).data('iddocpessoal')
    var idpessoal = $(this).data('idpessoal')
    $.ajax({
        type: "GET",
        url: "/pessoas/altera_documento_colaborador",
        data: {
            iddocpessoal: iddocpessoal,
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

$(document).on('click', '.js-exclui-documento-colaborador', function() {
    var iddocpessoal = $(this).data('iddocpessoal')
    $.ajax({
        type: "GET",
        url: "/pessoas/exclui_documento_colaborador",
        data: {
            iddocpessoal: iddocpessoal,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_confirma_exclusao)
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
            var url = $(".foto").attr("src");
            // Força o recarregamento da foto sem utilizar o cache
            $(".foto").attr("src", url + `?v=${new Date().getTime()}`);
            if (data.html_form_documento_colaborador) {
                $('.card-form-colaborador').html(data.html_form_documento_colaborador)
                $('.card-form-colaborador').show()
            }
            $('.box-loader').hide()
        },
    });
});

$(document).on('submit', '.js-gera-demissao', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: "/pessoas/salva_demissao_colaborador",
        data: $(this).serialize(),
        beforeSend: function() {
            $('.card-dados-colaborador').hide()
            $('.card-form-colaborador').hide()
            $('.box-loader').show()
        },
        success: function(data) {
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            var url = $(".foto").attr("src");
            // Força o recarregamento da foto sem utilizar o cache
            $(".foto").attr("src", url + `?v=${new Date().getTime()}`);
            if (data.html_form_demissao_colaborador) {
                $('.card-form-colaborador').html(data.html_form_demissao_colaborador)
                $('.card-form-colaborador').show()
            }
            $('.box-loader').hide()
        },
    });
});

$(document).on('submit', '.js-gera-periodo-ferias', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: "/pessoas/salva_periodo_ferias",
        data: $(this).serialize(),
        beforeSend: function() {
            $('.card-form-colaborador').hide()
            $('.card-ferias-colaborador').hide()
            $('.box-loader').show()
        },
        success: function(data) {
            $(".card-dados-colaborador").show()
            $(".card-ferias-colaborador").html(data.html_ferias_colaborador)
            $('.card-ferias-colaborador').show()
            if (data.html_form_periodo_ferias) {
                $('.card-form-colaborador').html(data.html_form_periodo_ferias)
                $('.card-form-colaborador').show()
            }
            $('.box-loader').hide()
        },
    });
});

$(document).on('submit', '.js-apaga-documento', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: "/pessoas/apaga_documento_colaborador",
        data: $(this).serialize(),
        beforeSend: function() {
            $('.card-dados-colaborador').hide()
            $('.card-form-colaborador').hide()
            $('.box-loader').show()
        },
        success: function(data) {
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            var url = $(".foto").attr("src");
            // Força o recarregamento da foto sem utilizar o cache
            $(".foto").attr("src", url + `?v=${new Date().getTime()}`);
            $('.box-loader').hide()
        },
    });
});

$(document).on('click', '.js-adiciona-telefone-colaborador', function() {
    var idpessoal = $(this).data('idpessoal')
    $.ajax({
        type: "GET",
        url: "/pessoas/adiciona_telefone_colaborador",
        data: {
            idpessoal: idpessoal,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_fone_colaborador)
            $(".card-form-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('click', '.js-altera-telefone-colaborador', function() {
    var idfonepessoal = $(this).data('idfonepessoal')
    var idpessoal = $(this).data('idpessoal')
    $.ajax({
        type: "GET",
        url: "/pessoas/altera_telefone_colaborador",
        data: {
            idfonepessoal: idfonepessoal,
            idpessoal: idpessoal,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_fone_colaborador)
            $(".card-form-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('click', '.js-verbas-rescisoria', function() {
    var idpessoal = $(this).data('idpessoal')
    $.ajax({
        type: "GET",
        url: "/pessoas/verba_rescisoria",
        data: {
            idpessoal: idpessoal,
        },
        beforeSend: function() {
            $(".card-ferias-colaborador").hide()
            $(".card-multas-colaborador").hide()
            $(".card-decimo-terceiro").hide()
            $(".card-verbas-rescisoria").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-verbas-rescisoria").html(data.html_verbas_rescisoria)
            $(".card-verbas-rescisoria").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});


$(document).on('click', '.js-exclui-telefone-colaborador', function() {
    var idfonepessoal = $(this).data('idfonepessoal')
    $.ajax({
        type: "GET",
        url: "/pessoas/exclui_telefone_colaborador",
        data: {
            idfonepessoal: idfonepessoal,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_confirma_exclusao)
            $(".card-form-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('click', '.js-confirma-exclusao-periodo-ferias', function() {
    var idferias = $(this).data('idferias')
    $.ajax({
        type: "GET",
        url: "/pessoas/confirma_exclusao_periodo_ferias",
        data: {
            idferias: idferias,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_confirma_exclusao)
            $(".card-form-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('submit', '.js-gera-telefone', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: "/pessoas/salva_telefone_colaborador",
        data: $(this).serialize(),
        beforeSend: function() {
            $('.card-dados-colaborador').hide()
            $('.card-form-colaborador').hide()
            $('.box-loader').show()
        },
        success: function(data) {
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            var url = $(".foto").attr("src");
            // Força o recarregamento da foto sem utilizar o cache
            $(".foto").attr("src", url + `?v=${new Date().getTime()}`);
            if (data.html_form_fone_colaborador) {
                $('.card-form-colaborador').html(data.html_form_fone_colaborador)
                $('.card-form-colaborador').show()
            }
            $('.box-loader').hide()
        },
    });
});

$(document).on('submit', '.js-apaga-telefone', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: "/pessoas/apaga_telefone_colaborador",
        data: $(this).serialize(),
        beforeSend: function() {
            $('.card-dados-colaborador').hide()
            $('.card-form-colaborador').hide()
            $('.box-loader').show()
        },
        success: function(data) {
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            var url = $(".foto").attr("src");
            // Força o recarregamento da foto sem utilizar o cache
            $(".foto").attr("src", url + `?v=${new Date().getTime()}`);
            $('.box-loader').hide()
        },
    });
});

$(document).on('submit', '.js-exclui-periodo-ferias', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: "/pessoas/exclui_periodo_ferias",
        data: $(this).serialize(),
        beforeSend: function() {
            $('.card-ferias-colaborador').hide()
            $('.card-form-colaborador').hide()
            $('.box-loader').show()
        },
        success: function(data) {
            $(".card-ferias-colaborador").html(data.html_ferias_colaborador)
            $(".card-ferias-colaborador").show()
            var url = $(".foto").attr("src");
            // Força o recarregamento da foto sem utilizar o cache
            $(".foto").attr("src", url + `?v=${new Date().getTime()}`);
            $('.box-loader').hide()
        },
    });
});

$(document).on('click', '.js-adiciona-conta-colaborador', function() {
    var idpessoal = $(this).data('idpessoal')
    $.ajax({
        type: "GET",
        url: "/pessoas/adiciona_conta_colaborador",
        data: {
            idpessoal: idpessoal,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_conta_colaborador)
            $(".card-form-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('click', '.js-altera-conta-colaborador', function() {
    var idcontapessoal = $(this).data('idcontapessoal')
    var idpessoal = $(this).data('idpessoal')
    $.ajax({
        type: "GET",
        url: "/pessoas/altera_conta_colaborador",
        data: {
            idcontapessoal: idcontapessoal,
            idpessoal: idpessoal,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_conta_colaborador)
            $(".card-form-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('click', '.js-exclui-conta-colaborador', function() {
    var idcontapessoal = $(this).data('idcontapessoal')
    $.ajax({
        type: "GET",
        url: "/pessoas/exclui_conta_colaborador",
        data: {
            idcontapessoal: idcontapessoal,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_confirma_exclusao)
            $(".card-form-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});

$(document).on('submit', '.js-gera-conta', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: "/pessoas/salva_conta_colaborador",
        data: $(this).serialize(),
        beforeSend: function() {
            $('.card-dados-colaborador').hide()
            $('.card-form-colaborador').hide()
            $('.box-loader').show()
        },
        success: function(data) {
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            var url = $(".foto").attr("src");
            // Força o recarregamento da foto sem utilizar o cache
            $(".foto").attr("src", url + `?v=${new Date().getTime()}`);
            if (data.html_form_conta_colaborador) {
                $('.card-form-colaborador').html(data.html_form_conta_colaborador)
                $('.card-form-colaborador').show()
            }
            $('.box-loader').hide()
        },
    });
});

$(document).on('submit', '.js-apaga-conta', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: "/pessoas/apaga_conta_colaborador",
        data: $(this).serialize(),
        beforeSend: function() {
            $('.card-dados-colaborador').hide()
            $('.card-form-colaborador').hide()
            $('.box-loader').show()
        },
        success: function(data) {
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            var url = $(".foto").attr("src");
            // Força o recarregamento da foto sem utilizar o cache
            $(".foto").attr("src", url + `?v=${new Date().getTime()}`);
            $('.box-loader').hide()
        },
    });
});

$(document).on('click', '.js-altera-salario-colaborador', function() {
    var idsalario = $(this).data('idsalario')
    var idpessoal = $(this).data('idpessoal')
    $.ajax({
        type: "GET",
        url: "/pessoas/altera_salario_colaborador",
        data: {
            idsalario: idsalario,
            idpessoal: idpessoal,
        },
        beforeSend: function() {
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_salario_colaborador)
            $(".card-form-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});


$(document).on('submit', '.js-salva-salario', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: "/pessoas/salva_salario_colaborador",
        data: $(this).serialize(),
        beforeSend: function() {
            $('.card-dados-colaborador').hide()
            $('.card-form-colaborador').hide()
            $('.box-loader').show()
        },
        success: function(data) {
            console.log(data)
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            var url = $(".foto").attr("src");
            // Força o recarregamento da foto sem utilizar o cache
            $(".foto").attr("src", url + `?v=${new Date().getTime()}`);
            if (data.html_form_salario_colaborador) {
                $('.card-form-colaborador').html(data.html_form_salario_colaborador)
                $('.card-form-colaborador').show()
            }
            $('.box-loader').hide()
        },
    });
});

$(document).on('click', '.js-fecha-formulario', function() {
    $('.card-form-colaborador').hide();
});

$(document).on('click', '.js-form-paga-decimo-terceiro', function() {
    var idparcela = $(this).data("idparcela");
    var idpessoal = $(this).data("idpessoal");
    $.ajax({
        type: "GET",
        url: "/pessoas/form_paga_decimo_terceiro",
        data: {
            idparcela: idparcela,
            idpessoal: idpessoal,
        },
        beforeSend: function() {
            $('.box-loader').show();
        },
        success: function(data) {
            $(".card-form-colaborador").html(data.html_form_paga_decimo_terceiro)
            $(".card-form-colaborador").show()
            $('.box-loader').hide()
        },
        error: function(errorThrown) {
            console.log(errorThrown);
        },
    });
});

$(document).on('submit', '.js-paga-decimo-terceiro', function(event) {
    event.preventDefault();
    $.ajax({
        type: $(this).attr('method'),
        url: "/pessoas/paga_decimo_terceiro",
        data: $(this).serialize(),
        beforeSend: function() {
            $('.card-form-colaborador').hide()
            $(".card-decimo-terceiro").hide()
            $('.box-loader').show()
        },
        success: function(data) {
            console.log(data)
            $(".card-decimo-terceiro").html(data.html_decimo_terceiro)
            $(".card-decimo-terceiro").show()
            $('.box-loader').hide()
        },
    });
});

$(document).on('click', '.js-altera-status-colaborador', function() {
    var idpessoal = $("#idpessoal").val()
    var lista = $(this).data("lista")
    $.ajax({
        type: "GET",
        url: "/pessoas/altera_status_colaborador",
        data: {
            idpessoal: idpessoal,
            lista: lista,
        },
        beforeSend: function() {
            $(".box-loader").show()
            $(".card-lista-colaboradores").hide()
            $(".card-foto-colaborador").hide()
        },
        success: function(data) {
            $(".card-lista-colaboradores").html(data.html_lista_colaboradores_ativo)
            $(".card-foto-colaborador").html(data.html_card_foto_colaborador)
            $(".card-lista-colaboradores").show()
            $(".card-foto-colaborador").show()
            $(".box-loader").hide()
        },
    });
});

$(document).on('click', '.js-altera-lista', function() {
    var lista = $(this).data("lista")
    $.ajax({
        type: "GET",
        url: "/pessoas/altera_lista",
        data: {
            lista: lista,
        },
        beforeSend: function() {
            $(".box-loader").show()
            $(".card-lista-colaboradores").hide()
            $(".card-dados-colaborador").hide()
        },
        success: function(data) {
            $(".card-lista-colaboradores").html(data.html_lista_colaboradores_ativo)
            $(".card-lista-colaboradores").show()
            $(".box-loader").hide()
        },
    });
});


$(document).on("input", '#causa', function() {
    $("#print-rescisao-trabalho").prop('href', function() {
        var href = $("#print-rescisao-trabalho").prop('href');
        var url = new URL(href);
        url.searchParams.set('causa', $("#causa").val());
        $("#print-rescisao-trabalho").attr("href", url.toString());
    });
});

$(document).on('click', '.js-toggle-multas', function() {
    $(".js-mostra-dados-multa").slideToggle(500)
    $(".js-toggle-multas").toggleClass("icofont-square-up");
});
