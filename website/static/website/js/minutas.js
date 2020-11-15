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
                $(to_id).text('R$ ' + ($(ta_id).val()*1).toFixed(2).replace('.',','))
                $(hi_id).val($(ta_id).val())
            }
        } else {
            $(to_id).text('R$ 0,00')
            $(hi_id).val(0.00)
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
                console.log(data);
                $("#modal-formulario .modal-content").html(data.html_form);
                $(".js-edita-minutaveiculo-form").attr('action', "{% url 'editaminutaveiculo' 0 %}".replace(/0/, idminuta));
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

    $("#mi-ajudante-paga").attr('disabled', 'disabled')
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
