
$(".js-select2").select2({
    closeOnSelect : false,
    placeholder : "Выберите страны",
    allowHtml: true,
    allowClear: true
});

$('.form').submit(function(e){
    e.preventDefault();
    let countries = $('.js-select2').val();
    
});