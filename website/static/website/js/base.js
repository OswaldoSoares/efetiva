$(".div-sucesso").hide()
$(".div-erro").hide()

if ($(window).width() <= 800) {
    $(".menu-nav-icons").css('display', 'none')
    $(".menu-dots").css('display', 'block')
    $(".container").css('margin-top', '0')
} else {
    $(".container").css('margin-top', '79px')
};

$(document).on('click', '#menu-dots', function() {
    if ($(".menu-nav-icons").is(':visible')) {
        $(".menu-nav-icons").css('display', 'none')
    } else {
        $(".menu-nav-icons").css('display', 'block')
    };
});
