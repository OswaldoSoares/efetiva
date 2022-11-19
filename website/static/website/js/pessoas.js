$(document).on('click', ".js-seleciona-colaborador", function() {
    var id_pessoal = $(this).data("idpessoal");
    $.ajax({
        type: "GET",
        url: "/pessoas/consulta_pessoa",
        data: {
            id_pessoal: id_pessoal,
        },
        beforeSend: function() {
            $(".card-dados-colaborador").hide()
            $(".box-loader").show()
        },
        success: function(data) {
            $(".card-dados-colaborador").html(data.html_dados_colaborador)
            $(".card-dados-colaborador").show()
            $(".box-loader").hide()
        },
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});