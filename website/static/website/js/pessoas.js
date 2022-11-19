$(document).on('click', ".js-seleciona-colaborador", function() {
    var id_pessoal = $(this).data("idpessoal");
    $.ajax({
        type: "GET",
        url: "/pessoas/consulta_pessoa",
        data: {
            id_pessoal: id_pessoal,
        },
        beforeSend: function() {},
        success: function(data) {},
        error: function(errorThrown) {
            console.log("error: " + errorThrown)
        }
    });
});