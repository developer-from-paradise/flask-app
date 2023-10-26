$('#add_faq_form').submit(function(e){
    e.preventDefault();
    $.ajax({
        url: '/add_faq',
        method: 'post',
        data: {
            'title': $('#add_faq_title').val(),
            'link': $('#add_faq_link').val()
        },
        success: function(data) {
            if (data.status == 'success') {
                alert_box(data.message, 3000, 'var(--success)');
            } else {
                alert_box(data.message, 3000, 'var(--error)');
            }
        }
    })
});

$('#remove_faq_form').submit(function(e){
    e.preventDefault();
    $.ajax({
        url: '/remove_faq',
        method: 'post',
        data: {
            'id': $('#remove_faq_id').val()
        },
        success: function(data) {
            if (data.status == 'success') {
                alert_box(data.message, 3000, 'var(--success)');
            } else {
                alert_box(data.message, 3000, 'var(--error)');
            }
        }
    })
});