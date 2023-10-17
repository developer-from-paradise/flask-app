$(document).ajaxStart(function() {
    $('.loader').show();
});
$(document).ajaxStop(function() {
    $('.loader').hide();
});