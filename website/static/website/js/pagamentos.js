$(document).ready(function(){

});

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

$(document).on('change', '#id_MesReferencia', function(event) {
    $(".fp-contrachequeitens").html("");
    $(".fp-folha-contracheque").html("");
    $(".fp-adiantamento").html("");
    $(".fp-adiantamento").hide();
});

$(document).on('change', '#id_AnoReferencia', function(event) {
    $(".fp-contrachequeitens").html("");
    $(".fp-folha-contracheque").html("");
    $(".fp-adiantamento").html("");
    $(".fp-adiantamento").hide();
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
            $(".fp-adiantamento").hide();
        },
        success: function(data){
            $(".fp-folha-contracheque").html(data.html_folha);
            $(".fp-contrachequeitens").html("");
            $(".fp-adiantamento").hide();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('submit', '#form-cria-contrachequeitens', function(event) {
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
            $(".fp-contrachequeitens").html(data.html_formccitens);
            $(".fp-contracheque").html(data.html_contracheque);
            if (data.html_adiantamento == true) {
                $(".fp-adiantamento").hide();
            } else {
                $(".fp-adiantamento").show();
            }
            $(".fp-adiantamento").html(data.html_formccadianta);
            $(".fp-cartaoponto").html(data.html_cartaoponto);
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
            $(".fp-adiantamento").hide();
        },
        success: function(data){
            $(".fp-folha-contracheque").html(data.html_folha);
            $(".fp-adiantamento").hide();
        },
        error: function(error) {
            console.log(error)
        }
    });
});

$(document).on('click', '.selecionar-contracheque', function(event) {
    var url = $(this).attr('data-url')
    var mesreferencia = $(this).attr('mesreferencia')
    var anoreferencia = $(this).attr('anoreferencia')
    var idpessoal = $(this).attr('idpessoal')
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        data: {
            MesReferencia: mesreferencia,
            AnoReferencia: anoreferencia,
            idPessoal: idpessoal,
        },
        beforeSend: function(){
            $(".fp-contrachequeitens").html("");
            $(".fp-contracheque").html("");
            $(".fp-adiantamento").html("");
            $(".fp-adiantamento").hide();
            $(".fp-cartaoponto").html("");
        },
        success: function(data){
            $(".fp-contrachequeitens").html(data.html_formccitens);
            $(".fp-contracheque").html(data.html_contracheque);
            if (data.html_adiantamento == true) {
                $(".fp-adiantamento").hide();
            } else {
                $(".fp-adiantamento").show();
            }
            $(".fp-adiantamento").html(data.html_formccadianta);
            $(".fp-cartaoponto").html(data.html_cartaoponto);
        },
        error: function(error) {
            console.log(error)
        }
    });
});