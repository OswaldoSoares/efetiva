$(document).ready(function() {
    /* Versão Nova */
    $(document).on('submit', '#form-edita-hora', function(event) {
        event.preventDefault();
        $(".div-sucesso").hide()
        $(".div-erro").hide()
        var url = $(this).attr('action') || action;
        $.ajax({
            type: $(this).attr('method'),
            url: url,
            data: $(this).serialize(),
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
                verificaTotalHoras();
                recarregaFinanceiro(data['html_pagamento'], data['html_recebimento'])
                escondeChecklist();
                $('.html-checklist').html(data['html_checklist']);
                mostraChecklist();
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    /* Versão Nova */
    $(document).on('submit', '#form-edita-km', function(event) {
        event.preventDefault();
        $(".div-sucesso").hide()
        $(".div-erro").hide()
        var url = $(this).attr('action') || action;
        $.ajax({
            type: $(this).attr('method'),
            url: url,
            data: $(this).serialize(),
            success: function(data) {
                if (data.html_tipo_mensagem == 'ERROR') {
                    $(".mensagem-erro").text(data.html_mensagem);
                    mostraMensagemErro()
                }
                if (data.html_tipo_mensagem == 'SUCESSO') {
                    $(".mensagem-sucesso").text(data.html_mensagem);
                    mostraMensagemSucesso()
                }
                recarregaFinanceiro(data['html_pagamento'], data['html_recebimento'])
                escondeChecklist();
                $('.html-checklist').html(data['html_checklist']);
                mostraChecklist();
                $(".total-kms").text(data.html_total_kms);
                verificaTotalKMs()
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    /* Versão Nova */
    $(document).on('submit', '#form-gera-paga', function(event) {
        verificaTotalZero();
        $(".container").hide()
        event.preventDefault();
        var url = $(this).attr('action') || action;
        $.ajax({
            type: $(this).attr('method'),
            url: url,
            data: $(this).serialize(),
            success: function(data) {
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
                escondeChecklist()
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
                escondeChecklist();
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
                escondeChecklist();
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
                escondeChecklist();
                $('.html-checklist').html(data['html_checklist']);
                mostraChecklist();
                EscondeEntrega()
                $('.js-entrega').html(data['html_entrega']);
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

    // Versão Nova - Cadastra Entrega (Form) //
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

    // Versão Nova - Cadastra Entrega (Form) //
    $(document).on('click', '#chk-saida', function(event) {
        if ($('#chk-saida').is(":checked")) {
            $('#id_Nota').val($('#label-chk-saida').attr('saida'))
            $('#id_ValorNota').focus();
        } else {
            $('#id_Nota').val('')
            $('#id_Nota').focus();
        }
    });

    $(document).on('change', '.c_paga', function() {
        var checkbox_change = $(this).attr('id').substring(7)
        var visible = $('#form-paga-' + checkbox_change).is(':visible')
        $('#form-paga-' + checkbox_change).fadeToggle(500)
        if (visible) {
            $('#t_paga_' + checkbox_change).text('0,00')}
    })

    // Versão Nova //
    // Ao modificar um checkbox //
    $(document).on('change', '.c_recebe', function() {
        var checkbox_change = $(this).attr('id').substring(9)
        var visible = $('#form-recebe-' + checkbox_change).is(':visible')
        $('#form-recebe-' + checkbox_change).fadeToggle(500)
        if (visible) {
            $('#t_recebe_' + checkbox_change).val('0,00')
            somaReceita();
        } else {
            var valor_digitado = $('#v_' + checkbox_change).val()
            verificaElemento('v_' + checkbox_change, valor_digitado)
            $('#v_' + checkbox_change).select()
        }
    })

    $(document).on('change', '.js-input-change', function() {
        // Cria as variaveis como o nome do atributo e com valor 0
        var element_select = $(this).attr('name')
        var valor_digitado = '0,00'
            // Verifica se o valor do elemento e inteiro se for acrescenta o ',00' ao final - Bug do plugin mask e altera a
            // variavel valor_digitado
        if ($(this).val() % 1 === 0) {
            valor_digitado = $(this).val() + ',00'
            $(this).val(valor_digitado)
        } else {
            valor_digitado = $(this).val()
        }
        verificaElemento(element_select, valor_digitado)
    })

    verificaSwitchPaga();
    verificaSwitchRecebe();
    mostraChecklist();
    formatMask();

});

function filtroMenuSelecionado(item) {
    alert($(item).attr('class'))
    $(item).removeClass('i-button')
    alert($(item).attr('class'))
}

function verificaElemento(element_select, valor_digitado) {
    function calculaPorcentagem(v_porcentagem, v_valor) {
        var valor1 = parseFloat(v_porcentagem.replace('.', '').replace(',', '.')) / 100
        var valor2 = parseFloat(v_valor.replace('.', '').replace(',', '.'))
        var valor3 = (valor1 * valor2).toFixed(2)

        return valor3
    }

    function calculaMultiplo(v_valor1, v_valor2) {
        var valor1 = parseFloat(v_valor1.replace('.', '').replace(',', '.'))
        var valor2 = parseFloat(v_valor2.replace('.', '').replace(',', '.'))
        var valor3 = (valor1 * valor2).toFixed(2)

        return valor3
    }

    function calculaHora(v_porcentagem, v_valor1, v_hora) {
        var horas = v_hora.substring(0, 2)
        var minutos = v_hora.substring(3, 5)
        var valor_hora = (parseFloat(v_porcentagem.replace('.', '').replace(',', '.')) / 100 * parseFloat(v_valor1.replace('.', '').replace(',', '.')))
        var valor_minuto = (valor_hora / 60)
        var valor_total = ((valor_hora * horas) + (valor_minuto * minutos)).toFixed(2)

        return (valor_total)
    }
    // verifica o elemento e realiza as operações, quando necessárias para retornar o total
    if (element_select == 'v_taxa') {
        $('#t_recebe_taxa').val(valor_digitado)
    } else if (element_select == 'v_segu' || element_select == 'm_segu') {
        $('#t_recebe_segu').val(calculaPorcentagem($('#v_segu').val(), $('#m_segu').val()))
    } else if (element_select == 'v_porc' || element_select == 'm_porc') {
        $('#t_recebe_porc').val(calculaPorcentagem($('#v_porc').val(), $('#m_porc').val()))
    } else if (element_select == 'v_hora' || element_select == 'm_hora') {
        $('#t_recebe_hora').val(calculaHora('100', $('#v_hora').val(), $('#m_hora').val()))
    } else if (element_select == 'v_exce' || element_select == 'm_exce') {
        $('#t_recebe_exce').val(calculaHora($('#v_exce').val(), $('#v_hora').val(), $('#m_exce').val()))
    } else if (element_select == 'v_kilm' || element_select == 'm_kilm') {
        $('#t_recebe_kilm').val(calculaMultiplo($('#v_kilm').val(), $('#m_kilm').val()))
    } else if (element_select == 'v_entr' || element_select == 'm_entr') {
        $('#t_recebe_entr').val(calculaMultiplo($('#v_entr').val(), $('#m_entr').val()))
    } else if (element_select == 'v_enkg' || element_select == 'm_enkg') {
        $('#t_recebe_enkg').val(calculaMultiplo($('#v_enkg').val(), $('#m_enkg').val()))
    } else if (element_select == 'v_evol' || element_select == 'm_evol') {
        $('#t_recebe_evol').val(calculaMultiplo($('#v_evol').val(), $('#m_evol').val()))
    } else if (element_select == 'v_said') {
        $('#t_recebe_said').val(valor_digitado)
    } else if (element_select == 'v_capa') {
        $('#t_recebe_capa').val(valor_digitado)
    } else if (element_select == 'v_peri' || element_select == 'm_peri') {
        $('#t_recebe_peri').val(calculaPorcentagem($('#v_peri').val(), $('#m_peri').val()))
    } else if (element_select == 'v_pnoi' || element_select == 'm_pnoi') {
        $('#t_recebe_pnoi').val(calculaPorcentagem($('#v_pnoi').val(), $('#m_pnoi').val()))
    } else if (element_select == 'v_ajud' || element_select == 'm_ajud') {
        $('#t_recebe_ajud').val(calculaMultiplo($('#v_ajud').val(), $('#m_ajud').val()))
    } else if (element_select.substring(0, 6) == 'v_desp') {
        $('#t_recebe_' + element_select.substring(2)).val(valor_digitado)
    }
    // recarrega mask
    formatUnmask();
    formatMask();
    // Faz a soma geral com os valores atualizados 
    somaReceita();
}

function recarregaFinanceiro(html_paga, html_recebe) {
    $(".html-form-paga").hide(500);
    $(".html-form-recebe").hide(500);
    $('.html-form-paga').html(html_paga);
    $('.html-form-recebe').html(html_recebe);
    formatUnmask();
    formatMask();
    somaReceita();
    $(".html-form-paga").slideDown(500);
    $(".html-form-recebe").slideDown(500);
    verificaSwitchPaga();
    verificaSwitchRecebe();
}

function formatMask() {
    $('#v_taxa').mask('#.##0,00', { reverse: true })
    $('#v_segu').mask('#.##0,000', { reverse: true })
    $('#m_segu').mask('#.##0,00', { reverse: true })
    $('#v_porc').mask('#.##0,00', { reverse: true })
    $('#m_porc').mask('#.##0,00', { reverse: true })
    $('#v_hora').mask('#.##0,00', { reverse: true })
    $('#v_exce').mask('#.##0,00', { reverse: true })
    $('#v_kilm').mask('#.##0,00', { reverse: true })
    $('#m_kilm').mask('#.##0', { reverse: true })
    $('#v_entr').mask('#.##0,00', { reverse: true })
    $('#m_entr').mask('#.##0', { reverse: true })
    $('#v_enkg').mask('#.##0,00', { reverse: true })
    $('#m_enkg').mask('#.##0,00', { reverse: true })
    $('#v_evol').mask('#.##0,00', { reverse: true })
    $('#m_evol').mask('#.##0', { reverse: true })
    $('#v_said').mask('#.##0,00', { reverse: true })
    $('#v_capa').mask('#.##0,00', { reverse: true })
    $('#v_peri').mask('#.##0,00', { reverse: true })
    $('#m_peri').mask('#.##0,00', { reverse: true })
    $('#v_pnoi').mask('#.##0,00', { reverse: true })
    $('#m_pnoi').mask('#.##0,00', { reverse: true })
    $('#v_ajud').mask('#.##0,00', { reverse: true })
    $('#m_ajud').mask('#.##0', { reverse: true })
    $('.v_desp').mask('#.##0,00', { reverse: true })
    $('.total-recebe').mask('#.##0,00', { reverse: true })
    // $("#totalrecebe").mask('#.##0,00', { reverse: true })
}

function formatUnmask() {
    $('#v_taxa').unmask()
    $('#v_segu').unmask()
    $('#m_segu').unmask()
    $('#v_porc').unmask()
    $('#m_porc').unmask()
    $('#v_hora').unmask()
    $('#v_exce').unmask()
    $('#v_kilm').unmask()
    $('#m_kilm').unmask()
    $('#v_entr').unmask()
    $('#m_entr').unmask()
    $('#v_enkg').unmask()
    $('#m_enkg').unmask()
    $('#v_evol').unmask()
    $('#m_evol').unmask()
    $('#v_said').unmask()
    $('#v_capa').unmask()
    $('#v_peri').unmask()
    $('#m_peri').unmask()
    $('#v_pnoi').unmask()
    $('#m_pnoi').unmask()
    $('#v_ajud').unmask()
    $('#m_ajud').unmask()
    $('#v_desp').unmask()
    $('.total-recebe').unmask()
    // $("#totalrecebe").unmask()
}


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
                    escondeChecklist();
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
                        $('.js-entrega').html(xhr['html_entrega']);
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

// Apenas roda na versão mais nova do financeiro
var somaReceita = function() {
    var valor_receita = 0.00;
    $(".total-recebe").each(function() {
        valor_receita += parseFloat($(this).val().replace('.', '').replace(',', '.'))
    });
    $("#totalrecebe").text(valor_receita.toFixed(2))
    $("#totalrecebe").unmask()
    $("#totalrecebe").mask('#.##0,00', { reverse: true })
    var text_total = $("#totalrecebe").text();
    var text_total = "TOTAL R$ " + text_total
    $("#totalrecebe").text(text_total)
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

function verificaSwitchPaga() {
    if ($('#c_paga_porc').is(':not(:checked)')) {
        $('#form-paga-porc').slideUp(500)
    }
    if ($('#c_paga_hora').is(':not(:checked)')) {
        $('#form-paga-hora').slideUp(500)
    }
    if ($('#c_paga_exce').is(':not(:checked)')) {
        $('#form-paga-exce').slideUp(500)
    }
    if ($('#c_paga_kilm').is(':not(:checked)')) {
        $('#form-paga-kilm').slideUp(500)
    }
    if ($('#c_paga_entr').is(':not(:checked)')) {
        $('#form-paga-entr').slideUp(500)
    }
    if ($('#c_paga_enkg').is(':not(:checked)')) {
        $('#form-paga-enkg').slideUp(500)
    }
    if ($('#c_paga_evol').is(':not(:checked)')) {
        $('#form-paga-evol').slideUp(500)
    }
    if ($('#c_paga_said').is(':not(:checked)')) {
        $('#form-paga-said').slideUp(500)
    }
    if ($('#c_paga_capa').is(':not(:checked)')) {
        $('#form-paga-capa').slideUp(500)
    }
    if ($('#c_paga_peri').is(':not(:checked)')) {
        $('#form-paga-peri').slideUp(500)
    }
    if ($('#c_paga_pnoi').is(':not(:checked)')) {
        $('#form-paga-pnoi').slideUp(500)
    }
    if ($('#c_paga_ajud').is(':not(:checked)')) {
        $('#form-paga-ajud').slideUp(500)
    }
};

function verificaSwitchRecebe() {
    if ($('#c_recebe_taxa').is(':not(:checked)')) {
        $('#form-recebe-taxa').slideUp(500)
    }
    if ($('#c_recebe_segu').is(':not(:checked)')) {
        $('#form-recebe-segu').slideUp(500)
    }
    if ($('#c_recebe_porc').is(':not(:checked)')) {
        $('#form-recebe-porc').slideUp(500)
    }
    if ($('#c_recebe_hora').is(':not(:checked)')) {
        $('#form-recebe-hora').slideUp(500)
    }
    if ($('#c_recebe_exce').is(':not(:checked)')) {
        $('#form-recebe-exce').slideUp(500)
    }
    if ($('#c_recebe_kilm').is(':not(:checked)')) {
        $('#form-recebe-kilm').slideUp(500)
    }
    if ($('#c_recebe_entr').is(':not(:checked)')) {
        $('#form-recebe-entr').slideUp(500)
    }
    if ($('#c_recebe_enkg').is(':not(:checked)')) {
        $('#form-recebe-enkg').slideUp(500)
    }
    if ($('#c_recebe_evol').is(':not(:checked)')) {
        $('#form-recebe-evol').slideUp(500)
    }
    if ($('#c_recebe_said').is(':not(:checked)')) {
        $('#form-recebe-said').slideUp(500)
    }
    if ($('#c_recebe_capa').is(':not(:checked)')) {
        $('#form-recebe-capa').slideUp(500)
    }
    if ($('#c_recebe_peri').is(':not(:checked)')) {
        $('#form-recebe-peri').slideUp(500)
    }
    if ($('#c_recebe_pnoi').is(':not(:checked)')) {
        $('#form-recebe-pnoi').slideUp(500)
    }
    if ($('#c_recebe_ajud').is(':not(:checked)')) {
        $('#form-recebe-ajud').slideUp(500)
    }
};

function verificaTotalZero() {
    if ($('#t_recebe_taxa').val() == 0.00) {
        $('#c_recebe_taxa').prop('checked', false)
    }
    if ($('#t_recebe_segu').val() == 0.00) {
        $('#c_recebe_segu').prop('checked', false)
    }
    if ($('#t_recebe_porc').val() == 0.00) {
        $('#c_recebe_porc').prop('checked', false)
    }
    if ($('#t_recebe_hora').val() == 0.00) {
        $('#c_recebe_hora').prop('checked', false)
    }
    if ($('#t_recebe_exce').val() == 0.00) {
        $('#c_recebe_exce').prop('checked', false)
    }
    if ($('#t_recebe_kilm').val() == 0.00) {
        $('#c_recebe_kilm').prop('checked', false)
    }
    if ($('#t_recebe_entr').val() == 0.00) {
        $('#c_recebe_entr').prop('checked', false)
    }
    if ($('#t_recebe_enkg').val() == 0.00) {
        $('#c_recebe_enkg').prop('checked', false)
    }
    if ($('#t_recebe_evol').val() == 0.00) {
        $('#c_recebe_evol').prop('checked', false)
    }
    if ($('#t_recebe_said').val() == 0.00) {
        $('#c_recebe_said').prop('checked', false)
    }
    if ($('#t_recebe_capa').val() == 0.00) {
        $('#c_recebe_capa').prop('checked', false)
    }
    if ($('#t_recebe_peri').val() == 0.00) {
        $('#c_recebe_peri').prop('checked', false)
    }
    if ($('#t_recebe_pnoi').val() == 0.00) {
        $('#c_recebe_pnoi').prop('checked', false)
    }
    if ($('#t_recebe_ajud').val() == 0.00) {
        $('#c_recebe_ajud').prop('checked', false)
    }
    verificaSwitchRecebe();
    if ($('#t_paga_porc').text() == 0.00) {
        $('#c_paga_porc').prop('checked', false)
    }
    if ($('#t_paga_hora').text() == 0.00) {
        $('#_pagac_hora').prop('checked', false)
    }
    if ($('#t_paga_exce').text() == 0.00) {
        $('#c_paga_exce').prop('checked', false)
    }
    if ($('#t_paga_kilm').text() == 0.00) {
        $('#c_paga_kilm').prop('checked', false)
    }
    if ($('#t_paga_entr').text() == 0.00) {
        $('#c_paga_entr').prop('checked', false)
    }
    if ($('#t_paga_enkg').text() == 0.00) {
        $('#c_paga_enkg').prop('checked', false)
    }
    if ($('#t_paga_evol').text() == 0.00) {
        $('#c_paga_evol').prop('checked', false)
    }
    if ($('#t_paga_said').text() == 0.00) {
        $('#c_paga_said').prop('checked', false)
    }
    if ($('#t_paga_capa').text() == 0.00) {
        $('#c_paga_capa').prop('checked', false)
    }
    if ($('#t_paga_peri').text() == 0.00) {
        $('#c_paga_peri').prop('checked', false)
    }
    if ($('#t_paga_pnoi').text() == 0.00) {
        $('#c_paga_pnoi').prop('checked', false)
    }
    if ($('#t_paga_ajud').text() == 0.00) {
        $('#c_paga_ajud').prop('checked', false)
    }
    verificaSwitchPaga();
};

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
    $(".js-entrega").hide()
}

var MostraEntrega = function() {
    $(".js-entrega").delay(1000).slideDown(500)
}

var escondeChecklist = function() {
    $(".html-checklist").hide()
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

// Versão Nova //
$(document).on('click', '.js-adiciona-romaneio-minuta', function() {
    var _id_romaneio = $(this).data('idromaneio')
    var _id_minuta = $(this).data('idminuta')
    $.ajax({
        type: 'GET',
        url: '/minutas/adiciona_romaneio_minuta',
        data: {
            idRomaneio: _id_romaneio,
            idMinuta: _id_minuta,
        },
        beforeSend: function() {
            $('.js-entrega').hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $('.js-entrega').html(data['html_entrega'])
            $('.js-entrega').show()
            $(".box-loader").hide()
        },
    });
});