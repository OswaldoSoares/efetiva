$(document).ready(function(){
    window.MesReferencia = '';
    window.AnoReferencia = '';
    window.idpessoal = '';
    $(".down-folha").hide();
    $(".down-avulso").hide();
    $('[data-toggle="tooltip"]').tooltip();
});

$(document).on('change', '#id_MesReferencia', function(event) {
    $(".fp-base").html("");
    $(".fp-contrachequeitens").html("");
    $(".fp-adiantamento").html("");
    $(".fp-adiantamento").hide();
});

$(document).on('change', '#id_AnoReferencia', function(event) {
    $(".fp-base").html("");
    $(".fp-contrachequeitens").html("");
    $(".fp-adiantamento").html("");
    $(".fp-adiantamento").hide();
});

$(document).on('click', '.js-seleciona-mes-ano', function(event) {
    v_mes_ano = $('.select-mes-ano option:selected').text()
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: '/pagamentos/seleciona_mes_ano',
        data: {
            mes_ano: v_mes_ano,
        },
        beforeSend: function(){
            $('.js-folha').fadeOut(500)
        },
        success: function(data){
            $('.js-folha').html(data.html_folha)
            $('.js-folha').fadeIn(500)
        },
    });
});

$(document).on('click', '.js-dados', function(event) {
    v_dados = $(this).data('dados')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: '/pagamentos/dados',
        data: {
            dados: v_dados,
        },
        beforeSend: function(){
            $('.js-cartao-ponto').fadeOut(500)
        },
        success: function(data){
            $('.js-cartao-ponto').html(data.html_cartao_ponto)
            $('.js-cartao-ponto').fadeIn(500)
        },
    });
});

$(document).on('change', '.switchmini', function(event) {
    var idpessoalconcatenado = '#vale_' + $(this).attr('idpessoal')
    if ($(this).attr('tipopgto') == 'mensalista'){
        if ($(this).is(":checked")) {
            var url = 'criacontrachequeitensvale'
        } else {
            var url = 'excluicontrachequeitensvale'
        }
        var idpessoal = $(this).attr('idpessoal')
        var idvales = $(this).attr('idvales')
        var idcontracheque = $(this).attr('idcontracheque')
        var mesreferencia = window.MesReferencia
        var anoreferencia = window.AnoReferencia
        var estado_switchmini = estadoswitchmini(idpessoal)
        $.ajax({
            type: 'GET',
            dateType:'json',
            url: url,
            data:{
                idPessoal: idpessoal,
                idVales: idvales,
                idContraCheque: idcontracheque,
                MesReferencia: mesreferencia,
                AnoReferencia: anoreferencia,
                EstadoSwitchMini: estado_switchmini,
            },
            success: function(data){
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
            }
        })
    }
    valeselect(idpessoalconcatenado);
    somavales();
});

$(document).on('submit', '#form-seleciona-folha', function(event) {
    event.preventDefault();
    var url = $(this).attr('action') || action;
    window.MesReferencia = $('#id_MesReferencia').val();
    window.AnoReferencia = $('#id_AnoReferencia').val();
    $.ajax({
        type: $(this).attr('method'),
        url: url,
        data: $(this).serialize(),
        success: function(data){
            $(".fp-base").html(data.html_folha);
            $(".fp-contrachequeitens").html("");
            $(".fp-adiantamento").hide();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('submit', '.form-cria-contrachequeitens', function(event) {
    event.preventDefault();
    var url = $(this).attr('action') || action;
    $.ajax({
        type: $(this).attr('method'),
        url: url,
        data: $(this).serialize(),
        success: function(data){
            $(".fp-base").html(data.html_folha)
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
            console.log(error)
        }
    });
});

$(document).on('submit', '#form-seleciona-periodo', function(event) {
    event.preventDefault();
    var url = $(this).attr('action') || action;
    $.ajax({
        type: $(this).attr('method'),
        url: url,
        data: $(this).serialize(),
        beforeSend: function(){
            
        },
        success: function(data){
          /*  $(".pa-saldo").html("");*/
            $(".pa-saldo-minutas").html(data.html_saldoavulso);
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('submit', '#form-vale', function(event) {
    event.preventDefault();
    var url = $(this).attr('action') || action;
    $.ajax({
        type: $(this).attr('method'),
        url: url,
        data: $(this).serialize(),
        success: function(data){
            if (data.html_vales) {
                $(".fp-vales").html(data.html_vales);
            }
            if (data.html_valesavulso) {
                $(".pa-vales").html(data.html_valesavulso);
            }
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('click', '.selecionar-contracheque', function(event) {
    var url = $(this).attr('data-url')
    var mesreferencia = window.MesReferencia
    var anoreferencia = window.AnoReferencia
    var idpessoal = $(this).attr('idpessoal')
    window.idPessoal = $(this).attr('idpessoal')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        },
        success: function(data){
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
            console.log(error)
        }
    });
});

$(document).on('click', '.remove-item', function(event) {
    var url = $(this).attr('data-url')
    var idcontracheque = $(this).attr('idcontracheque')
    var descricao = $(this).attr('descricao')
    var registro = $(this).attr('registro')
    var mesreferencia = window.MesReferencia
    var anoreferencia = window.AnoReferencia
    var idpessoal = $(this).attr('idpessoal')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            idContraCheque: idcontracheque,
            Descricao: descricao,
            Registro: registro,
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        },
        success: function(data){
            $(".fp-base").html(data.html_folha)
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
            console.log(error)
        }
    });
});

$(document).on('click', '.remove-vale', function(event) {
    var url = $(this).attr('data-url')
    var idvales = $(this).attr('idvales')
    var mesreferencia = window.MesReferencias
    var anoreferencia = window.AnoReferencia
    var idpessoal = window.idPessoal

    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            idVales: idvales,
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        },
        success: function(data){
            $(".fp-base").html(data.html_folha)
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
            console.log(error)
        }
    });
});

$(document).on('click', '.estorna-recibo', function(event) {
    var url = $(this).attr('data-url')
    var idrecibo = $(this).attr('idrecibo')
    var mesreferencia = window.MesReferencias
    var anoreferencia = window.AnoReferencia
    var idpessoal = window.idPessoal

    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            idRecibo: idrecibo,
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        },
        success: function(data){
            $(".pa-saldo-minutas").html(data.html_saldoavulso);
            $(".pa-minutas").html(data.html_minutas);
            $(".pa-vales").html(data.html_valesavulso);
            $(".pa-recibos").html(data.html_recibos);
            valeselect('#vale_' + idpessoal);
            somavales();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('click', '#gerar-folha', function(event) {
    var url = $(this).attr('data-url')
    var mesreferencia = $(this).attr('mesreferencia')
    var anoreferencia = $(this).attr('anoreferencia')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
        },
        beforeSend: function(){
            $(".fp-base").html("");
            $(".fp-adiantamento").hide();
        },
        success: function(data){
            $(".fp-base").html(data.html_folha);
            $(".fp-adiantamento").hide();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('click', '#gerar-pagamento', function(event) {
    var url = $(this).attr('data-url')
    var idpessoal = $(this).attr('idpessoal')
    var datainicial = $(this).attr('datainicial')
    var datafinal = $(this).attr('datafinal')
    var valesselecionados = valeselect('#vale_' + $(this).attr('idpessoal'))
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            idPessoal: idpessoal,
            DataInicial: datainicial,
            DataFinal: datafinal,
            ValesSelecionados: valesselecionados,
        },
        success: function(data){
            $(".pa-saldo-minutas").html(data.html_saldoavulso);
            $(".pa-minutas").html(data.html_minutas);
            $(".pa-vales").html(data.html_valesavulso);
            $(".pa-recibos").html(data.html_recibos);
            valeselect('#vale_' + idpessoal);
            somavales();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('click', '.altera-falta', function(event) {
    var url = $(this).attr('data-url')
    var mesreferencia = $(this).attr('mesreferencia')
    var anoreferencia = $(this).attr('anoreferencia')
    var idpessoal = $(this).attr('idpessoal')
    var idcartaoponto = $(this).attr('idcartaoponto')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
            idCartaoPonto: idcartaoponto,
        },
        success: function(data){
            $(".fp-base").html(data.html_folha)
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
            console.log(error)
        }
    });
});

$(document).on('click', '.selecionar-saldoavulso', function(event) {
    var url = $(this).attr('data-url')
    var datainicial = $(this).attr('datainicial')
    var datafinal = $(this).attr('datafinal')
    var idpessoal = $(this).attr('idpessoal')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            DataInicial: datainicial,
            DataFinal: datafinal,
            idPessoal: idpessoal,
        },
        success: function(data){
            $(".pa-minutas").html(data.html_minutas);
            $(".pa-vales").html(data.html_valesavulso);
            $(".pa-recibos").html(data.html_recibos);
            valeselect('#vale_' + idpessoal);
            somavales();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(".div-fade-folha").click(function(){  
    if ($("#fp-main").is(':hidden')) {
        $("#fp-main").slideDown("fast");
        $(".up-folha").show()
        $(".down-folha").hide()
    } else {
        $(".up-folha").hide()
        $(".down-folha").show()
        $("#fp-main").slideUp("fast");
    }
});

$(".div-fade-avulso").click(function(){  
    if ($("#pa-main").is(':hidden')) {
        $("#pa-main").slideDown("fast");
        $(".up-avulso").show()
        $(".down-avulso").hide()
    } else {
        $(".up-avulso").hide()
        $(".down-avulso").show()
        $("#pa-main").slideUp("fast");
    }
});

function openMyModal(event) {
    var modal = initModalDialog(event, '#MyModal');
    var url = $(event.target).data('action');
    var idcartaoponto = $(event.target).data('idcartaoponto');
    var mesreferencia = $(event.target).data('mesreferencia');
    var anoreferencia = $(event.target).data('anoreferencia');
    var idpessoal = $(event.target).data('idpessoal');
    $.ajax({
        type: "GET",
        url: url,
        data : {
            idCartaoPonto: idcartaoponto,
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        }
    }).done(function(data, textStatus, jqXHR) {
        modal.find('.modal-body').html(data.html_form);
        modal.modal('show');
        formAjaxSubmit(modal, url, null, null);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        alert("SERVER ERROR: " + errorThrown);
    });
}

function initModalDialog(event, modal_element) {
    var modal = $(modal_element);
    var target = $(event.target);
    var title = target.data('title') || '';
    var subtitle = target.data('subtitle') || '';
    var dialog_class = (target.data('dialog-class') || '') + ' modal-dialog';
    var icon_class = (target.data('icon') || 'fa-laptop') + ' fa modal-icon';
    var button_save_label = target.data('button-save-label') || 'Save changes';
    modal.find('.modal-dialog').attr('class', dialog_class);
    modal.find('.modal-title').text(title);
    modal.find('.modal-subtitle').text(subtitle);
    modal.find('.modal-header .title-wrapper i').attr('class', icon_class);
    modal.find('.modal-footer .btn-save').text(button_save_label);
    modal.find('.modal-body').html('');
    modal.data('target', target);
    return modal;
}

function formAjaxSubmit(modal, action, cbAfterLoad, cbAfterSuccess) {
    var form = modal.find('.modal-body form');
    var header = $(modal).find('.modal-header');
    var btn_save = modal.find('.modal-footer .btn-save');
    if (btn_save) {
        modal.find('.modal-body form .form-submit-row').hide();
        btn_save.off().on('click', function(event) {
            modal.find('.modal-body form').submit();
        });
    }
    if (cbAfterLoad) { cbAfterLoad(modal); }
    modal.find('form input:visible').first().focus();
    $(form).on('submit', function(event) {
        event.preventDefault();
        header.addClass('loading');
        var url = $(this).attr('action') || action;
        $.ajax({
            type: $(this).attr('method'),
            url: url,
            idobj: $(this).attr('idobj'),
            data: $(this).serialize(),
            success: function(xhr, ajaxOptions, thrownError) {
                $(modal).find('.modal-body').html(xhr['html_form']);
                if ($(xhr['html_form']).find('.errorlist').length > 0) {
                    formAjaxSubmit(modal, url, cbAfterLoad, cbAfterSuccess);
                } else {
                    $(modal).modal('hide');
                    $(".fp-base").html(xhr.html_folha)
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
                    if (cbAfterSuccess) { cbAfterSuccess(modal); }
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                console.log('SERVER ERROR: ' + thrownError);
            },
            complete: function() {
                header.removeClass('loading');
            }
        });
    });
}

function valeselect(idpessoal) {
    var data = [];
    var total = 0.00
    $('.switchmini').each(function() {
        if ($(this).is(":checked") && $(this).attr('idPessoal') == idpessoal.substring(6)) {
            total += parseFloat($(this).attr('valorvale').replace(',', '.'))
            data.push($(this).attr('id'))
        }
        $(idpessoal).text('R$ ' + total.toFixed(2).replace('.', ','));
    });
    return data
}

function somavales() {
    var total = 0.00
    $('.saldovale').each(function() {
        total += parseFloat($(this).text().replace('R$ ', '').replace(',', '.'))
    });
    $('#totalvales').text('R$ ' + total.toFixed(2).replace('.', ','))    
}

function estadoswitchmini(idpessoal) {
    estado_switchmini = 'Manual-'
    $('.switchmini').each(function() {
        if ($(this).is(':checked')) {
            if ($(this).attr('idpessoal') == idpessoal) {
                estado_switchmini += $(this).attr('idvales') + '-'
            }
        }
    })
    return estado_switchmini
}