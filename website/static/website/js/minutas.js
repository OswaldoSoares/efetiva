$(document).ready(function(){
    $(document).on('submit', '#form-edita-hora', function(event) {
        event.preventDefault();
        $(".div-sucesso").hide()
        $(".div-erro").hide()
        var url = $(this).attr('action') || action;
        $.ajax({
            type: $(this).attr('method'),
            url: url,
            data: $(this).serialize(),
            success: function(data){
                if (data.html_tipo_mensagem == 'ERROR') {
                    $(".mensagem-erro").text(data.html_mensagem);
                    mostraMensagemErro()
                }
                if (data.html_tipo_mensagem == 'SUCESSO') {
                    $(".mensagem-sucesso").text(data.html_mensagem);
                    mostraMensagemSucesso()
                }
                $(".total-horas").text(data.html_total_horas);
                verificaTotalHoras()
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    $(document).on('submit', '#form-edita-km', function(event) {
        event.preventDefault();
        $(".div-sucesso").hide()
        $(".div-erro").hide()
        var url = $(this).attr('action') || action;
        $.ajax({
            type: $(this).attr('method'),
            url: url,
            data: $(this).serialize(),
            success: function(data){
                if (data.html_tipo_mensagem == 'ERROR') {
                    $(".mensagem-erro").text(data.html_mensagem);
                    mostraMensagemErro()
                }
                if (data.html_tipo_mensagem == 'SUCESSO') {
                    $(".mensagem-sucesso").text(data.html_mensagem);
                    mostraMensagemSucesso()
                }
                $(".total-kms").text(data.html_total_kms);
                verificaTotalKMs()
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    $(document).on('click', '.remove-colaborador', function(event) {
        var idminutacolaboradores = $(this).attr('idMinutaColaboradores')
        var idminuta = $(this).attr('idMinuta')
        var cargo = $(this).attr('Cargo')
        $.ajax({
            type: 'GET',
            url: '/minutas/removecolaborador',
            data: {
                idMinutaColaboradores: idminutacolaboradores,
                idMinuta: idminuta,
                Cargo: cargo
            },
            success: function(data){
                if (cargo == 'AJUDANTE') {
                    $('.html-ajudante').html(data['html_ajudante']);
                } else if (cargo == 'MOTORISTA') {
                    EscondeVeiculo()
                    $('.html-veiculo').html(data['html_veiculo']);
                    MostraVeiculo()
                }
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    $(document).on('click', '.remove-despesa', function(event) {
        var idminutaitens = $(this).attr('idMinutaItens')
        var idminuta = $(this).attr('idMinuta')
        $.ajax({
            type: 'GET',
            url: '/minutas/removedespesa',
            data: {
                idMinutaItens: idminutaitens,
                idMinuta: idminuta,
            },
            success: function(data){
                EscondeDespesa()
                $('.html-despesa').html(data['html_despesa']);
                MostraDespesa()
            },
            error: function(error) {
                console.log(error)
            }
        });
    });
    
    $('#MyModal').on('shown.bs.modal', function () {
        setTimeout(function(){      // Delay para função loadCubagem, após janela estar carregada
            $(".form-radio").click(function() {
                $(".escolha-veiculo").fadeOut(500)
                var filtro = $(this).val()
                $.ajax({
                    type: 'GET',
                    url: '/minutas/filtraveiculoescolhido',
                    data: {
                        idobj: $('#idminuta').attr('idminuta'),
                        idPessoal: $("#idpessoal").attr('idpessoal'),
                        Filtro: filtro,
                    },
                    success: function(data){
                        $(".html-escolhido").html(data['html_filtro'])
                        $(".escolha-veiculo").fadeIn(500)
                    },
                    error: function(error) {
                        console.log(error)
                    }
                });
            });
            $("#id_Propriedade").focus();   // Configura o foco inicial
        }, 800);
    });
    
    verificaTotalKMs()
    verificaTotalHoras()
    $(".div-sucesso").hide()
    $(".div-erro").hide()

    // JQuery da Janela Modal
    $('#modal-formulario').on('shown.bs.modal', function () {
        setTimeout(function(){      // Delay para função loadCubagem, após janela estar carregada
            $("#id_Propriedade").change(function() {
                var obj = $(this)
                var propriedade = $(this).val();
                var idminutacolaboradores = $(".js-excluiminutamotorista").attr("idminutacolaboradores");

                $.ajax({
                    url: obj.attr("data-url"),
                    type: 'get',
                    dataType: 'json',
                    data: {
                        propriedade: propriedade,
                        idminutacolaboradores, idminutacolaboradores
                    },
                    success: function(data){
                        $("#id_Veiculo").fadeOut(500).fadeIn(500)
                        $("#id_Veiculo ").html(data.html_form)
                    }
                });
            });
            $("#id_Propriedade").focus();   // Configura o foco inicial
        }, 800);

        $('#id_NotaGuia').change(function() {
            if ($('#id_NotaGuia').val() != 0) {
                nota_guia = $('#id_NotaGuia').val()
                id_minuta = $('#id_idMinuta').val()
                $('#id_Nome').attr('readonly', 'readonly')
                $('#id_Estado').attr('readonly', 'readonly')
                $('#id_Cidade').attr('readonly', 'readonly')
                $.ajax({
                    url: '/minutas/buscaminutaentrega',
                    type: 'get',
                    dataType: 'json',
                    data: {
                        nota_guia: nota_guia,
                        id_minuta: id_minuta,
                    },
                    beforeSend: function(){
                    },
                    success: function(data){
                        $('#id_Nome').val(data.nota_guia_nome);
                        $('#id_Estado').val(data.nota_guia_estado);
                        $('#id_Cidade').val(data.nota_guia_cidade);
                    }
                });

            } else {
                $('#id_Nome').removeAttr('readonly')
                $('#id_Estado').removeAttr('readonly')
                $('#id_Cidade').removeAttr('readonly')
            }
        });
        $('#id_Nota').focusout(function() {
            if ($('#id_Nota').val().toUpperCase() == 'PERIMETRO') {
                $('#id_Estado').focus();
                $('#id_ValorNota').attr('readonly', 'readonly')
                $('#id_Peso').attr('readonly', 'readonly')
                $('#id_Volume').attr('readonly', 'readonly')
                $('#id_NotaGuia').attr('disabled', 'disabled')
                $('#id_Nome').attr('readonly', 'readonly')
            }
        });
        $("#id_EntregaNota").click(function() {
            $('#id_NotaGuia').removeAttr('disabled');
            $('#id_NotaGuia').val("0");
        });
    });

    var mostravalores = function(obj) {
        var switch_id = obj.attr('id');
        var ta_id = '#' + switch_id.replace('sw','ta');
        var mi_id = '#' + switch_id.replace('sw','mi');
        var to_id = '#' + switch_id.replace('sw','to');
        var hi_id = '#' + switch_id.replace('sw','hi');
        if (obj.is(":checked")) {
            if ($(mi_id).length) {
                if ($(ta_id).attr('meu_tipo') == '%' && $(mi_id).attr('meu_tipo') == 'R$') {
                    $(to_id).text('R$ ' + ($(ta_id).val() /100 * $(mi_id).val()).toFixed(2).replace('.',','))
                    $(hi_id).val(($(ta_id).val() /100 * $(mi_id).val()))
                } else if ($(ta_id).attr('meu_tipo') == 'R$' && $(mi_id).attr('meu_tipo') == 'HS') {
                    if (ta_id == "#ta-horas-recebe") {
                        var valor_hora = $("#ta-horas-recebe").val();
                        var horas = $("#mi-horas-recebe").val().substring(0,2);
                        var minutos = $("#mi-horas-recebe").val().substring(3,5);
                        total_horas = horas * valor_hora
                        total_minutos = minutos * (valor_hora/60).toFixed(5)
                        total_horas_recebe = total_horas + total_minutos
                        $(to_id).text('R$ ' + total_horas_recebe.toFixed(2).replace('.',','))
                        $(hi_id).val(total_horas_recebe)
                    } else if (ta_id == "#ta-horas-paga") {
                        var valor_hora = $("#ta-horas-paga").val();
                        var horas = $("#mi-horas-paga").val().substring(0,2);
                        var minutos = $("#mi-horas-paga").val().substring(3,5);
                        total_horas = horas * valor_hora
                        total_minutos = minutos * (valor_hora/60).toFixed(5)
                        total_horas_paga = total_horas + total_minutos
                        $(to_id).text('R$ ' + total_horas_paga.toFixed(2).replace('.',','))
                        $(hi_id).val(total_horas_paga)
                    }
                } else if ($(ta_id).attr('meu_tipo') == '%' && $(mi_id).attr('meu_tipo') == 'HS') {
                    if (ta_id == "#ta-horasexcede-recebe") {
                        var valor_hora_excede = $("#ta-horas-recebe").val() * ($(ta_id).val() / 100)
                        var horas = $("#mi-horasexcede-recebe").val().substring(0,2);
                        var minutos = $("#mi-horasexcede-recebe").val().substring(3,5);
                        total_horas_excede = horas * valor_hora_excede
                        total_minutos_excede = minutos * (valor_hora_excede/60).toFixed(5)
                        total_horas_excede_recebe = total_horas_excede + total_minutos_excede
                        $(to_id).text('R$ ' + total_horas_excede_recebe.toFixed(2).replace('.',','))
                        $(hi_id).val(total_horas_excede_recebe)
                    } else if (ta_id == "#ta-horasexcede-paga") {
                        var valor_hora_excede = $("#ta-horas-paga").val() * ($(ta_id).val() / 100)
                        var horas = $("#mi-horasexcede-paga").val().substring(0,2);
                        var minutos = $("#mi-horasexcede-paga").val().substring(3,5);
                        total_horas_excede = horas * valor_hora_excede
                        total_minutos_excede = minutos * (valor_hora_excede/60).toFixed(5)
                        total_horas_excede_paga = total_horas_excede + total_minutos_excede
                        $(to_id).text('R$ ' + total_horas_excede_paga.toFixed(2).replace('.',','))
                        $(hi_id).val(total_horas_excede_paga)
                    }
                } else if ($(ta_id).attr('meu_tipo') == 'R$' && $(mi_id).attr('meu_tipo') == 'UN') {
                    $(to_id).text('R$ ' + ($(ta_id).val()*$(mi_id).val()).toFixed(2).replace('.',','))
                    $(hi_id).val($(ta_id).val()*$(mi_id).val())
                } else if ($(ta_id).attr('meu_tipo') == 'R$' && $(mi_id).attr('meu_tipo') == 'KG') {
                    $(to_id).text('R$ ' + ($(ta_id).val()*$(mi_id).val()).toFixed(2).replace('.',','))
                    $(hi_id).val($(ta_id).val()*$(mi_id).val())
                }
            } else {
                if (to_id == '#to-desconto-recebe') {
                    $(to_id).text('R$ ' + ($(ta_id).val()*-1).toFixed(2).replace('.',','))
                    $(hi_id).val($(ta_id).val()*-1)
                } else {
                    $(to_id).text('R$ ' + ($(ta_id).val()*1).toFixed(2).replace('.',','))
                    $(hi_id).val($(ta_id).val())
                }
            }
        } else {
            $(to_id).text('R$ 0,00')
            $(hi_id).val(0.00)
        }
        somaPerimetro();
        // Calcula novamente o pernoite e o perimetro caso tenha alguma mudança
        if ($('#to-perimetro-recebe').is(":checked")) {
            $('#to-perimetro-recebe').text('R$ ' + ($('#ta-perimetro-recebe').val() /100 * $('#mi-perimetro-recebe').val())
            .toFixed(2).replace('.',','))
            $('#hi-perimetro-recebe').val(($('#ta-perimetro-recebe').val() /100 * $('#mi-perimetro-recebe').val()))
        }
        if ($('#to-pernoite-recebe').is(":checked")) {
            $('#to-pernoite-recebe').text('R$ ' + ($('#ta-pernoite-recebe').val() /100 * $('#mi-pernoite-recebe').val())
            .toFixed(2).replace('.',','))
            $('#hi-pernoite-recebe').val(($('#ta-pernoite-recebe').val() /100 * $('#mi-pernoite-recebe').val()))
        }
        if ($('#to-perimetro-paga').is(":checked")) {
            $('#to-perimetro-paga').text('R$ ' + ($('#ta-perimetro-paga').val() /100 * $('#mi-perimetro-paga').val())
            .toFixed(2).replace('.',','))
            $('#hi-perimetro-paga').val(($('#ta-perimetro-paga').val() /100 * $('#mi-perimetro-paga').val()))
        }
        if ($('#to-pernoite-paga').is(":checked")) {
            $('#to-pernoite-paga').text('R$ ' + ($('#ta-pernoite-paga').val() /100 * $('#mi-pernoite-paga').val())
            .toFixed(2).replace('.',','))
            $('#hi-pernoite-paga').val(($('#ta-pernoite-paga').val() /100 * $('#mi-pernoite-paga').val()))
        }
        totais();
    };

    var totais = function() {
        valor_recebe = 0.00;
        valor_paga = 0.00;
        $(".valor-recebe").each(function() {
            valor_recebe += parseFloat($(this).val())
        });
        $(".valor-paga").each(function() {
            valor_paga += parseFloat($(this).val())
        });
        $("#totalrecebe").text('R$ ' + valor_recebe.toFixed(2).replace('.',','))
        $("#totalpaga").text('R$ ' + valor_paga.toFixed(2).replace('.',','))
        $(".saldo-minuta").text('Saldo da Minuta R$ ' + (valor_recebe-valor_paga).toFixed(2).replace('.',','))
    }

    var somaPerimetro = function() {
        var soma_recebe = 0.00
        soma_recebe += $('#hi-porcentagem-recebe').val()*1
        soma_recebe += $('#hi-horas-recebe').val()*1
        soma_recebe += $('#hi-horasexcede-recebe').val()*1
        soma_recebe += $('#hi-kilometragem-recebe').val()*1
        soma_recebe += $('#hi-entregas-recebe').val()*1
        soma_recebe += $('#hi-entregaskg-recebe').val()*1
        soma_recebe += $('#hi-entregasvolume-recebe').val()*1
        soma_recebe += $('#hi-saida-recebe').val()*1
        soma_recebe += $('#hi-capacidade-recebe').val()*1
        soma_recebe = (soma_recebe*1).toFixed(2)
        $('#mi-perimetro-recebe').val(soma_recebe)
        $('#mi-pernoite-recebe').val(soma_recebe)
        var soma_paga = 0.00
        soma_paga += $('#hi-porcentagem-paga').val()*1
        soma_paga += $('#hi-horas-paga').val()*1
        soma_paga += $('#hi-horasexcede-paga').val()*1
        soma_paga += $('#hi-kilometragem-paga').val()*1
        soma_paga += $('#hi-entregas-paga').val()*1
        soma_paga += $('#hi-entregaskg-paga').val()*1
        soma_paga += $('#hi-entregasvolume-paga').val()*1
        soma_paga += $('#hi-saida-paga').val()*1
        soma_paga += $('#hi-capacidade-paga').val()*1
        soma_paga = (soma_paga*1).toFixed(2)
        $('#mi-perimetro-paga').val(soma_paga)
        $('#mi-pernoite-paga').val(soma_paga)
    }

    var loadForm = function(){
        var obj = $(this);
        var idminuta = $(this).attr("idminuta");
        var urlok = obj.attr("data-url")
        console.log(urlok)

        $.ajax({
            url: obj.attr("data-url"),
            type: 'get',
            dataType: 'json',
            data: {
                idminuta: idminuta,
            },
            beforeSend: function(){
                $("#modal-formulario .modal-content").html("");
                $("#modal-formulario").modal("show");
            },
            success: function(data){
                $("#modal-formulario .modal-content").html(data.html_form);
                if ($('#id_NotaGuia').val() != 0) {
                    $('#id_Nome').attr('readonly', 'readonly')
                    $('#id_Estado').attr('readonly', 'readonly')
                    $('#id_Cidade').attr('readonly', 'readonly')
                }
            }
        });
        
    };

    $('.switch').each(function() {
        mostravalores($(this));
    });

    $('.switch').change(function() {
        mostravalores($(this));
    });

    $('.demonstrativo-input').change(function() {
        if ($(this).attr('type') != 'time') {
            $(this).val(parseFloat($(this).val()).toFixed(2))
        }
    })

    $('.demonstrativo-input').change(function() {
        var elemento_alterado = '#sw' + $(this).attr('id').substring(2, 50)
        var obj = $('input').filter(elemento_alterado)
        mostravalores(obj);
    });

    $("#mi-ajudante-paga").attr('readonly', 'readonly')
    $(".js-criaminuta").click(loadForm);
    $(".js-editaminuta").click(loadForm);
    $(".js-imprimeminuta").click(loadForm);
    $(".js-fechaminuta").click(loadForm);
    $(".js-criaminutamotorista").click(loadForm);
    $(".js-excluiminutamotorista").click(loadForm);
    $(".js-criaminutaajudante").click(loadForm);
    $(".js-excluiminutaajudante").click(loadForm);
    $(".js-editaminutaveiculo").click(loadForm);
    $(".js-criaminutaparametrodespesa").click(loadForm);
    $(".js-excluiminutadespesa").click(loadForm);
    $(".js-criaminutaentrega").click(loadForm);
    $(".js-editaminutaentrega").click(loadForm);
    $(".js-excluiminutaentrega").click(loadForm);


    

    
    /*$(".total-horas").text(hora_minuto);*/

});

function openMyModal(event) {
    var modal = initModalDialog(event, '#MyModal');
    var url = $(event.target).data('action');
    $.ajax({
        type: "GET",
        url: url,
        data : { 
            idobj: $(event.target).data('idminuta'),
            idPessoal: $(event.target).data('idpessoal'),
        }
    }).done(function(data, textStatus, jqXHR) {
        modal.find('.modal-body').html(data.html_form);
        modal.modal('show');
        formAjaxSubmit(modal, url, null, null);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        $(".mensagem-erro").text(errorThrown);
        mostraMensagemErro()
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
                    if (xhr['c_view'] == 'insere_motorista') {
                        EscondeVeiculo()
                        $('.html-veiculo').html(xhr['html_veiculo']);
                        MostraVeiculo()
                        verificaTotalKMs()
                    } else if (xhr['c_view'] == 'insere_ajudante') {
                        $('.html-ajudante').html(xhr['html_ajudante']);
                    } else if (xhr['c_view'] == 'edita_minuta_veiculo_solicitado') {
                        if (xhr['html_tipo_mensagem'] == 'ERROR') {
                            $(".mensagem-erro").text(data.html_mensagem);
                            mostraMensagemErro()
                        }
                        if (xhr['html_tipo_mensagem'] == 'SUCESSO') {
                            $(".mensagem-sucesso").text(xhr['html_mensagem']);
                            mostraMensagemSucesso()
                            EscondeCategoria();
                            $(".html-categoria").html(xhr['html_categoria']);
                            MostraCategoria()
                            if (xhr['html_veiculo'] == '') {
                                EscondeVeiculo() 
                            } else {
                                $('.html-veiculo').html(xhr['html_veiculo']);
                                MostraVeiculo()
                                verificaTotalKMs()
                            }
                        }
                    } else if (xhr['c_view'] == 'edita_minuta_veiculo_escolhido') {
                        $(".mensagem-sucesso").text(xhr['html_mensagem']);
                        mostraMensagemSucesso()
                        EscondeVeiculo()
                        $('.html-veiculo').html(xhr['html_veiculo']);
                        MostraVeiculo()
                        verificaTotalKMs()
                    } else if (xhr['c_view'] == 'edita_minuta_coleta_entrega_obs') {
                        $(".mensagem-sucesso").text(xhr['html_mensagem']);
                        mostraMensagemSucesso()
                        EscondeInfo()
                        $('.html-coleta-entrega-obs').html(xhr['html_coleta_entrega_obs']);
                        MostraInfo()
                        verificaTotalKMs()
                    } else if (xhr['c_view'] == 'insere_minuta_despesa') {
                        $(".mensagem-sucesso").text(xhr['html_mensagem']);
                        mostraMensagemSucesso()
                        EscondeDespesa()
                        $('.html-despesa').html(xhr['html_despesa']);
                        MostraDespesa()
                        verificaTotalKMs()
                    }
                    if (cbAfterSuccess) { cbAfterSuccess(modal); }
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                $(".mensagem-erro").text(thrownError);
                mostraMensagemErro()
            },
            complete: function() {
                header.removeClass('loading');
            }
        });
    });
}

var verificaTotalHoras = function() {
    if ($(".total-horas").text() == '00:00 Hs') {
        $(".calcula-horas").slideUp(500)
        $('#id_HoraFinal').val('00:00')
    } else {
        $(".calcula-horas").slideDown(500)
    }
}

var verificaTotalKMs = function() {
    if ($(".total-kms").text() == '0 KMs') {
        $(".calcula-kms").slideUp(500)
        $('#id_KMFinal').val(0)
    } else {
        $(".calcula-kms").slideDown(500)
    }
}

var mostraMensagemErro = function() {
    $(".div-erro").slideDown(500)
    $(".div-erro").delay(5000).slideUp(500)        
}

var mostraMensagemSucesso = function() {
    $(".div-sucesso").slideDown(500)
    $(".div-sucesso").delay(5000).slideUp(500)        
}

var EscondeCategoria = function() {
    $(".html-categoria").hide()
}

var MostraCategoria = function() {
    $(".html-categoria").delay(1000).slideDown(500)
}

var EscondeVeiculo = function() {
    $(".html-veiculo").hide()
}

var MostraVeiculo = function() {
    $(".html-veiculo").delay(1000).slideDown(500)
}

var EscondeInfo = function() {
    $(".html-coleta-entrega-obs").hide()
}

var MostraInfo = function() {
    $(".html-coleta-entrega-obs").delay(1000).slideDown(500)
}

var EscondeDespesa = function() {
    $(".html-despesa").hide()
}

var MostraDespesa = function() {
    $(".html-despesa").delay(1000).slideDown(500)
}