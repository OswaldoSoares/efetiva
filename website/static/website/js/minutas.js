$(document).ready(function(){
    // JQuery da Janela Modal
    $('#modal-formulario').on('shown.bs.modal', function () {
        setTimeout(function(){      // Delay para função loadCubagem, após janela estar carregada
            $("#id_Propriedade").change(function(){
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
                        console.log(data)
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
                        console.log(nota_guia, id_minuta)
                    },
                    success: function(data){
                        console.log(data)
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
                    if (ta_id = "#ta-horas-recebe") {
                        var valor_hora = $("#ta-horas-recebe").val()
                        var horas = $("#mi-horas-recebe").val().substring(0,2);
                        var minutos = $("#mi-horas-recebe").val().substring(3,5);
                        total_horas = horas * valor_hora
                        total_minutos = minutos * (valor_hora/60).toFixed(5)
                        total_horas_recebe = total_horas + total_minutos
                        $(to_id).text('R$ ' + total_horas_recebe.toFixed(2).replace('.',','))
                        $(hi_id).val(total_horas_recebe)
                    } else if (ta_id = "#ta-horas-paga") {
                        var valor_hora = $("#ta-horas-paga").val()
                        var horas = $("#mi-horas-paga").val().substring(0,2);
                        var minutos = $("#mi-horas-paga").val().substring(3,5);
                        total_horas = horas * valor_hora
                        total_minutos = minutos * (valor_hora/60).toFixed(5)
                        total_horas_paga = total_horas + total_minutos
                        $(to_id).text('R$ ' + total_horas_paga.toFixed(2).replace('.',','))
                        $(hi_id).val(total_horas_paga)
                    }
                } else if ($(ta_id).attr('meu_tipo') == '%' && $(mi_id).attr('meu_tipo') == 'HS') {
                    if (ta_id = "#ta-horasexcede-recebe") {
                        var valor_hora_excede = $("#ta-horas-recebe").val() * ($(ta_id).val() / 100)
                        var horas = $("#mi-horasexcede-recebe").val().substring(0,2);
                        var minutos = $("#mi-horasexcede-recebe").val().substring(3,5);
                        total_horas_excede = horas * valor_hora_excede
                        total_minutos_excede = minutos * (valor_hora_excede/60).toFixed(5)
                        total_horas_excede_recebe = total_horas_excede + total_minutos_excede
                        $(to_id).text('R$ ' + total_horas_excede_recebe.toFixed(2).replace('.',','))
                        $(hi_id).val(total_horas_excede_recebe)
                    } else if (ta_id = "#ta-horasexcede-paga") {
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
        soma_recebe = (soma_recebe*1).toFixed(2).replace('.',',')
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
        soma_paga = (soma_paga*1).toFixed(2).replace('.',',')
        $('#mi-perimetro-paga').val(soma_paga)
        $('#mi-pernoite-paga').val(soma_paga)
    }

    var loadForm = function(){
        var obj = $(this);
        var idminuta = $(this).attr("idminuta");

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

});
