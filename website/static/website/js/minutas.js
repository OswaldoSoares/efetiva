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

    $('.switch').each(function(index) {
        if ($(this).is(":checked")) {
            var switch_id = $(this).attr('id');
            var tr_id = '#' + switch_id.replace('sw','tr')
            var mr_id = '#' + switch_id.replace('sw','mr')
            var to_id = '#' + switch_id.replace('sw','to')
            var hi_id = '#' + switch_id.replace('sw','hi')

            $(hi_id).val($(tr_id).val())
            $(to_id).text($(tr_id).val())
//          console.log( index + ": " + $(this).attr('checked') + " - " + switch_id + " - " + to_id );
            console.log( index + ': ' + tr_id + ' - ' + mr_id + ' - ' + to_id + ' - ' + hi_id );
        }
    });


//    // TAXA DE EXPEDIÇÃO
//    var switchTaxaExpedicaoRecebe = function(){
//        if ($("#sw-taxaexpedicao-recebe").is(":checked")) {
//                var valorTaxaExpedicaoRecebe = ($("#tb-taxaexpedicao-recebe").val() * 1).toFixed(2)
//            } else {
//                var valorTaxaExpedicaoRecebe = (0.00).toFixed(2)
//            }
//            $("#tl-taxaexpedicao-recebe").text('R$ ' + valorTaxaExpedicaoRecebe.replace('.',','))
//            $("#hi-taxaexpedicao-recebe").val(valorTaxaExpedicaoRecebe)
//    }
//    // Altera TAXA DE EXPEDIÇÃO
//    $(".change-taxaexpedicao-recebe").change(function(){
//        switchTaxaExpedicaoRecebe();
//        somaMinutaRecebe();
//        $("#tb-taxaexpedicao-recebe").val(($("#tb-taxaexpedicao-recebe").val()*1).toFixed(2))
//        console.log($("valor-recebe").val())
//    });
//    // SEGURO
//    var switchSeguroRecebe = function() {
//        console.log('SIM - SEGURO')
//        if ($("#sw-seguro-recebe").is(":checked")) {
//            var valorSeguroRecebe = ($("#tb-seguro-recebe").val() * $("#fa-seguro-recebe").val() / 100).toFixed(2)
//        } else {
//            var valorSeguroRecebe = (0.00).toFixed(2)
//        }
//        $("#tl-seguro-recebe").text('R$ ' + valorSeguroRecebe.replace('.',','))
//        $("#hi-seguro-recebe").val(valorSeguroRecebe)
//    }
//    // Altera SEGURO
//    $(".change-seguro-recebe").change(function(){
//        switchSeguroRecebe();
//        somaMinutaRecebe();
//        $("#tb-seguro-recebe").val(($("#tb-seguro-recebe").val()*1).toFixed(1))
//        $("#fa-seguro-recebe").val(($("#fa-seguro-recebe").val()*1).toFixed(2))
//    });
//    // PORCENTAGEM RECEBE
//    var switchPorcentagemRecebe = function(){
//        if ($("#sw-porcentagem-recebe").is(":checked")) {
//                var valorPorcentagemRecebe = ($("#tb-porcentagem-recebe").val() * $("#fa-porcentagem-recebe").val() / 100).toFixed(2)
//            } else{
//                var valorPorcentagemRecebe = (0.00).toFixed(2)
//            }
//            $("#tl-porcentagem-recebe").text('R$ ' + valorPorcentagemRecebe.replace('.',','))
//            $("#hi-porcentagem-recebe").val(valorPorcentagemRecebe)
//
//    }
//    // Altera PORCENTAGEM RECEBE
//    $(".change-porcentagem-recebe").change(function(){
//        switchPorcentagemRecebe();
//        somaMinutaRecebe();
//        $("#tb-porcentagem-recebe").val(($("#tb-porcentagem-recebe").val()*1).toFixed(1))
//        $("#fa-porcentagem-recebe").val(($("#fa-porcentagem-recebe").val()*1).toFixed(2))
//    });
//    // PORCENTAGEM PAGA
//    var switchPorcentagemPaga = function(){
//        if ($("#sw-porcentagem-paga").is(":checked")) {
//                var valorPorcentagemPaga = ($("#tb-porcentagem-paga").val() * $("#fa-porcentagem-paga").val() / 100).toFixed(2)
//            } else{
//                var valorPorcentagemPaga = (0.00).toFixed(2)
//            }
//            $("#tl-porcentagem-paga").text('R$ ' + valorPorcentagemPaga.replace('.',','))
//            $("#hi-porcentagem-paga").val(valorPorcentagemPaga)
//    }
//    // Altera PORCENTAGEM PAGA
//    $(".change-porcentagem-paga").change(function(){
//        switchPorcentagemPaga();
//        somaMinutaPaga();
//        $("#tb-porcentagem-paga").val(($("#tb-porcentagem-paga").val()*1).toFixed(1))
//        $("#fa-porcentagem-paga").val(($("#fa-porcentagem-paga").val()*1).toFixed(2))
//    });
//    // HORA RECEBE
//    var switchHoraRecebe = function(){
//        if ($("#sw-hora-recebe").is(":checked")) {
//            var valorHora = $("#tb-hora-recebe").val()
//            var horas = $("#fa-hora-recebe").val().substring(0,2);
//            var minutos = $("#fa-hora-recebe").val().substring(3,5);
//            totalHora = horas * valorHora
//            totalMinuto = minutos * (valorHora/60).toFixed(5)
//            totalHoraRecebe = totalHora + totalMinuto
//            var valorHoraRecebe = (totalHoraRecebe).toFixed(2)
//        } else {
//            var valorHoraRecebe = (0.00).toFixed(2)
//        }
//        $("#tl-hora-recebe").text('R$ ' + valorHoraRecebe.replace('.',','))
//        $("#hi-hora-recebe").val(valorHoraRecebe)
//    }
//    // Altera HORA RECEBE
//    $(".change-hora-recebe").change(function(){
//        switchHoraRecebe();
//        somaMinutaRecebe();
//        $("#tb-hora-recebe").val(($("#tb-hora-recebe").val()*1).toFixed(2))
//    });
//    // HORA PAGA
//    var switchHoraPaga = function(){
//        if ($("#sw-hora-paga").is(":checked")) {
//            var valorHora = $("#tb-hora-paga").val()
//            var horas = $("#fa-hora-paga").val().substring(0,2);
//            var minutos = $("#fa-hora-paga").val().substring(3,5);
//            totalHora = horas * valorHora
//            totalMinuto = minutos * (valorHora/60).toFixed(5)
//            totalHoraPaga = totalHora + totalMinuto
//            var valorHoraPaga = (totalHoraPaga).toFixed(2)
//        } else {
//            var valorHoraPaga = (0.00).toFixed(2)
//        }
//        $("#tl-hora-paga").text('R$ ' + valorHoraPaga.replace('.',','))
//        $("#hi-hora-paga").val(valorHoraPaga)
//    }
//    // Altera HORA PAGA
//    $(".change-hora-paga").change(function(){
//        switchHoraPaga();
//        somaMinutaPaga();
//        $("#tb-hora-paga").val(($("#tb-hora-paga").val()*1).toFixed(2))
//    });
//    // HORA EXCEDENTE RECEBE
//    var switchHoraExcedeRecebe = function() {
//        if ($("#sw-horasexcede-recebe").is(":checked")) {
////            var horasExcede = $("#mr-horasexcede-recebe").val().substring(0,2);
////            var minutosExcede = $("#mr-horasexcede-recebe").val().substring(3,5);
////            var valorHorasExcede = $("#tb-hora-recebe").val() * $("#fa-horasexcede-recebe").val() / 100
////            totalHora = horasExcede * valorHorasExcede
////            totalMinuto = minutosExcede * (valorHorasExcede/60).toFixed(5)
////            totalHorasExcedeRecebe = totalHora + totalMinuto
////            var valorHorasExcedeRecebe = (totalHorasExcedeRecebe).toFixed(2)
//        } else {
//            var valorHorasExcedeRecebe = (0.00).toFixed(2)
//        }
////        $("#tl-horasexcede-recebe").text('R$ ' + valorHorasExcedeRecebe.replace('.',','))
////        $("#hi-horasexcede-recebe").val(valorHorasExcedeRecebe)
//    }
//    // Altera HORA EXCEDENTE RECEBE
//    $(".change-horasexcede-recebe").change(function(){
//        switchHoraExcedeRecebe();
//        somaMinutaRecebe();
//        $("#fa-horasexcede-recebe").val(($("#fa-horasexcede-recebe").val()*1).toFixed(1))
//    });
//    // HORA EXCEDENTE PAGA
//    var switchHoraExcedePaga = function() {
//        if ($("#sw-horasexcede-paga").is(":checked")) {
////            var horasExcede = $("#tb-horasexcede-paga").val().substring(0,2);
////            var minutosExcede = $("#tb-horasexcede-paga").val().substring(3,5);
////            var valorHorasExcede = $("#tb-hora-paga").val() * $("#fa-horasexcede-paga").val() / 100
////            totalHora = horasExcede * valorHorasExcede
////            totalMinuto = minutosExcede * (valorHorasExcede/60).toFixed(5)
////            totalHorasExcedePaga = totalHora + totalMinuto
////            var valorHorasExcedePaga = (totalHorasExcedePaga).toFixed(2)
//        } else {
//            var valorHorasExcedePaga = (0.00).toFixed(2)
//        }
////        $("#tl-horasexcede-paga").text('R$ ' + valorHorasExcedePaga.replace('.',','))
////        $("#hi-horasexcede-paga").val(valorHorasExcedePaga)
//    }
//    // Altera HORA EXCEDENTE PAGA
//    $(".change-horasexcede-paga").change(function(){
//        switchHoraExcedePaga();
//        somaMinutaPaga();
//        $("#fa-horasexcede-paga").val(($("#fa-horasexcede-paga").val()*1).toFixed(1))
//    });
//    // KILOMETRAGEM RECEBE
//    switchKmRecebe = function(){
//        if ($("#sw-km-recebe").is(":checked")) {
//            var valorKmRecebe = ($("#tb-km-recebe").val() * $("#fa-km-recebe").val()).toFixed(2)
//        } else {
//            var valorKmRecebe = (0.00).toFixed(2)
//        }
//        $("#tl-km-recebe").text('R$ ' + valorKmRecebe.replace('.',','))
//        $("#hi-km-recebe").val(valorKmRecebe)
//    }
//    // Altera KILOMETRAGEM RECEBE
//    $(".change-km-recebe").change(function(){
//        switchKmRecebe();
//        somaMinutaRecebe();
//        $("#tb-km-recebe").val(($("#tb-km-recebe").val()*1).toFixed(2))
//        $("#fa-km-recebe").val(($("#fa-km-recebe").val()*1).toFixed(0))
//    });
//    // KILOMETRAGEM PAGA
//    switchKmPaga = function(){
//        if ($("#sw-km-paga").is(":checked")) {
//            var valorKmPaga = ($("#tb-km-paga").val() * $("#fa-km-paga").val()).toFixed(2)
//        } else {
//            var valorKmPaga = (0.00).toFixed(2)
//        }
//        $("#tl-km-paga").text('R$ ' + valorKmPaga.replace('.',','))
//        $("#hi-km-paga").val(valorKmPaga)
//    }
//    // Altera KILOMETRAGEM PAGA
//    $(".change-km-paga").change(function(){
//        switchKmPaga();
//        somaMinutaPaga();
//        $("#tb-km-paga").val(($("#tb-km-paga").val()*1).toFixed(2))
//        $("#fa-km-paga").val(($("#fa-km-paga").val()*1).toFixed(0))
//    });
//    // ENTREGA RECEBE
//    switchEntregaRecebe = function(){
//        if ($("#sw-entrega-recebe").is(":checked")) {
//            var valorEntregaRecebe = ($("#tb-entrega-recebe").val() * $("#fa-entrega-recebe").val()).toFixed(2)
//        } else {
//            var valorEntregaRecebe = (0.00).toFixed(2)
//        }
//        $("#tl-entrega-recebe").text('R$ ' + valorEntregaRecebe.replace('.',','))
//        $("#hi-entrega-recebe").val(valorEntregaRecebe)
//    }
//    // Altera ENTREGA RECEBE
//    $(".change-entrega-recebe").change(function(){
//        switchEntregaRecebe();
//        somaMinutaRecebe();
//        $("#tb-entrega-recebe").val(($("#tb-entrega-recebe").val()*1).toFixed(2))
//        $("#fa-entrega-recebe").val(($("#fa-entrega-recebe").val()*1).toFixed(0))
//    });
//    // ENTREGA PAGA
//    switchEntregaPaga = function(){
//        if ($("#sw-entrega-paga").is(":checked")) {
//            var valorEntregaPaga = ($("#tb-entrega-paga").val() * $("#fa-entrega-paga").val()).toFixed(2)
//        } else {
//            var valorEntregaPaga = (0.00).toFixed(2)
//        }
//        $("#tl-entrega-paga").text('R$ ' + valorEntregaPaga.replace('.',','))
//        $("#hi-entrega-paga").val(valorEntregaPaga)
//    }
//    // Altera ENTREGA PAGA
//    $(".change-entrega-paga").change(function(){
//        switchEntregaPaga()
//        somaMinutaPaga()
//        $("#tb-entrega-paga").val(($("#tb-entrega-paga").val()*1).toFixed(2))
//        $("#fa-entrega-paga").val(($("#fa-entrega-paga").val()*1).toFixed(0))
//    });
//    // ENTREGA KG RECEBE
//    var switchEntregaKgRecebe = function(){
//        if ($("#sw-entregakg-recebe").is(":checked")) {
//            var valorEntregaKgRecebe = ($("#tb-entregakg-recebe").val() * $("#fa-entregakg-recebe").val()).toFixed(2)
//        } else {
//            var valorEntregaKgRecebe = (0.00).toFixed(2)
//        }
//        $("#tl-entregakg-recebe").text('R$ ' + valorEntregaKgRecebe.replace('.',','))
//        $("#hi-entregakg-recebe").val(valorEntregaKgRecebe)
//    }
//    // Altera ENTREGA KG RECEBE
//    $(".change-entregakg-recebe").change(function(){
//        switchEntregaKgRecebe();
//        somaMinutaRecebe();
//        $("#tb-entregakg-recebe").val(($("#tb-entregakg-recebe").val()*1).toFixed(2))
//        $("#fa-entregakg-recebe").val(($("#fa-entregakg-recebe").val()*1).toFixed(2))
//    });
//    // ENTREGA KG PAGA
//    var switchEntregaKgPaga = function(){
//        if ($("#sw-entregakg-paga").is(":checked")) {
//            var valorEntregaKgPaga = ($("#tb-entregakg-paga").val() * $("#fa-entregakg-paga").val()).toFixed(2)
//        } else {
//            var valorEntregaKgPaga = (0.00).toFixed(2)
//        }
//        $("#tl-entregakg-paga").text('R$ ' + valorEntregaKgPaga.replace('.',','))
//        $("#hi-entregakg-paga").val(valorEntregaKgPaga)
//    }
//    // Altera ENTREGA KG PAGA
//    $(".change-entregakg-paga").change(function(){
//        switchEntregaKgPaga();
//        somaMinutaPaga();
//        $("#tb-entregakg-paga").val(($("#tb-entregakg-paga").val()*1).toFixed(2))
//        $("#fa-entregakg-paga").val(($("#fa-entregakg-paga").val()*1).toFixed(2))
//    });
//    // ENTREGA VOLUME RECEBE
//    var switchEntregaVolumeRecebe = function(){
//        if ($("#sw-entregavolume-recebe").is(":checked")) {
//            var valorEntregaVolumeRecebe = ($("#tb-entregavolume-recebe").val() * $("#fa-entregavolume-recebe").val()).toFixed(2)
//        } else {
//            var valorEntregaVolumeRecebe = (0.00).toFixed(2)
//        }
//        $("#tl-entregavolume-recebe").text('R$ ' + valorEntregaVolumeRecebe.replace('.',','))
//        $("#hi-entregavolume-recebe").val(valorEntregaVolumeRecebe)
//    }
//    // ALTERA ENTREGA VOLUME RECEBE
//    $(".change-entregavolume-recebe").change(function(){
//        switchEntregaVolumeRecebe();
//        somaMinutaRecebe();
//        $("#tb-entregavolume-recebe").val(($("#tb-entregavolume-recebe").val()*1).toFixed(2))
//        $("#fa-entregavolume-recebe").val(($("#fa-entregavolume-recebe").val()*1).toFixed(0))
//    });
//    // ENTREGA VOLUME PAGA
//    var switchEntregaVolumePaga = function(){
//        if ($("#sw-entregavolume-paga").is(":checked")) {
//            var valorEntregaVolumePaga = ($("#tb-entregavolume-paga").val() * $("#fa-entregavolume-paga").val()).toFixed(2)
//        } else {
//            var valorEntregaVolumePaga = (0.00).toFixed(2)
//        }
//        $("#tl-entregavolume-paga").text('R$ ' + valorEntregaVolumePaga.replace('.',','))
//        $("#hi-entregavolume-paga").val(valorEntregaVolumePaga)
//    }
//    // ALTERA ENTREGA VOLUME PAGA
//    $(".change-entregavolume-paga").change(function(){
//        switchEntregaVolumePaga();
//        somaMinutaPaga();
//        $("#tb-entregavolume-paga").val(($("#tb-entregavolume-paga").val()*1).toFixed(2))
//        $("#fa-entregavolume-paga").val(($("#fa-entregavolume-paga").val()*1).toFixed(0))
//    });
//    // SAIDA RECEBE
//    var switchSaidaRecebe = function(){
//        if ($("#sw-saida-recebe").is(":checked")) {
//            var valorSaidaRecebe = ($("#tb-saida-recebe").val() * 1).toFixed(2)
//        } else {
//            var valorSaidaRecebe = (0.00).toFixed(2)
//        }
//        $("#tl-saida-recebe").text('R$ ' + valorSaidaRecebe.replace('.',','))
//        $("#hi-saida-recebe").val(valorSaidaRecebe)
//    }
//    // Altera SAIDA RECEBE
//    $(".change-saida-recebe").change(function(){
//        switchSaidaRecebe();
//        somaMinutaRecebe();
//        $("#tb-saida-recebe").val(($("#tb-saida-recebe").val()*1).toFixed(2))
//    });
//    // SAIDA PAGA
//    var switchSaidaPaga = function(){
//        if ($("#sw-saida-paga").is(":checked")) {
//            var valorSaidaPaga = ($("#tb-saida-paga").val() * 1).toFixed(2)
//        } else {
//            var valorSaidaPaga = (0.00).toFixed(2)
//        }
//        $("#tl-saida-paga").text('R$ ' + valorSaidaPaga.replace('.',','))
//        $("#hi-saida-paga").val(valorSaidaPaga)
//    }
//    // Altera SAIDA
//    $(".change-saida-paga").change(function(){
//        switchSaidaPaga();
//        somaMinutaPaga();
//        $("#tb-saida-paga").val(($("#tb-saida-paga").val()*1).toFixed(2))
//    });
//    // CAPACIDADE RECEBE
//    var switchCapacidadeRecebe = function(){
//        if ($("#sw-capacidade-recebe").is(":checked")) {
//                var valorCapacidadeRecebe = ($("#tb-capacidade-recebe").val() * 1).toFixed(2)
//            } else {
//                var valorCapacidadeRecebe = (0.00).toFixed(2)
//            }
//            $("#tl-capacidade-recebe").text('R$ ' + valorCapacidadeRecebe.replace('.',','))
//            $("#hi-capacidade-recebe").val(valorCapacidadeRecebe)
//    }
//    // Altera CAPACIDADE RECEBE
//    $(".change-capacidade-recebe").change(function(){
//        switchCapacidadeRecebe();
//        somaMinutaRecebe();
//        $("#tb-capacidade-recebe").val(($("#tb-capacidade-recebe").val()*1).toFixed(2))
//    });
//    // CAPACIDADE PAGA
//    var switchCapacidadePaga = function(){
//        if ($("#sw-capacidade-paga").is(":checked")) {
//                var valorCapacidadePaga = ($("#tb-capacidade-paga").val() * 1).toFixed(2)
//            } else {
//                var valorCapacidadePaga = (0.00).toFixed(2)
//            }
//            $("#tl-capacidade-paga").text('R$ ' + valorCapacidadePaga.replace('.',','))
//            $("#hi-capacidade-paga").val(valorCapacidadePaga)
//    }
//    // Altera CAPACIDADE PAGA
//    $(".change-capacidade-paga").change(function(){
//        switchCapacidadePaga();
//        somaMinutaPaga();
//        $("#tb-capacidade-paga").val(($("#tb-capacidade-paga").val()*1).toFixed(2))
//    });
//    // PERIMETRO
//    // PERNOITE
//    // AJUDANTE RECEBE
//    var switchAjudanteRecebe = function(){
//        if ($("#sw-ajudante-recebe").is(":checked")) {
//            var valorAjudanteRecebe = ($("#tb-ajudante-recebe").val() * $("#fa-ajudante-recebe").val()).toFixed(2)
//        } else {
//            var valorAjudanteRecebe = (0.00).toFixed(2)
//        }
//        $("#tl-ajudante-recebe").text('R$ ' + valorAjudanteRecebe.replace('.',','))
//        $("#hi-ajudante-recebe").val(valorAjudanteRecebe)
//    }
//    // Altera AJUDANTE RECEBE
//    $(".change-ajudante-recebe").change(function(){
//        switchAjudanteRecebe();
//        somaMinutaRecebe();
//        $("#tb-ajudante-recebe").val(($("#tb-ajudante-recebe").val()*1).toFixed(2))
//        $("#fa-ajudante-recebe").val(($("#fa-ajudante-recebe").val()*1).toFixed(0))
//    });
//    // AJUDANTE PAGA
//    var switchAjudantePaga = function(){
//        if ($("#sw-ajudante-paga").is(":checked")) {
//            var valorAjudantePaga = ($("#tb-ajudante-paga").val() * $("#fa-ajudante-paga").val()).toFixed(2)
//        } else {
//            var valorAjudantePaga = (0.00).toFixed(2)
//        }
//        $("#tl-ajudante-paga").text('R$ ' + valorAjudantePaga.replace('.',','))
//        $("#hi-ajudante-paga").val(valorAjudantePaga)
//    }
//    // Altera AJUDANTE PAGA
//    $(".change-ajudante-paga").change(function(){
//        switchAjudantePaga();
//        somaMinutaPaga();
//        $("#tb-ajudante-paga").val(($("#tb-ajudante-paga").val()*1).toFixed(2))
//    });
//    // DESCONTO
//    var switchDescontoRecebe = function(){
//        if ($("#sw-desconto-recebe").is(":checked")) {
//            var valorDescontoRecebe = ($("#tb-desconto-recebe").val() - ($("#tb-desconto-recebe").val() * 2)).toFixed(2)
//        } else {
//            var valorDescontoRecebe = (0.00).toFixed(2)
//        }
//        $("#tl-desconto-recebe").text('R$ ' + valorDescontoRecebe.replace('.',','))
//        $("#hi-desconto-recebe").val(valorDescontoRecebe)
//    }
//    // Altera DESCONTO
//    $(".change-desconto-recebe").change(function(){
//        switchDescontoRecebe();
//        somaMinutaRecebe();
//        $("#tb-desconto-recebe").val(($("#tb-desconto-recebe").val()*1).toFixed(2))
//    });
//    // DESPESAS RECEBE
//    var despesaRecebe = function(){
//        $(".hi-despesa-recebe").each(function(){
//            tlDespesaRecebe = '#'+$(this).attr('id').replace('hi','tl')
//            $(this).val(parseFloat($(tlDespesaRecebe).text().substring(3,12).replace(',','.')))
//        });
//    };
//    $(".switch-despesa-recebe").change(function(){
//        console.log('OK')
//        tbDespesaRecebe = '#'+$(this).attr('id').replace('sw','tb')
//        tlDespesaRecebe = '#'+$(this).attr('id').replace('sw','tl')
//        hiDespesaRecebe = '#'+$(this).attr('id').replace('sw','hi')
//        console.log(hiDespesaRecebe)
//        if ($(this).is(":checked")) {
//            $(tlDespesaRecebe).text('R$ ' + ($(tbDespesaRecebe).val()*1).toFixed(2).replace('.',','))
//            $(hiDespesaRecebe).val($(tbDespesaRecebe).val())
//        } else {
//            $(tlDespesaRecebe).text('R$ 0,00')
//            $(hiDespesaRecebe).val(0.00)
//        }
//        somaMinutaRecebe();
//    });
//    $(".tb-despesa-recebe").change(function(){
//        swDespesaRecebe = '#'+$(this).attr('id').replace('tb','sw')
//        tlDespesaRecebe = '#'+$(this).attr('id').replace('tb','tl')
//        hiDespesaRecebe = '#'+$(this).attr('id').replace('tb','hi')
//        if ($(swDespesaRecebe).is(":checked")) {
//            $(tlDespesaRecebe).text('R$ ' + ($(this).val()*1).toFixed(2).replace('.',','))
//            $(hiDespesaRecebe).val($(this).val())
//        } else {
//            $(tlDespesaRecebe).text('R$ 0,00')
//            $(hiDespesaRecebe).val(0.00)
//        }
//        $(this).val(($(this).val()*1).toFixed(2))
//        somaMinutaRecebe();
//    });
//    // DESPESAS PAGA
//    var despesaPaga = function(){
//        $(".hi-despesa-paga").each(function(){
//            tlDespesaPaga = '#'+$(this).attr('id').replace('hi','tl')
//            $(this).val(parseFloat($(tlDespesaPaga).text().substring(3,12).replace(',','.')))
//        });
//    };
//    $(".switch-despesa-paga").change(function(){
//        tbDespesaPaga = '#'+$(this).attr('id').replace('sw','tb')
//        tlDespesaPaga = '#'+$(this).attr('id').replace('sw','tl')
//        hiDespesaPaga = '#'+$(this).attr('id').replace('sw','hi')
//        if ($(this).is(":checked")) {
//            $(tlDespesaPaga).text('R$ ' + ($(tbDespesaPaga).val()*1).toFixed(2).replace('.',','))
//            $(hiDespesaPaga).val($(tbDespesaPaga).val())
//        } else {
//            $(tlDespesaPaga).text('R$ 0,00')
//            $(hiDespesaPaga).val(0.00)
//        }
//        somaMinutaPaga();
//    });
//    $(".tb-despesa-paga").change(function(){
//        swDespesaPaga = '#'+$(this).attr('id').replace('tb','sw')
//        tlDespesaPaga = '#'+$(this).attr('id').replace('tb','tl')
//        hiDespesaPaga = '#'+$(this).attr('id').replace('tb','hi')
//        if ($(swDespesaPaga).is(":checked")) {
//            $(tlDespesaPaga).text('R$ ' + ($(this).val()*1).toFixed(2).replace('.',','))
//            $(hiDespesaPaga).val($(this).val())
//        } else {
//            $(tlDespesaPaga).text('R$ 0,00')
//            $(hiDespesaPaga).val(0.00)
//        }
//        $(this).val(($(this).val()*1).toFixed(2))
//        somaMinutaPaga();
//    });
//    // SOMA MINUTA RECEBE
//    var somaMinutaRecebe = function(){
//        totalRecebe = 0
//        $(".tl-despesa-recebe").each(function(){
//            totalRecebe = totalRecebe + parseFloat($(this).text().substring(3,12).replace(',','.'))
//        });
//        $("#totalrecebe").text('R$ ' + totalRecebe.toFixed(2).replace('.',','))
//        saldoMinuta();
//    };
//    // SOMA MINUTA PAGA
//    var somaMinutaPaga = function(){
//        totalPaga = 0
//        $(".tl-despesa-paga").each(function(){
//            totalPaga = totalPaga + parseFloat($(this).text().substring(3,12).replace(',','.'))
//        });
//        $("#totalpaga").text('R$ ' + totalPaga.toFixed(2).replace('.',','))
//        saldoMinuta();
//    };
//    // SALDO MINUTA
//    var saldoMinuta = function(){
//        var totalSaldoMinuta = parseFloat($("#totalrecebe").text().substring(3,12).replace(',','.')) -
//                                parseFloat($("#totalpaga").text().substring(3,12).replace(',','.'))
//        $(".saldo-minuta").text('Saldo da Minuta R$ ' + totalSaldoMinuta.toFixed(2).replace('.',','))
//    };
//
//    var valorRecebe = function(){
//        $(".valor-recebe").each(function(){
//            tlvalorRecebe = '#'+$(this).attr('id').replace('hi','tl')
//            $(this).val(parseFloat($(tlvalorRecebe).text().substring(3,12).replace(',','.')))
//        });
//    };
//
//    var valorPaga = function(){
//        $(".valor-paga").each(function(){
//            tlvalorPaga = '#'+$(this).attr('id').replace('hi','tl')
//            $(this).val(parseFloat($(tlvalorPaga).text().substring(3,12).replace(',','.')))
//        });
//    };
//
//    switchTaxaExpedicaoRecebe();
//    switchSeguroRecebe();
//    switchPorcentagemRecebe();
//    switchHoraRecebe();
//    switchHoraExcedeRecebe();
//    switchKmRecebe();
//    switchEntregaRecebe();
//    switchEntregaKgRecebe();
//    switchEntregaVolumeRecebe();
//    switchSaidaRecebe();
//    switchCapacidadeRecebe();
//    switchAjudanteRecebe();
//    despesaRecebe();
//    valorRecebe();
//    switchDescontoRecebe();
//    switchPorcentagemPaga();
//    switchHoraPaga();
//    switchHoraExcedePaga();
//    switchKmPaga();
//    switchEntregaPaga();
//    switchEntregaKgPaga();
//    switchEntregaVolumePaga();
//    switchSaidaPaga();
//    switchCapacidadePaga();
//    switchAjudantePaga();
//    despesaPaga();
//    somaMinutaRecebe();
//    somaMinutaPaga();

    var loadForm = function(){
        var obj = $(this);
        var idminuta = $(this).attr("idminuta");
        var idminutacolaboradores = $(this).attr("idminutacolaboradores");
        var idminutaitens = $(this).attr("idminutaitens");
        var idminutanotas = $(this).attr("idminutanotas");

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
                $(".js-edita-minuta-form").attr('action', "{% url 'editaminuta' 0 %}".replace(/0/, idminuta));
                $(".js-edita-minutaveiculo-form").attr('action', "{% url 'editaminutaveiculo' 0 %}".replace(/0/, idminuta));
                $(".js-exclui-minutamotorista-form").attr('action', "{% url 'excluiminutamotorista' 0 %}".replace(/0/, idminutacolaboradores));
                $(".js-exclui-minutaajudante-form").attr('action', "{% url 'excluiminutaajudante' 0 %}".replace(/0/, idminutacolaboradores));
                $(".js-exclui-minutadespesa-form").attr('action', "{% url 'excluiminutadespesa' 0 %}".replace(/0/, idminutaitens));
                $(".js-edita-minutaentrega-form").attr('action', "{% url 'editaminutaentrega' 0 %}".replace(/0/, idminutanotas));
                $(".js-exclui-minutaentrega-form").attr('action', "{% url 'excluiminutaentrega' 0 %}".replace(/0/, idminutanotas));
                console.log(data)
            }
        });
    };

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