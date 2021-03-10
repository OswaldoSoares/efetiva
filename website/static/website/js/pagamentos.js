$('.switch').change(function() {
    $('.pagamento-base-itens').html("");
    console.log($(this).attr('id'));
    nome = $(this).attr('id');

    $.ajax({
        type: 'GET',
        url: 'teste',
        data: {
            nome: nome,
        },
        success: function(data) {
            $('.pagamento-base-itens').html(data.html_form);
            console.log('ok')
            
        },
    });
});