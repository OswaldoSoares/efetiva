let idContraCheque = null;
let idPessoal = null;

var ocultarCardsColaborador =  function() {
    $(".card-foto-colaborador").hide();
    $(".card-eventos-rescisorios-colaborador").hide();
    $(".card-vales-colaborador").hide();
    $(".card-contra-cheque-colaborador").hide();
    $(".card-decimo-terceiro-colaborador").hide();
    $(".card-docs-colaborador").hide();
    $(".card-fones-colaborador").hide();
    $(".card-contas-colaborador").hide();
};

$(document).ready(function() {
    $(".button-demissao").hide();
    ocultarCardsColaborador();
});

$(document).on("click", ".js-alterar-categoria", function() {
    const selecionado = $(this)
    const tipo = $(this).data("tipo")

    // Alterando variável global
    idPessoal = null;
    idContraCheque = null;

    $(".js-alterar-categoria").each(function() {
        $(this).removeClass("icofont-checked");
        $(this).removeClass("disabled");
        $(this).addClass("icofont-square");
    });

    executarAjax("/pessoas/selecionar_categoria", "GET", {
        tipo: tipo,
    }, function(data) {
        ocultarCardsColaborador();
        $(".card-colaboradores").html(data["html-card-colaboradores"])
        $(".box-loader").hide()
    });

    $(selecionado).removeClass("icofont-square")
    $(selecionado).addClass("icofont-checked")
    $(selecionado).addClass("disabled")
});

$(document).on('click', ".js-selecionar-colaborador", function() {
    const selecionado = $(this)

    // Alterando variáveis global
    idPessoal = $(this).data("id_pessoal");
    idContraCheque = null;

    $(".js-selecionar-colaborador").each(function() {
        $(this).removeClass("icofont-checked");
        $(this).removeClass("disabled");
        $(this).addClass("icofont-square");
    });

    executarAjax("/pessoas/consultar_colaborador", "GET", {
        id_pessoal: idPessoal,
    }, function(data) {
        $(".card-foto-colaborador").html(data["html-card-foto-colaborador"]);
        $(".card-foto-colaborador").show();
        $(".card-contra-cheque-colaborador").hide();
        $(".js-fechar-card-contra-cheque").click();
        $(".sub-grid").css("padding-top", "0");
        $(".card-vales-colaborador").html(data["html-card-vales-colaborador"]);
        $(".card-vales-colaborador").show();
        $(".card-decimo-terceiro-colaborador").html(
            data["html-card-decimo-terceiro-colaborador"]
        );
        $(".parcelas-13").hide();
        $(".card-decimo-terceiro-colaborador").show();
        $(".card-docs-colaborador").html(data["html-card-docs-colaborador"]);
        $(".card-docs-colaborador").show();
        $(".card-fones-colaborador").html(data["html-card-fones-colaborador"]);
        $(".card-fones-colaborador").show();
        $(".card-contas-colaborador").html(data["html-card-contas-colaborador"]);
        $(".card-contas-colaborador").show();
        var url = $(".foto").attr("src");
        // Força o recarregamento da foto sem utilizar o cache
        $(".foto").attr("src", url + `?v=${new Date().getTime()}`);

        $(".card-info-colaborador").html(data.html_card_info_colaborador)
        $(".card-dados-colaborador").html(data.html_dados_colaborador)
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
        $(".card-vales-colaborador").html(data.html_vales_colaborador)
        if (data.categoria == "MOTORISTA") {
            $(".card-multas-colaborador").html(data.html_multas_colaborador)
            $(".card-multas-colaborador").show()
            $(".js-mostra-dados-multa").hide()
        }
        $(".js-mostra-vales").show()
        $(".js-mostra-ferias").hide()
        $(".js-mostra-decimo-terceiro").hide()
        $(".card-vales-colaborador").show()
        valesSelecionaveis()
        $(window).scrollTop(0)
        $(".box-loader").hide()
    });

    $(selecionado).removeClass("icofont-square")
    $(selecionado).addClass("icofont-checked")
    $(selecionado).addClass("disabled")
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


$(document).on("click", ".js-mostrar-eventos-rescisorios", function() {
    executarAjax("/pessoas/mostrar_eventos_rescisorios_colaborador", "GET", {
        id_pessoal: idPessoal,
    }, function(data) {
        $(".card-eventos-rescisorios-colaborador").html(data["html-card-eventos-rescisorios-colaborador"]);
        $(".card-eventos-rescisorios-colaborador").show();
        $(".box-loader").hide();
    });
});

$(document).on("click", ".js-selecionar-evento-rescisorio", function() {
    const eventoId = "#" + $(this).data("evento")
    const currentValue = $(eventoId).val() === "true";
    const newValue = !currentValue

    $(eventoId).val(newValue.toString());

    $(this).toggleClass("icofont-checked")
    $(this).toggleClass("icofont-square")
});

$(document).on("click", "js-calcular-verba_rescisorias", function() {
    executarAjax("/pessoas/calcular_verbas_rescisorias", "GET", {
        id_pessoal: idPessoal,
    }, function(data) {
        console.log(data)
        $(".card-eventos-rescisorios-colaborador").html(data["html-card-eventos-rescisorios-colaborador"]);
        $(".card-eventos-rescisorios-colaborador").show();
        $(".box-loader").hide();
    });
});

$(document).on("click", ".js-selecionar-decimo-terceiro", function() {
    const id = $(this).attr("id");

    $(".js-selecionar-decimo-terceiro").each(function() {
        $(this).removeClass("icofont-checked");
        $(this).removeClass("disabled");
        $(this).addClass("icofont-square");
    });

    $(this).addClass("icofont-checked");
    $(this).addClass("disabled")
    $(this).removeClass("icofont-square");

    $(".parcelas-13").each(function() {
        $(this).hide();
    });

    $("." + id).toggle();
});

$(document).on("click", ".js-selecionar-parcela", function ()  {
    const ano = $(this).data("ano");
    const mes = $(this).data("mes");
    const dozeavos = $(this).data("dozeavos");
    const valor = $(this).data("valor");

    executarAjax("/pessoas/selecionar_contra_cheque_decimo_terceiro", "GET", {
        ano: ano,
        mes: mes,
        dozeavos: dozeavos,
        valor: valor,
        //  Variável global
        id_pessoal: idPessoal,
    }, function(data) {
        $(".card-contra-cheque-colaborador").html(
            data["html-card-contra-cheque-colaborador"]
        )
        $(".card-contra-cheque-colaborador").show()
        idContraCheque = $("#id_contra_cheque").data("id_contra_cheque")
        selecionarValesToggle()
        $(window).scrollTop(0)
        $(".box-loader").hide()
    });
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

// $(document).on('click', '.js-adicionar-demissao', function() {
    // var idpessoal = $("#idpessoal").val();

    // executarAjax("/pessoas/demissao_colaborador", "GET", {
        // idpessoal: idpessoal,
    // }, function(data) {
            // $(".card-form-colaborador").html(data.html_form_demissao_colaborador)
            // $(".card-form-colaborador").show()
            // $(".box-loader").hide()
    // });
// });

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
    $(".js-toggle-multas").toggleClass("icofont-square-down");
});

$(document).on('click', '.js-toggle-vales', function() {
    $(".js-mostra-vales").slideToggle(500)
    $(".js-toggle-vales").toggleClass("icofont-square-up");
    $(".js-toggle-vales").toggleClass("icofont-square-down");
});

$(document).on('click', '.js-toggle-ferias', function() {
    $(".js-mostra-ferias").slideToggle(500)
    $(".js-toggle-ferias").toggleClass("icofont-square-up");
    $(".js-toggle-ferias").toggleClass("icofont-square-down");
});

$(document).on('click', '.js-toggle-decimo-terceiro', function() {
    $(".js-mostra-decimo-terceiro").slideToggle(500)
    $(".js-toggle-decimo-terceiro").toggleClass("icofont-square-up");
    $(".js-toggle-decimo-terceiro").toggleClass("icofont-square-down");
});

$(document).on('click', '.js-seleciona-aquisitivo', function() {
    var idpessoal = $(this).data("idpessoal")
    var idaquisitivo = $(this).data("idaquisitivo")
    var descricao = $(this).data("descricao")
    $.ajax({
        type: "GET",
        url: "/pessoas/seleciona_aquisitivo",
        data: {
            idpessoal: idpessoal,
            idaquisitivo: idaquisitivo,
            descricao:  descricao,
        },
        beforeSend: function() {
            $(".box-loader").show()
            $(".card-contra-cheque-colaborador").hide()
            localStorage.setItem("idcontracheque", "")
        },
        success: function(data) {
            $(".card-contra-cheque-colaborador").html(data.html_card_contra_cheque_colaborador)
            $(".card-contra-cheque-colaborador").show()
            localStorage.setItem("idcontracheque", $("#idcontracheque").data("idcontracheque"))
            localStorage.setItem("mes_ano", data["mes_ano"])
            valesSelecionaveis()
            $(".box-loader").hide()
        },
    });
});

$(document).on('click', '.js-seleciona-parcela', function() {
    var idpessoal = $(this).data("idpessoal")
    var idparcela = $(this).data("idparcela")
    var descricao = $(this).data("descricao")
    $.ajax({
        type: "GET",
        url: "/pessoas/seleciona_parcela",
        data: {
            idpessoal: idpessoal,
            idparcela: idparcela,
            descricao:  descricao,
        },
        beforeSend: function() {
            $(".box-loader").show()
            $(".card-contra-cheque-colaborador").hide()
            $(".card-decimo-terceiro").hide()
            localStorage.setItem("idcontracheque", "")
        },
        success: function(data) {
            $(".card-contra-cheque-colaborador").html(data.html_card_contra_cheque_colaborador)
            $(".card-contra-cheque-colaborador").show()
            $(".card-decimo-terceiro").html(data.html_decimo_terceiro)
            $(".card-decimo-terceiro").show()
            $("#submit-contracheque").hide()
            localStorage.setItem("idcontracheque", $("#idcontracheque").data("idcontracheque"))
            localStorage.setItem("mes_ano", data["mes_ano"])
            valesSelecionaveis()
            $(".box-loader").hide()
        },
    });
});

var valesSelecionaveis = function() {
    $(".js-pessoas-toggle-vales-selecionaveis").toggleClass("i-button");
    $(".js-pessoas-toggle-vales-selecionaveis").toggleClass("i-button-null");       
    $(".js-pessoas-toggle-vales-selecionaveis").toggleClass("js-pessoas-seleciona-vale");       
}

$(document).on('click', '.js-pessoas-exclui-contra-cheque-item', function () {
    var id_pessoal = localStorage.getItem("id_pessoal")
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
            $(".card-contra-chqeue-colaborador").hide()
            $(".card-vales-colaborador").hide()
        },
        success: function(data) {
            $(".card-contra-cheque-colaborador").html(data.html_card_contra_cheque_colaborador)
            $(".card-vales-colaborador").html(data.html_vales_colaborador)
            $(".card-contra-cheque-colaborador").show()
            $(".card-vales-colaborador").show()
            $(".box-loader").hide()
        },
    });
});
