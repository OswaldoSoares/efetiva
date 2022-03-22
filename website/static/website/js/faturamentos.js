$(document).ready(function(){
    $('.box-loader').hide()

    /**
     * Percorre todos os cards e deixa o body do mesmo tamanho (somento os que estão no mesmo "position top" do primiro card)
     */
    // TODO: Implementar para cards que não estiverem no mesmo "position top" do primeiro
    var maxHeight = 0;
    var topPosition = 0;
    var tamanhoCardBody = function() {
        $('.js-card-body').each(function(index) {
            if (index === 0) {
                topPosition = $(this).position().top
            }
            var thisH = $(this).height();
            if (thisH > maxHeight) {
                maxHeight = thisH
            }
        });
        $('.js-card-body').each(function() {
            if ($(this).position().top == topPosition) {
                $(this).height(maxHeight)
            }
        });
    }
    tamanhoCardBody();

    var text_mensagem = $('.text-mensagem').text()
    var type_mensagem = $('.type-mensagem').text()
    if (type_mensagem != 'None') {
        if (type_mensagem == 'ERROR') {
            $('.mensagem-erro').text(text_mensagem)
            $(".div-erro").slideDown(500)
            $(".div-erro").delay(5000).slideUp(500) 
        } else if (type_mensagem == 'SUCESSO') {
            $('.mensagem-sucesso').text(text_mensagem)
            $(".div-sucesso").slideDown(500)
            $(".div-sucesso").delay(5000).slideUp(500) 
        }
    }

    $('.js-file-nota').on('change', function() {
        if ($('.js-file-nota').val()) {
            $('.js-notaTxt').text($('.js-file-nota').val().match(/[\/\\]([\w\d\s\.\-\(\)]+)$/)[1]);
        } else {
            $('.js-notaTxt').text('Selecionar nota fiscal.');
        }
    });

    $('.js-file-boleto').on('change', function() {
        if ($('.js-file-boleto').val()) {
            $('.js-boletoTxt').text($('.js-file-boleto').val().match(/[\/\\]([\w\d\s\.\-\(\)]+)$/)[1]);
        } else {
            $('.js-boletoTxt').text('Selecionar boleto.');
        }
    });

    $('.js-delete-file').on('click', function() {
        var idobj = $(this).data('idobj')
        var idfatura = $(this).data('idfatura')
        $.ajax({
            url: '/faturamentos/delete_file',
            type: 'GET',
            data: {
                idobj: idobj,
                idfatura: idfatura,
            },
            beforeSend: function() {
            },
            success: function(data) {
                window.location.href = '/faturamentos/fatura/' + data['idfatura'] + '/'
            }
        });
    });

    $('.js-send-email').on('click', function() {
        var idobj = $('.js-send-email').data('idobj')
        var emails = $('#email').val()
        var texto = $('#text').val()
        $.ajax({
            url: '/faturamentos/email_fatura',
            type: 'GET',
            data: {
                idobj: idobj,
                emails: emails,
                texto: texto,
            },
            beforeSend: function(){
                $('.text-loader').text('Aguarde, enviando e-mail...')
                $('.box-loader').fadeIn(50);
            },
            success: function(data){
                $('.box-loader').hide();
                $('.text-loader').text('Aguarde...')
                if (data['type_mensagem'] == 'ERROR') {
                    $('.mensagem-erro').text(data['text_mensagem'])
                    $(".div-erro").slideDown(500)
                    $(".div-erro").delay(5000).slideUp(500) 
                } else if (data['type_mensagem'] == 'SUCESSO') {
                    $('.mensagem-sucesso').text(data['text_mensagem'])
                    $(".div-sucesso").slideDown(500)
                    $(".div-sucesso").delay(5000).slideUp(500) 
                }    
            },
            error: function(data) {
                $('.box-loader').hide();
                $('.text-loader').text('Aguarde...')
            },
        });
    });

    $('.js-paga-fatura').on('click', function() {
        var idobj = $('.js-paga-fatura').data('idobj')
        var datapagto = $('#dt_paga').val()
        var valorpago = $('#vl_paga').val()
        $.ajax({
            url: '/faturamentos/paga_fatura',
            type: 'GET',
            data: {
                idobj: idobj,
                datapagto: datapagto,
                valorpago: valorpago,
            },
            beforeSend: function() {
                $('.text-loader').text('Aguarde, processando pagamento...')
                $('.box-loader').fadeIn(50);
            },
            success: function(data) {
                $('.box-loader').hide();
                $('.text-loader').text('Aguarde...')
                if (data['type_mensagem'] == 'ERROR') {
                    $('.mensagem-erro').text(data['text_mensagem'])
                    $(".div-erro").slideDown(500)
                    $(".div-erro").delay(5000).slideUp(500) 
                } else if (data['type_mensagem'] == 'SUCESSO') {
                    $('.mensagem-sucesso').text(data['text_mensagem'])
                    $(".div-sucesso").slideDown(500)
                    $(".div-sucesso").delay(5000).slideUp(500) 
                }
            },
            error: function(error) {

            },
        });
    });

    $('.js-cliente-faturas').on('click', function () {
        var vElementSel = $(this)
        var idobj = $(this).data('idobj')
        var vElement = $('.cl-'+$(this).data('idobj'))
        if ($(vElement).is(':hidden')) {
            $.ajax({
                url: '/faturamentos/cliente_fatura',
                type: 'GET',
                data: {
                    idobj: idobj,
                },
                beforeSend: function() {
                    escondeFaturasPagas()
                },
                success: function(data) {
                    $(vElementSel).removeClass("bi-caret-right-fill").addClass("bi-caret-down-fill");
                    $(vElement).html(data['html_faturas'])
                    $(vElement).fadeIn(500)
                },
                error: function(error) {
    
                },
            });
        } else {
            $(vElementSel).removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
            escondeFaturasPagas()
        }
    });

    

    if ($('.body-email').height() > $('.body-file').height()) {
        $('.body-file').height($('.body-email').height())
        $('.body-fatura').height($('.body-email').height())
    } else {
        $('.body-email').height($('.body-file').height())
        $('.body-fatura').height($('.body-file').height())
    }


    var buscaDados = function(minuta){
        var minuta = minuta;
        var idcliente = 9;

        $.ajax({
            url: "/faturamentos/criadivselecionada",
            type: 'get',
            dataType: 'json',
            data: {
                minuta: minuta,
            },
            beforeSend: function(){
                $('#'+minuta).html("");
            },
            success: function(data){
                $('#'+minuta).html(data.html_minuta);
            }
        });
    };

    var somaFatura = 0.00

    $('.tag-select').each(function(){
        if ($(this).text() == $('#cod-10004').text()) {
            somaFatura += parseFloat($(this).attr('valor').replace(',','.'))
            minuta = $(this).attr('id').substr(6,($(this).attr('id').length)-1);
            $('.minutas-selecionadas').append('<div class="auto-minuta" id=' + minuta + ' data-sid=' + minuta + '>' + minuta + '</div>');
            $('.input-cria-fatura').append('<input id="input'+ minuta +'" type="hidden" name="numero-minuta" value='+
            minuta +'>');
            buscaDados(minuta);
        }
        $('.valor-fatura').val('R$ ' + somaFatura.toFixed(2).replace('.',','));
    });

    $(".tb-select-minuta > tbody > tr > td").on("click", function (e) {
        var $this = '#'+$(this).attr('id').replace('col2','col1');
        var $atual =  $this.replace('col1','atual');
        var minuta = $atual.substr(7,($atual.length)-1);
        if ($($atual).text() == $('#cod-10004').text()) {
            $('#'+minuta).remove();
            $('#input'+minuta).remove();
            $($this).removeClass("checked");
            $($this).toggleClass("nochecked");
            $($atual).text($('#cod-10008').text());
            somaFatura -= parseFloat($($atual).attr('valor').replace(',','.'));
        } else {
            $('.minutas-selecionadas').append('<div class="auto-minuta" id=' + minuta + ' data-sid=' + minuta + '>' + minuta + '</div>');
            $('.input-cria-fatura').append('<input id="input'+ minuta +'" type="hidden" name="numero-minuta" value='+
            minuta +'>');
            buscaDados(minuta);
            $($this).removeClass("nochecked");
            $($this).toggleClass("checked");
            $($atual).text($('#cod-10004').text());
            somaFatura += parseFloat($($atual).attr('valor').replace(',','.'));
        };
        $('.minutas-selecionadas div').sort(function(a,b){
            return parseInt(a.dataset.sid) > parseInt(b.dataset.sid)
        }).appendTo('.minutas-selecionadas');
        $('.valor-fatura').val('R$ ' + somaFatura.toFixed(2).replace('.',','));
    });

    var loadForm = function(){
        var obj = $(this);
        var idfatura = $(this).attr("idfatura");

        $.ajax({
            url: obj.attr("data-url"),
            type: 'get',
            dataType: 'json',
            data: {
                idfatura: idfatura,
            },
            beforeSend: function(){
                $("#modal-formulario .modal-content").html("");
                $("#modal-formulario").modal("show");
            },
            success: function(data){
                $("#modal-formulario .modal-content").html(data.html_form);
            }
        });
    };

    $(".js-pagafatura").click(loadForm);
    escondeFaturasPagas()
});

var escondeFaturasPagas = function() {
    $('.js-div-pagas').each(function() {
        $(this).fadeOut('500')
        $(this).html('')
        $(this).hide()
    });
    $('.js-cliente-faturas').each(function() {
        $(this).removeClass("bi-caret-down-fill").addClass("bi-caret-right-fill");
    });
}