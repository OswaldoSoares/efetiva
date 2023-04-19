$(document).ready(function() {
    /* Versão Nova */
    

    /* Versão Nova - Função que envia formulário com os itens de
    recebimento para serem processados pelo servidor */
    $(document).on('submit', '#js-gera-receitas', function(event) {
        event.preventDefault();
        $.ajax({
            type: "POST",
            url: "/minutas/gera_receitas",
            data: $(this).serialize,
            beforeSend: function() {
                $(".box-loader").show();
            },
            success: function(data) {
                $(".box-loader").hide();
            },
            error: function(error) {
                $(".mensagem-erro").text(
                    error.status + " " + error.message + " "
                    + "- entre em contato com o administrador do aplicativo."
                );
                $('html, body').scrollTop(0);
                $(".box-loader").hide();
                mostraMensagemErro()
                console.log(error)
            },
        });
    });
    
    /* Versão Nova */
    $(document).on('submit', '#js-gera-pagamentos', function(event) {
        event.preventDefault();
        $.ajax({
            type: "POST",
            url: '/minutas/gera_pagamentos',
            data: $(this).serialize(),
            before: function() {
                $(".box-loader").show();
            },
            success: function(data) {
                $(".box-loader").hide();
                window.location.href = '/minutas/minuta/' + data['html_idminuta'] + '/'
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Versão Nova //
    $(document).on('click', '.estorna-pagamentos', function(event) {
        $(".container").hide()
        var idminuta = $(this).attr('idMinuta')
        $.ajax({
            type: 'GET',
            url: '/minutas/estornapagamentos',
            data: {
                idMinuta: idminuta,
            },
            success: function(data) {
                window.location.href = '/minutas/minuta/' + data['html_idminuta'] + '/'
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Versão Nova //
    $(document).on('click', '.conclui-minuta', function(event) {
        var idminuta = $(this).attr('idMinuta')
        $.ajax({
            type: 'GET',
            url: '/minutas/concluirminuta',
            data: {
                idMinuta: idminuta,
            },
            success: function(data) {
                $(".html-checklist").hide()
                $('.html-checklist').html(data['html_checklist']);
                mostraChecklist();
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Versão Nova //
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
            success: function(data) {
                if (cargo == 'AJUDANTE') {
                    $('.html-ajudante').html(data['html_ajudante']);
                } else if (cargo == 'MOTORISTA') {
                    EscondeVeiculo()
                    $('.html-veiculo').html(data['html_veiculo']);
                    MostraVeiculo();
                }
                recarregaFinanceiro(data['html_pagamento'], data['html_recebimento'])
                $(".html-checklist").hide()
                $('.html-checklist').html(data['html_checklist']);
                mostraChecklist();
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Versão Nova //
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
            success: function(data) {
                recarregaFinanceiro(data['html_pagamento'], data['html_recebimento'])
                $(".html-checklist").hide()
                $('.html-checklist').html(data['html_checklist']);
                mostraChecklist();
                EscondeDespesa();
                $('.html-despesa').html(data['html_despesa']);
                MostraDespesa();
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Versão Nova //
    $(document).on('click', '.remove-entrega', function(event) {
        var idminutanotas = $(this).attr('idMinutaNotas')
        var idminuta = $(this).attr('idMinuta')
        $.ajax({
            type: 'GET',
            url: '/minutas/removeentrega',
            data: {
                idMinutaNotas: idminutanotas,
                idMinuta: idminuta,
            },
            success: function(data) {
                recarregaFinanceiro(data['html_pagamento'], data['html_recebimento'])
                $(".html-checklist").hide()
                $('.html-checklist').html(data['html_checklist']);
                mostraChecklist();
                EscondeEntrega()
                $('.card-entrega').html(data['html_entrega']);
                MostraEntrega()
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Versão Nova - Consultas //
    $(document).on('click', '.list-cliente', function(event) {
        $(".fd-colaborador").hide()
        $(".list-colaborador").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".fd-veiculo").hide()
        $(".list-veiculo").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".fd-entrega-cidade").hide()
        $(".list-entrega-cidade").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".filtro-destinatario").hide()
        $(".digita-destinatario").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        if ($('.fd-cliente').is(':hidden')) {
            $(".fd-cliente").show()
            $(this).removeClass("bi-caret-right-fill").addClass("bi-caret-down-fill");
        } else {
            $(".fd-cliente").hide()
            $(this).removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        }
    });

    // Versão Nova - Consultas //
    $(document).on('click', '.list-colaborador', function(event) {
        $(".fd-cliente").hide()
        $(".list-cliente").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".fd-veiculo").hide()
        $(".list-veiculo").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".fd-entrega-cidade").hide()
        $(".list-entrega-cidade").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".filtro-destinatario").hide()
        $(".digita-destinatario").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        if ($('.fd-colaborador').is(':hidden')) {
            $(".fd-colaborador").show()
            $(this).removeClass("bi-caret-right-fill").addClass("bi-caret-down-fill");
        } else {
            $(".fd-colaborador").hide()
            $(this).removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        }
    });

    // Versão Nova - Consultas //
    $(document).on('click', '.list-veiculo', function(event) {
        $(".fd-cliente").hide()
        $(".list-cliente").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".fd-colaborador").hide()
        $(".list-colaborador").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".fd-entrega-cidade").hide()
        $(".list-entrega-cidade").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".filtro-destinatario").hide()
        $(".digita-destinatario").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        if ($('.fd-veiculo').is(':hidden')) {
            $(".fd-veiculo").show()
            $(this).removeClass("bi-caret-right-fill").addClass("bi-caret-down-fill");
        } else {
            $(".fd-veiculo").hide()
            $(this).removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        }
    });

    // Versão Nova - Consultas //
    $(document).on('click', '.list-entrega-cidade', function(event) {
        $(".fd-cliente").hide()
        $(".list-cliente").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".fd-colaborador").hide()
        $(".list-colaborador").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".fd-veiculo").hide()
        $(".list-veiculo").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".filtro-destinatario").hide()
        $(".digita-destinatario").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        if ($('.fd-entrega-cidade').is(':hidden')) {
            $(".fd-entrega-cidade").show()
            $(this).removeClass("bi-caret-right-fill").addClass("bi-caret-down-fill");
        } else {
            $(".fd-entrega-cidade").hide()
            $(this).removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        }
    });

    // Versão Nova - Consultas //
    $(document).on('click', '.digita-destinatario', function(event) {
        $(".fd-cliente").hide()
        $(".list-cliente").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".fd-colaborador").hide()
        $(".list-colaborador").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".fd-veiculo").hide()
        $(".list-veiculo").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        $(".fd-entrega-cidade").hide()
        $(".list-entrega-cidade").removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        if ($('.filtro-destinatario').is(':hidden')) {
            $(".filtro-destinatario").show()
            $(this).removeClass("bi-caret-right-fill").addClass("bi-caret-down-fill");
        } else {
            $(".filtro-destinatario").hide()
            $(this).removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
        }
    });

    // Versão Nova - Consultas //
    $(document).on('click', '.filtro-consulta', function(event) {
        $(".filtro-lista").each(function() {
            $(this).addClass("i-button")
        });
        if ($(".minutas-atual").is(":hidden")) {
            $(".minutas-consulta").hide()
        } else {
            $(".minutas-atual").hide()
        }
        $(".box-loader").show()
        $(this).removeClass("i-button")
        var filtro = $(this).attr('data-filtro')
        var filtro_consula = $(this).attr('data-filtro-consulta')
        var meses = $(this).attr('data-meses')
        var anos = $(this).attr('data-anos')
        $.ajax({
            type: 'GET',
            url: '/minutas/filtraminuta',
            data: {
                Filtro: filtro,
                FiltroConsulta: filtro_consula,
                Meses: meses,
                Anos: anos,
            },
            success: function(data) {
                $(".minutas-consulta").html(data['html_filtra_minuta'])
                $(".box-loader").hide()
                $(".minutas-consulta").show()
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    // Versão Nova - Consultas //
    $(document).on('click', '.filtro-periodo', function(event) {
        $(".minutas-consulta").hide()
        $(".box-loader").show()
        var filtro = $(this).attr('data-filtro')
        var filtro_consula = $(this).attr('data-filtro-consulta')
        var meses = $(this).attr('data-meses')
        var anos = $(this).attr('data-anos')
        var menu_selecionado = $(this)
        $.ajax({
            type: 'GET',
            url: '/minutas/filtraminuta',
            data: {
                Filtro: filtro,
                FiltroConsulta: filtro_consula,
                Meses: meses,
                Anos: anos,
            },
            success: function(data) {
                $(".minutas-consulta").html(data['html_filtra_minuta'])
                $(".filtro-periodo").each(function() {
                    if ($(this).text() == menu_selecionado.text()) {
                        $(this).removeClass("i-button")
                    } else {
                        $(this).addClass("i-button")
                    }
                });
                $(".box-loader").hide()
                $(".minutas-consulta").show()
            },
            error: function(error) {
                console.log(error)
            }
        })
    });

    // Versão Nova - Consultas //
    $(document).on('click', '.search-destinatario', function(event) {
        $(".filtro-lista").each(function() {
            $(this).addClass("i-button")
        });
        if ($(".minutas-atual").is(":hidden")) {
            $(".minutas-consulta").hide()
        } else {
            $(".minutas-atual").hide()
        }
        $(".box-loader").show()
        var filtro = $(".text-search").val()
        var filtro_consula = $(this).attr('data-filtro-consulta')
        var meses = $(this).attr('data-meses')
        var anos = $(this).attr('data-anos')
        var menu_selecionado = $(this)
        $.ajax({
            type: 'GET',
            url: '/minutas/filtraminuta',
            data: {
                Filtro: filtro,
                FiltroConsulta: filtro_consula,
                Meses: meses,
                Anos: anos,
            },
            success: function(data) {
                $(".minutas-consulta").html(data['html_filtra_minuta'])
                $(".box-loader").hide()
                $(".minutas-consulta").show()
            },
            error: function(error) {
                console.log(error)
            }
        })
    });


    $('#MyModal').on('shown.bs.modal', function() {
        setTimeout(function() { // Delay para função loadCubagem, após janela estar carregada
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
                    success: function(data) {
                        $(".html-escolhido").html(data['html_filtro'])
                        $(".escolha-veiculo").fadeIn(500)
                    },
                    error: function(error) {
                        console.log(error)
                    }
                });
            });
            $("#id_Propriedade").focus(); // Configura o foco inicial
        }, 800);
    });

    verificaTotalKMs()
    verificaTotalHoras()
    // Versão Nova //
    $(".div-sucesso").hide()
    // Versão Nova //
    $(".div-erro").hide()
    $(".filtro-dados").hide()
    $(".minutas-consulta").hide()
    // Versão Nova //
    $(".box-loader").hide()
    $(".filtro-destinatario").hide()

    // JQuery da Janela Modal Antigo
    $('#modal-formulario').on('shown.bs.modal', function() {
        setTimeout(function() { // Delay para função loadCubagem, após janela estar carregada
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
                        idminutacolaboradores,
                        idminutacolaboradores
                    },
                    success: function(data) {
                        $("#id_Veiculo").fadeOut(500).fadeIn(500)
                        $("#id_Veiculo ").html(data.html_form)
                    }
                });
            });
            $("#id_Propriedade").focus(); // Configura o foco inicial
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
                    beforeSend: function() {},
                    success: function(data) {
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

    // Versão Antiga //
    var mostravalores = function(obj) {
        var switch_id = obj.attr('id');
        var ta_id = '#' + switch_id.replace('sw', 'ta');
        var mi_id = '#' + switch_id.replace('sw', 'mi');
        var to_id = '#' + switch_id.replace('sw', 'to');
        var hi_id = '#' + switch_id.replace('sw', 'hi');
        if (obj.is(":checked")) {
            if ($(mi_id).length) {
                if ($(ta_id).attr('meu_tipo') == '%' && $(mi_id).attr('meu_tipo') == 'R$') {
                    $(to_id).text('R$ ' + ($(ta_id).val() / 100 * $(mi_id).val()).toFixed(2).replace('.', ','))
                    $(hi_id).val(($(ta_id).val() / 100 * $(mi_id).val()))
                } else if ($(ta_id).attr('meu_tipo') == 'R$' && $(mi_id).attr('meu_tipo') == 'HS') {
                    if (ta_id == "#ta-horas-recebe") {
                        var valor_hora = $("#ta-horas-recebe").val();
                        var horas = $("#mi-horas-recebe").val().substring(0, 2);
                        var minutos = $("#mi-horas-recebe").val().substring(3, 5);
                        total_horas = horas * valor_hora
                        total_minutos = minutos * (valor_hora / 60).toFixed(5)
                        total_horas_recebe = total_horas + total_minutos
                        $(to_id).text('R$ ' + total_horas_recebe.toFixed(2).replace('.', ','))
                        $(hi_id).val(total_horas_recebe)
                    } else if (ta_id == "#ta-horas-paga") {
                        var valor_hora = $("#ta-horas-paga").val();
                        var horas = $("#mi-horas-paga").val().substring(0, 2);
                        var minutos = $("#mi-horas-paga").val().substring(3, 5);
                        total_horas = horas * valor_hora
                        total_minutos = minutos * (valor_hora / 60).toFixed(5)
                        total_horas_paga = total_horas + total_minutos
                        $(to_id).text('R$ ' + total_horas_paga.toFixed(2).replace('.', ','))
                        $(hi_id).val(total_horas_paga)
                    }
                } else if ($(ta_id).attr('meu_tipo') == '%' && $(mi_id).attr('meu_tipo') == 'HS') {
                    if (ta_id == "#ta-horasexcede-recebe") {
                        var valor_hora_excede = $("#ta-horas-recebe").val() * ($(ta_id).val() / 100)
                        var horas = $("#mi-horasexcede-recebe").val().substring(0, 2);
                        var minutos = $("#mi-horasexcede-recebe").val().substring(3, 5);
                        total_horas_excede = horas * valor_hora_excede
                        total_minutos_excede = minutos * (valor_hora_excede / 60).toFixed(5)
                        total_horas_excede_recebe = total_horas_excede + total_minutos_excede
                        $(to_id).text('R$ ' + total_horas_excede_recebe.toFixed(2).replace('.', ','))
                        $(hi_id).val(total_horas_excede_recebe)
                    } else if (ta_id == "#ta-horasexcede-paga") {
                        var valor_hora_excede = $("#ta-horas-paga").val() * ($(ta_id).val() / 100)
                        var horas = $("#mi-horasexcede-paga").val().substring(0, 2);
                        var minutos = $("#mi-horasexcede-paga").val().substring(3, 5);
                        total_horas_excede = horas * valor_hora_excede
                        total_minutos_excede = minutos * (valor_hora_excede / 60).toFixed(5)
                        total_horas_excede_paga = total_horas_excede + total_minutos_excede
                        $(to_id).text('R$ ' + total_horas_excede_paga.toFixed(2).replace('.', ','))
                        $(hi_id).val(total_horas_excede_paga)
                    }
                } else if ($(ta_id).attr('meu_tipo') == 'R$' && $(mi_id).attr('meu_tipo') == 'UN') {
                    $(to_id).text('R$ ' + ($(ta_id).val() * $(mi_id).val()).toFixed(2).replace('.', ','))
                    $(hi_id).val($(ta_id).val() * $(mi_id).val())
                    $(mi_id).val(parseFloat($(mi_id).val()).toFixed(0).replace('.', ','))
                } else if ($(ta_id).attr('meu_tipo') == 'R$' && $(mi_id).attr('meu_tipo') == 'KG') {
                    $(to_id).text('R$ ' + ($(ta_id).val() * $(mi_id).val()).toFixed(2).replace('.', ','))
                    $(hi_id).val($(ta_id).val() * $(mi_id).val())
                }
            } else {
                if (to_id == '#to-desconto-recebe') {
                    $(to_id).text('R$ ' + ($(ta_id).val() * -1).toFixed(2).replace('.', ','))
                    $(hi_id).val($(ta_id).val() * -1)
                } else {
                    $(to_id).text('R$ ' + ($(ta_id).val() * 1).toFixed(2).replace('.', ','))
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
            $('#to-perimetro-recebe').text('R$ ' + ($('#ta-perimetro-recebe').val() / 100 * $('#mi-perimetro-recebe').val())
                .toFixed(2).replace('.', ','))
            $('#hi-perimetro-recebe').val(($('#ta-perimetro-recebe').val() / 100 * $('#mi-perimetro-recebe').val()))
        }
        if ($('#to-pernoite-recebe').is(":checked")) {
            $('#to-pernoite-recebe').text('R$ ' + ($('#ta-pernoite-recebe').val() / 100 * $('#mi-pernoite-recebe').val())
                .toFixed(2).replace('.', ','))
            $('#hi-pernoite-recebe').val(($('#ta-pernoite-recebe').val() / 100 * $('#mi-pernoite-recebe').val()))
        }
        if ($('#to-perimetro-paga').is(":checked")) {
            $('#to-perimetro-paga').text('R$ ' + ($('#ta-perimetro-paga').val() / 100 * $('#mi-perimetro-paga').val())
                .toFixed(2).replace('.', ','))
            $('#hi-perimetro-paga').val(($('#ta-perimetro-paga').val() / 100 * $('#mi-perimetro-paga').val()))
        }
        if ($('#to-pernoite-paga').is(":checked")) {
            $('#to-pernoite-paga').text('R$ ' + ($('#ta-pernoite-paga').val() / 100 * $('#mi-pernoite-paga').val())
                .toFixed(2).replace('.', ','))
            $('#hi-pernoite-paga').val(($('#ta-pernoite-paga').val() / 100 * $('#mi-pernoite-paga').val()))
        }
        totais();
    };

    // Versão Antiga //
    var totais = function() {
        valor_recebe = 0.00;
        valor_paga = 0.00;
        $(".valor-recebe").each(function() {
            valor_recebe += parseFloat($(this).val())
        });
        $(".valor-paga").each(function() {
            valor_paga += parseFloat($(this).val())
        });
        $("#totalrecebe").text('R$ ' + valor_recebe.toFixed(2).replace('.', ','))
        $("#totalpaga").text('R$ ' + valor_paga.toFixed(2).replace('.', ','))
        $(".saldo-minuta").text('Saldo da Minuta R$ ' + (valor_recebe - valor_paga).toFixed(2).replace('.', ','))
    }

    // Versão Antiga //
    var somaPerimetro = function() {
        var soma_recebe = 0.00
        soma_recebe += $('#hi-porcentagem-recebe').val() * 1
        soma_recebe += $('#hi-horas-recebe').val() * 1
        soma_recebe += $('#hi-horasexcede-recebe').val() * 1
        soma_recebe += $('#hi-kilometragem-recebe').val() * 1
        soma_recebe += $('#hi-entregas-recebe').val() * 1
        soma_recebe += $('#hi-entregaskg-recebe').val() * 1
        soma_recebe += $('#hi-entregasvolume-recebe').val() * 1
        soma_recebe += $('#hi-saida-recebe').val() * 1
        soma_recebe += $('#hi-capacidade-recebe').val() * 1
        soma_recebe = (soma_recebe * 1).toFixed(2)
        $('#mi-perimetro-recebe').val(soma_recebe)
        $('#mi-pernoite-recebe').val(soma_recebe)
        var soma_paga = 0.00
        soma_paga += $('#hi-porcentagem-paga').val() * 1
        soma_paga += $('#hi-horas-paga').val() * 1
        soma_paga += $('#hi-horasexcede-paga').val() * 1
        soma_paga += $('#hi-kilometragem-paga').val() * 1
        soma_paga += $('#hi-entregas-paga').val() * 1
        soma_paga += $('#hi-entregaskg-paga').val() * 1
        soma_paga += $('#hi-entregasvolume-paga').val() * 1
        soma_paga += $('#hi-saida-paga').val() * 1
        soma_paga += $('#hi-capacidade-paga').val() * 1
        soma_paga = (soma_paga * 1).toFixed(2)
        $('#mi-perimetro-paga').val(soma_paga)
        $('#mi-pernoite-paga').val(soma_paga)
    }

    // Versão Antiga //
    var loadForm = function() {
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
            beforeSend: function() {
                $("#modal-formulario .modal-content").html("");
                $("#modal-formulario").modal("show");
            },
            success: function(data) {
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
            if ($(this).attr('id') == 'ta-seguro-recebe') {
                $(this).val(parseFloat($(this).val()).toFixed(3))
            } else {
                $(this).val(parseFloat($(this).val()).toFixed(2))
            }
        };
    });

    $('.demonstrativo-input').change(function() {
        var elemento_alterado = '#sw' + $(this).attr('id').substring(2, 50)
        var obj = $('input').filter(elemento_alterado)
        mostravalores(obj);
    });

    // Versão Antiga //
    $("#mi-ajudante-paga").attr('readonly', 'readonly');
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
 

    

    // Utilizado na Versão Nova
    verificaCheckboxPaga();
    verificaCheckboxRecebe();
    mostraChecklist();
    formatMask();
});











function openMyModal(event) {
    var modal = initModalDialog(event, '#MyModal');
    var url = $(event.target).data('action');
    $.ajax({
        type: "GET",
        url: url,
        data: {
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
    if (cbAfterLoad) {
        cbAfterLoad(modal);
    }
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
                    recarregaFinanceiro(xhr['html_pagamento'], xhr['html_recebimento'])
                    $(".html-checklist").hide()
                    $('.html-checklist').html(xhr['html_checklist']);
                    mostraChecklist();
                    if (xhr['c_view'] == 'adiciona_minuta') {
                        window.location.href = '/minutas/minuta/' + xhr['id_minuta_salva'] + '/'
                    } else if (xhr['c_view'] == 'edita_minuta') {
                        $(".mensagem-sucesso").text(xhr['html_mensagem']);
                        mostraMensagemSucesso()
                        EscondeCliente()
                        $('.html-cliente-data').html(xhr['html_cliente_data']);
                        MostraCliente()
                    } else if (xhr['c_view'] == 'insere_motorista') {
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
                    } else if (xhr['c_view'] == 'insere_minuta_entrega') {
                        $(".mensagem-sucesso").text(xhr['html_mensagem']);
                        mostraMensagemSucesso()
                        EscondeEntrega()
                        $('.card-entrega').html(xhr['html_entrega']);
                        MostraEntrega()
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

var EscondeCategoria = function() {
    $(".html-categoria").hide()
}

var MostraCategoria = function() {
    $(".html-categoria").delay(1000).slideDown(500)
}

var EscondeCliente = function() {
    $(".html-cliente-data").hide()
}

var MostraCliente = function() {
    $(".html-cliente-data").delay(1000).slideDown(500)
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

var EscondeEntrega = function() {
    $(".card-entrega").hide()
}

var MostraEntrega = function() {
    $(".card-entrega").delay(1000).slideDown(500)
}


var mostraChecklist = function() {
    $(".html-checklist").slideDown(500)
    $(".chk-red").each(function() {
        $('.conclui-minuta').slideUp(500)
    });
    $(".chk-red-gera-paga").each(function() {
        $('.conclui-minuta').slideUp(500)
    });
}











// Utilizado no Card-Receitas e no Card-Pagamentos
// Calcular inputs de Time
function calculaHora(v_porcentagem, v_valor1, v_hora) {
    var horas = v_hora.substring(0, 2)
    var minutos = v_hora.substring(3, 5)
    var valor_hora = (
        parseFloat
            (v_porcentagem.replace('.', '').replace(',', '.')
        ) / 100 * parseFloat(
                v_valor1.replace('.', '').replace(',', '.')
            )
    )
    var valor_minuto = (valor_hora / 60)
    return ((valor_hora * horas) + (valor_minuto * minutos)).toFixed(2)
}

// Utilizado no Card-Receitas e no Card-Pagamentos
// Calcular inputs de Numeros
function calculaMultiplo(v_valor1, v_valor2) {
    var valor1 = parseFloat(
        v_valor1.replace('.', '').replace(',', '.')
    )
    var valor2 = parseFloat(
        v_valor2.replace('.', '').replace(',', '.')
    )
    return (valor1 * valor2).toFixed(2)
}

// Utilizado no Card-Receitas e no Card-Pagamentos
// Calcular inputs de Porcentagem
function calculaPorcentagem(v_porcentagem, v_valor) {
    var valor1 = parseFloat(
        v_porcentagem.replace('.', '').replace(',', '.')
    ) / 100
    var valor2 = parseFloat(
        v_valor.replace('.', '').replace(',', '.')
    )
    return (valor1 * valor2).toFixed(2)
}

// Utilizado no Card-Pagamentos
// Calcula valor-item-paga
function calculosMudarInputPaga(element_select, valor_digitado) {
    if (element_select == 'tabela-porcentagem-paga'
     || element_select == 'minuta-porcentagem-paga') {
        // PORCENTAGEM PAGA
        $('#valor-porcentagem-paga').val(
            calculaPorcentagem(
                $('#tabela-porcentagem-paga').val(),
                $('#minuta-porcentagem-paga').val()
            )
        )
    } else if (element_select == 'tabela-hora-paga'
     || element_select == 'minuta-hora-paga') {
        // HORA PAGA
        $('#valor-hora-paga').val(
            calculaHora(
                '100',
                $('#tabela-hora-paga').val(),
                $('#minuta-hora-paga').val()
            )
        )
    } else if (element_select == 'tabela-excedente-paga'
     || element_select == 'minuta-excedente-paga') {
        // EXCEDENTE PAGA
        $('#valor-excedente-paga').val(
            calculaHora(
                $('#tabela-excedente-paga').val(),
                $('#tabela-hora-paga').val(),
                $('#minuta-excedente-paga').val()
            )
        )
    } else if (element_select == 'tabela-kilometragem-paga'
     || element_select == 'minuta-kilometragem-paga') {
        // KILOMETRAGEM PAGA
        $('#valor-kilometragem-paga').val(
            calculaMultiplo(
                $('#tabela-kilometragem-paga').val(),
                $('#minuta-kilometragem-paga').val()
            )
        )
    } else if (element_select == 'tabela-entrega-paga'
     || element_select == 'minuta-entrega-paga') {
        // ENTREGA RECEBE
        $('#valor-entrega-paga').val(
            calculaMultiplo(
                $('#tabela-entrega-paga').val(),
                $('#minuta-entrega-paga').val()
            )
        )
    } else if (element_select == 'tabela-entrega-kg-paga'
     || element_select == 'minuta-entrega-kg-paga') {
        // ENTREGA KG RECEBE
        $('#valor-entrega-kg-paga').val(
            calculaMultiplo(
                $('#tabela-entrega-kg-paga').val(),
                $('#minuta-entrega-kg-paga').val()
            )
        )
    } else if (element_select == 'tabela-entrega-volume-paga'
     || element_select == 'minuta-entrega-volume-paga') {
        // ENTREGA VOLUME RECEBE
        $('#valor-entrega-volume-paga').val(
            calculaMultiplo(
                $('#tabela-entrega-volume-paga').val(),
                $('#minuta-entrega-volume-paga').val()
            )
        )
    } else if (element_select == 'tabela-saida-paga') {
        // SAÍDA RECEBE
        $('#valor-saida-paga').val(
            valor_digitado
        )
    } else if (element_select == 'tabela-capacidade-paga') {
        // CAPACIDADE RECEBE
        $('#valor-capacidade-paga').val(
            valor_digitado
        )
    } else if (element_select == 'tabela-perimetro-paga'
     || element_select == 'minuta-perimetro-paga') {
        // PERIMETRO RECEBE
        $('#valor-perimetro-paga').val(
            calculaPorcentagem(
                $('#tabela-perimetro-paga').val(),
                $('#minuta-perimetro-paga').val()
            )
        )
    } else if (element_select == 'tabela-pernoite-paga'
     || element_select == 'minuta-pernoite-paga') {
        // PERNOITE RECEBE
        $('#valor-pernoite-paga').val(
            calculaPorcentagem(
                $('#tabela-pernoite-paga').val(),
                $('#minuta-pernoite-paga').val()
            )
        )
    } else if (element_select == "tabela-ajudante-paga") {
        // AJUDANTE PAGA
        $('#valor-ajudante-paga').val(
            valor_digitado
        )
    }
    // recarrega mask
    formatUnmask();
    formatMask();
    // Faz a soma geral com os valores atualizados 
    somaPagamentos();
}

// Utilizado no Card-Receitas
// Calcula valor-item-recebe
function calculosMudarInputRecebe(element_select, valor_digitado) {
    if (element_select == 'tabela-taxa-recebe') {
        // TAXA DE EXPEDIÇÃO RECEBE
        $('#valor-taxa-recebe').val(
            valor_digitado
        )
    } else if (element_select == 'tabela-seguro-recebe'
     || element_select == 'minuta-seguro-recebe') {
        // SEGURO RECEBE
        console.log("aqio")
        $('#valor-seguro-recebe').val(
            calculaPorcentagem(
                $('#tabela-seguro-recebe').val(),
                $('#minuta-seguro-recebe').val()
            )
        )
    } else if (element_select == 'tabela-porcentagem-recebe'
     || element_select == 'minuta-porcentagem-recebe') {
        // PORCENTAGEM RECEBE
        $('#valor-porcentagem-recebe').val(
            calculaPorcentagem(
                $('#tabela-porcentagem-recebe').val(),
                $('#minuta-porcentagem-recebe').val()
            )
        )
    } else if (element_select == 'tabela-hora-recebe'
     || element_select == 'minuta-hora-recebe') {
        // HORA RECEBE
        $('#valor-hora-recebe').val(
            calculaHora(
                '100',
                $('#tabela-hora-recebe').val(),
                $('#minuta-hora-recebe').val()
            )
        )
    } else if (element_select == 'tabela-excedente-recebe'
     || element_select == 'minuta-excedente-recebe') {
        // EXCEDENTE RECEBE
        $('#valor-excedente-recebe').val(
            calculaHora(
                $('#tabela-excedente-recebe').val(),
                $('#tabela-hora-recebe').val(),
                $('#minuta-excedente-recebe').val()
            )
        )
    } else if (element_select == 'tabela-kilometragem-recebe'
     || element_select == 'minuta-kilometragem-recebe') {
        // KILOMETRAGEM RECEBE
        $('#valor-kilometragem-recebe').val(
            calculaMultiplo(
                $('#tabela-kilometragem-recebe').val(),
                $('#minuta-kilometragem-recebe').val()
            )
        )
    } else if (element_select == 'tabela-entrega-recebe'
     || element_select == 'minuta-entrega-recebe') {
        // ENTREGA RECEBE
        $('#valor-entrega-recebe').val(
            calculaMultiplo(
                $('#tabela-entrega-recebe').val(),
                $('#minuta-entrega-recebe').val()
            )
        )
    } else if (element_select == 'tabela-entrega-kg-recebe'
     || element_select == 'minuta-entrega-kg-recebe') {
        // ENTREGA KG RECEBE
        $('#valor-entrega-kg-recebe').val(
            calculaMultiplo(
                $('#tabela-entrega-kg-recebe').val(),
                $('#minuta-entrega-kg-recebe').val()
            )
        )
    } else if (element_select == 'tabela-entrega-volume-recebe'
     || element_select == 'minuta-entrega-volume-recebe') {
        // ENTREGA VOLUME RECEBE
        $('#valor-entrega-volume-recebe').val(
            calculaMultiplo(
                $('#tabela-entrega-volume-recebe').val(),
                $('#minuta-entrega-volume-recebe').val()
            )
        )
    } else if (element_select == 'tabela-saida-recebe') {
        // SAÍDA RECEBE
        $('#valor-saida-recebe').val(
            valor_digitado
        )
    } else if (element_select == 'tabela-capacidade-recebe') {
        // CAPACIDADE RECEBE
        $('#valor-capacidade-recebe').val(
            valor_digitado
        )
    } else if (element_select == 'tabela-perimetro-recebe'
     || element_select == 'minuta-perimetro-recebe') {
        // PERIMETRO RECEBE
        $('#valor-perimetro-recebe').val(
            calculaPorcentagem(
                $('#tabela-perimetro-recebe').val(),
                $('#minuta-perimetro-recebe').val()
            )
        )
    } else if (element_select == 'tabela-pernoite-recebe' || element_select == 'minuta-pernoite-recebe') {
        // PERNOITE RECEBE
        $('#valor-pernoite-recebe').val(
            calculaPorcentagem(
                $('#tabela-pernoite-recebe').val(),
                $('#minuta-pernoite-recebe').val()
            )
        )
    } else if (element_select == 'tabela-ajudante-recebe' || element_select == 'minuta-ajudante-recebe') {
        // AJUDANTE RECEBE
        $('#valor-ajudante-recebe').val(
            calculaMultiplo(
                $('#tabela-ajudante-recebe').val(),
                $('#minuta-ajudante-recebe').val()
            )
        )
    } else if (element_select.substring(0, 21) == 'tabela-despesa-recebe') {
        // DESPESA RECEBE
        $('#valor-despesa-recebe-' + element_select.substring(2)).val(
            valor_digitado
        )
    } 
    // recarrega mask
    formatUnmask();
    formatMask();
    // Faz a soma geral com os valores atualizados 
    somaReceitas();
}

// Utilizado no Card-Entrega (Formulário Modal)
$(document).on('click', '#chk-perimetro', function(event) {
    alert("OK")
    if ($('#chk-perimetro').is(':checked')) {
        $('.js-perimetro-hide').hide();
        $('#js-perimetro-div').removeClass('col-md-2');
        $('#js-perimetro-div').addClass('col-md-12');
        $('#id_Nota').val('PERIMETRO');
        $('#id_Estado').focus();
    } else {
        $('.js-perimetro-hide').show();
        $('#js-perimetro-div').removeClass('col-md-12');
        $('#js-perimetro-div').addClass('col-md-2');
        $('#id_Nota').val('');
        $('#id_Nota').focus();
    }
});

// Utilizado no Card-Entrega (Formulário Modal)
$(document).on('click', '#chk-saida', function(event) {
    if ($('#chk-saida').is(":checked")) {
        $('#id_Nota').val($('#label-chk-saida').attr('saida'))
        $('#id_ValorNota').focus();
    } else {
        $('#id_Nota').val('')
        $('#id_Nota').focus();
    }
});

// Utilizado no Card-Receitas e no Card-Pagamentos
// aplica , e . de milhar pt-BR
function formatMask() {
    $(".js-decimal").each(function() {
        $(this).mask('#.##0,00', { reverse: true })
        if ($(this).attr("id") == "tabela-seguro-recebe") {
            $(this).mask('#.##0,000', { reverse: true })
        }
    });
    $(".js-unidade").each(function() {
        $(this).mask('#.##0', { reverse: true })
    });
    $('.total-recebe').mask('#.##0,00', { reverse: true })
    $('.total-pagamentos').mask('#.##0,00', { reverse: true })
}

// Utilizado no Card-Receitas e no Card-Pagamentos
// remove , e . de milhar pt-BR
function formatUnmask() {
    $(".js-decimal").each(function() {
        $(this).unmask()
    });
    $(".js-unidade").each(function() {
        $(this).unmask()
    });
    $('.total-recebe').unmask()
    $('.total-pagamentos').unmask()
}

// Card Entregas e Card Romaneio
$(document).on('click', '.js-adiciona-romaneio-minuta', function() {
    var idromaneio = $(this).data('idromaneio')
    var idminuta = $(this).data('idminuta')
    var idcliente = $(this).data('idcliente')
    $.ajax({
        type: 'GET',
        url: '/minutas/adiciona_romaneio_minuta',
        data: {
            idromaneio: idromaneio,
            idminuta: idminuta,
            idcliente: idcliente
        },
        beforeSend: function() {
            $('.card-entrega').hide()
            $('.card-romaneio').hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $('.card-entrega').html(data['html_entrega'])
            $('.card-entrega').show()
            $('.card-romaneio').html(data['html_romaneio'])
            $('.card-romaneio').show()
            $(".box-loader").hide()
        },
    });
});

// Utilizada no Catd-Minuta
// para atualizar data de fechamento da minuta
$(document).on('submit', '#form-edita-hora', function(event) {
    event.preventDefault();
    $.ajax({
        type: "POST",
        url: "/minutas/editahorafinal/",
        data: $(this).serialize(),
        beforeSend: function() {
            $(".box-loader").show()
            $(".div-sucesso").hide()
            $(".div-erro").hide()
            $(".html-checklist").hide()
            $('.html-form-paga').hide();
            $('.html-form-recebe').hide();
        },
        success: function(data) {
            if (data.html_tipo_mensagem == 'ERROR') {
                $(".mensagem-erro").text(data.html_mensagem);
                mostraMensagemErro()
            }
            if (data.html_tipo_mensagem == 'SUCESSO') {
                $(".mensagem-sucesso").text(data.html_mensagem);
                mostraMensagemSucesso()
            }
            $(".total-horas").text(data.html_total_horas);
            $('.html-checklist').html(data['html_checklist']); 
            $('.html-form-paga').html(data['html_pagamento']);
            $('.html-form-recebe').html(data['html_recebimento']);
            $(".html-checklist").show();
            $('.html-form-paga').show();
            $('.html-form-recebe').show();
            verificaTotalHoras();
            mostraChecklist();
            formatUnmask();
            formatMask();
            somaReceitas();
            somaPagamentos();
            verificaCheckboxPaga();
            verificaCheckboxRecebe();
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

// Utilizada no Catd-Minuta
// para atualizar km final da minuta
$(document).on('submit', '#form-edita-km', function(event) {
    event.preventDefault();
    $.ajax({
        type: "POST",
        url: "/minutas/editakmfinal/",
        data: $(this).serialize(),
        beforeSend: function() {
            $(".box-loader").show()
            $(".div-sucesso").hide()
            $(".div-erro").hide()
            $(".html-checklist").hide()
            $('.html-form-paga').hide();
            $('.html-form-recebe').hide();
        },
        success: function(data) {
            if (data.html_tipo_mensagem == 'ERROR') {
                $(".mensagem-erro").text(data.html_mensagem);
                mostraMensagemErro()
            }
            if (data.html_tipo_mensagem == 'SUCESSO') {
                $(".mensagem-sucesso").text(data.html_mensagem);
                mostraMensagemSucesso()
            }
            $(".total-kms").text(data.html_total_kms);
            $('.html-checklist').html(data['html_checklist']); 
            $('.html-form-paga').html(data['html_pagamento']);
            $('.html-form-recebe').html(data['html_recebimento']);
            $(".html-checklist").show();
            $('.html-form-paga').show();
            $('.html-form-recebe').show();
            verificaTotalKMs()
            mostraChecklist();
            formatUnmask();
            formatMask();
            somaReceitas();
            somaPagamentos();
            verificaCheckboxPaga();
            verificaCheckboxRecebe();
            $(".box-loader").hide();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

// Utilizado no Card-Pagamentos
// Mudança de estado do checkbox
$(document).on('change', '.js-checkbox-paga', function() {
    var div_mostra = $(this).attr('id').replace("check", "#js");
    var visible = $(div_mostra).is(':visible')
    var input_tabela = $(this).attr('id').replace("check", "#tabela");
    var input_valor = $(this).attr('id').replace("check", "#valor");
    $(div_mostra).slideToggle(500)
    if (visible) {
        $(input_valor).val('0,00')
    } else {
        var valor_digitado = $(input_tabela).val()
        calculosMudarInputPaga(input_tabela.replace("#", ""), valor_digitado)
        $(input_tabela).select()
    }
    somaPagamentos();
})

// Utilizado no Card-Receitas
// Mudança de estado do checkbox
$(document).on('change', '.js-checkbox-recebe', function() {
    var div_mostra = $(this).attr('id').replace("check", "#js");
    var visible = $(div_mostra).is(':visible')
    var input_tabela = $(this).attr('id').replace("check", "#tabela");
    var input_valor = $(this).attr('id').replace("check", "#valor");
    $(div_mostra).slideToggle(500)
    if (visible) {
        $(input_valor).val('0,00')
    } else {
        var valor_digitado = $(input_tabela).val()
        calculosMudarInputRecebe(input_tabela.replace("#", ""), valor_digitado)
        $(input_tabela).select()
    }
    somaReceitas();
})


// Utilizado no Card-Receitas e no Card-Pagamentos
// ao mudar qualquer input com a class js-input-change
$(document).on('change', '.js-input-change', function() {
    // Cria as variaveis como o nome do atributo e com valor 0
    var element_select = $(this).attr('name')
    var valor_digitado = '0,00'
        // Verifica se o valor do elemento e inteiro se for acrescenta o ',00' ao final - Bug do plugin mask e altera a
        // variavel valor_digitado
    if ($(this).val() % 1 === 0) {
        if ($(this).hasClass("js-decimal")) {
            valor_digitado = $(this).val() + ',00'
            $(this).val(valor_digitado)
        }
    } else {
        valor_digitado = $(this).val()
    }
    calculosMudarInputRecebe(element_select, valor_digitado)
    calculosMudarInputPaga(element_select, valor_digitado)
})

// Card Entregas e Card Romaneio
$(document).on('click', '.js-remove-romaneio-minuta', function() {
    var romaneio = $(this).data('romaneio')
    var idminuta = $(this).data('idminuta')
    var idcliente = $(this).data('idcliente')
    $.ajax({
        type: 'GET',
        url: '/minutas/remove_romaneio_minuta',
        data: {
            romaneio: romaneio,
            idminuta: idminuta,
            idcliente: idcliente,
        },
        beforeSend: function() {
            $('.card-entrega').hide()
            $('.card-romaneio').hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $('.card-entrega').html(data['html_entrega'])
            $('.card-entrega').show()
            $('.card-romaneio').html(data['html_romaneio'])
            $('.card-romaneio').show()
            $(".box-loader").hide()
        },
    });
});

// Mostra a div de mensagem com a mensagem de erro
function mostraMensagemErro() {
    $(".div-erro").slideDown(500)
    $(".div-erro").delay(5000).slideUp(500)
}

// Mostra a div de mensagem com a mensagem de sucesso
function mostraMensagemSucesso() {
    $(".div-sucesso").slideDown(500)
    $(".div-sucesso").delay(5000).slideUp(500)
}

// TODO VERIFICAR NECESSIDADE E APRIMORAR SE NECESSÁRIO
function recarregaFinanceiro(html_paga, html_recebe) {
    $('.html-form-paga').html(html_paga);
    $('.html-form-recebe').html(html_recebe);
    formatUnmask();
    formatMask();
    somaReceitas();
    somaPagamentos();
    verificaCheckboxPaga();
    verificaCheckboxRecebe();
}

// Utilizada no Card-Pagamentps
// Soma valor do motorista
function somaMotorista() {
    var valor_paga = 0.00;
    $(".total-paga").each(function() {
        if ($(this).attr("id") != "valor-ajudante-paga") {
            valor_paga += parseFloat($(this).val().replace('.', '').replace(',', '.'))
        }
    });
    $("#total-motorista").text(valor_paga.toFixed(2))
    if (valor_paga > 0) {
        $(".div-motorista").slideDown(500)
    } else {
        $(".div-motorista").slideUp(500)
    }
    $("#total-motorista").unmask()
    $("#total-motorista").mask('#.##0,00', { reverse: true })
    var text_total = $("#total-motorista").text();
    var text_total = "R$ " + text_total
    $("#total-motorista").text(text_total)
}

// Utilizada no Card-Pagamentos
// Soma total dos pagamentos
function somaPagamentos() {
    var valor_paga = 0.00;
    $(".total-paga").each(function() {
        valor_paga += parseFloat($(this).val().replace('.', '').replace(',', '.'))
    });
    $("#total-pagamentos").text(valor_paga.toFixed(2))
    $("#total-pagamentos").unmask()
    $("#total-pagamentos").mask('#.##0,00', { reverse: true })
    var text_total = $("#total-pagamentos").text();
    var text_total = "TOTAL R$ " + text_total
    $("#total-pagamentos").text(text_total)
    somaMotorista();
}

// Utilizada no Card-Receitas
// Soma total das receitas
function somaReceitas() {
    var valor_recebe = 0.00;
    $(".total-recebe").each(function() {
        valor_recebe += parseFloat($(this).val().replace('.', '').replace(',', '.'))
    });
    $("#total-receitas").text(valor_recebe.toFixed(2))
    $("#total-receitas").unmask()
    $("#total-receitas").mask('#.##0,00', { reverse: true })
    var text_total = $("#total-receitas").text();
    var text_total = "TOTAL R$ " + text_total
    $("#total-receitas").text(text_total)
}

// Utilizado no Card-Pagamentos
// Mostra inputs dos itens de acordo com o estado do checkbox
function verificaCheckboxPaga() {
    $('.total-paga').each(function() {
        check_altera = $(this).attr("name").replace("valor", "#check");
        div_mostra = $(this).attr("name").replace("valor", "#js");
        if (parseFloat($(this).val()) > parseFloat(0,00)) {
            $(check_altera).prop('checked', true)
            $(div_mostra).slideDown(500)
        } else {
            $(check_altera).prop('checked', false)
            $(div_mostra).slideUp(500)
        }
    });
};

// Utilizado no Card-Pagamentos
// Mostra inputs dos itens de acordo com o estado do checkbox
function verificaCheckboxRecebe() {
    $('.total-recebe').each(function() {
        check_altera = $(this).attr("name").replace("valor", "#check");
        div_mostra = $(this).attr("name").replace("valor", "#js");
        if (parseFloat($(this).val()) > parseFloat(0,00)) {
            $(check_altera).prop('checked', true)
            $(div_mostra).slideDown(500)
        } else {
            $(check_altera).prop('checked', false)
            $(div_mostra).slideUp(500)
        }
    });
};

// Utilizada no Card-Minuta
// Mostrra o calculo de horas
function verificaTotalHoras() {
    if ($(".total-horas").text() == '00:00 Hs') {
        $(".calcula-horas").hide()
        $('#id_HoraFinal').val('00:00')
    } else {
        $(".calcula-horas").show()
    }
}

// Utilizada no Card-Minuta
// Mostrra o calculo de Kms
function verificaTotalKMs() {
    if ($(".total-kms").text() == '0 KMs') {
        $(".calcula-kms").hide()
        $('#id_KMFinal').val(0)
    } else {
        $(".calcula-kms").show()
    }
}