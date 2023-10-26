$('#shortener_form').submit(function(e){
    
    e.preventDefault();
    $.ajax({
        url: '/short_it',
        method: 'post',
        data: {
            'url': $('#shortener_url').val()
        },
        success: function(data) {
            if (data.status == 'success') {
                alert_box(data.message, 3000, 'var(--success)');
                $('#shortener_link').attr('href', data.url);
                $('#shortener_link').text(data.url);

            } else {
                alert_box(data.message, 3000, 'var(--error)');
            }
        }
    })
});