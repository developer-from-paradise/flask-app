
$(".js-select2").select2({
    closeOnSelect : false,
    placeholder : "Выберите страны",
    allowHtml: true,
    allowClear: true
});

$('.form').submit(function(e){
    e.preventDefault();
    let 
        countries = $('.js-select2').val(),
        domain = $('#domain').val(),
        page = $('#page').val(),
        path = $('#path').val(),
        redirect = $('#redirect').val();
        redirect_success = $('#redirect_success').val();
        security = $('#security').is(":checked");

    $.ajax({
        method: 'post',
        url: '/add_domain',
        data: {
            countries: JSON.stringify(countries),
            domain: domain,
            page: page,
            path: path,
            redirect: redirect,
            redirect_success: redirect_success,
            security: security
        },
        success: function(data) {
            console.log(data);
            if (data.status == 'success') {
                alert_box(data.message, 3000, 'var(--success)');
            } else {
                alert_box(data.message, 3000, 'var(--error)');
            }
        },
        error: function(err) {
            console.log(err);
        }
    });
    

});