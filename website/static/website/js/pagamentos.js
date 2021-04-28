$('.switch').change(function() {
    $('.pagamento-base-itens').html("");
    nome = $(this).attr('id');

    $.ajax({
        type: 'GET',
        url: 'teste',
        data: {
            nome: nome,
        },
        success: function(data) {
            $('.pagamento-base-itens').html(data.html_form);
        },
    });

   
});

$(document).on('submit', '#form-seleciona-folha', function(event) {
    event.preventDefault();
    var url = $(this).attr('action') || action;
    $.ajax({
        type: $(this).attr('method'),
        url: url,
        data: $(this).serialize(),
        beforeSend: function(){
            $(".fp-folha-contracheque").html("");
        },
        success: function(data){
            $(".fp-folha-contracheque").html(data.html_folha);
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
            $(".fp-folha-contracheque").html("");
        },
        success: function(data){
            $(".fp-folha-contracheque").html(data.html_folha);
        },
        error: function(error) {
            console.log(error)
        }
    });
});