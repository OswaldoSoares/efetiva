$(document).ready(function(){
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
            $($this).removeClass("checked");
            $($this).toggleClass("nochecked");
            $($atual).text($('#cod-10008').text());
            somaFatura -= parseFloat($($atual).attr('valor').replace(',','.'));
        } else {
            $('.minutas-selecionadas').append('<div class="auto-minuta" id=' + minuta + ' data-sid=' + minuta + '>' + minuta + '</div>');
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

});
