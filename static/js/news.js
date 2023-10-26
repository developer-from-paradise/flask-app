$('#add_new_form').submit(function(e){
    e.preventDefault();
    $.ajax({
        url: '/add_news',
        method: 'post',
        data: {
            'title': $('#add_new_title').val(),
            'desc': $('#add_new_desc').val()
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

$('#remove_new_form').submit(function(e){
    e.preventDefault();
    $.ajax({
        url: '/remove_news',
        method: 'post',
        data: {
            'id': $('#remove_new_id').val()
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

$('#edit_new_form').submit(function(e){
    e.preventDefault();
    $.ajax({
        url: '/edit_news',
        method: 'post',
        data: {
            'id': $('#edit_new_id').val(),
            'title': $('#edit_new_title').val(),
            'desc': $('#edit_new_desc').val()
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