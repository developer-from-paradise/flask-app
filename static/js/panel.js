function animate(selector, fadeIn, fadeOut, time, display) {
    $(selector).css('animation-duration', time+"ms");

    if(!($(selector).hasClass(fadeIn))) {
        $(selector).removeClass(fadeOut);
        $(selector).css('display', display);
        $(selector).addClass(fadeIn);
    } else {
        $(selector).removeClass(fadeIn);
        $(selector).addClass(fadeOut);
        setTimeout(function(){
            $(selector).css('display', 'none');
        }, time);
    }
}


function alert_box(text, duration, bg) {
    $('.alert_box').text(text);
    $('.alert_box').css('background', bg);
    animate('.alert_box', 'animate__slideInUp', 'animate__slideOutDown', 300, 'block');
    setTimeout(function(){
        animate('.alert_box', 'animate__slideInUp', 'animate__slideOutDown', 300, 'block');
    }, duration);
}



$('.nav__burger').click(function(){
    $(this).toggleClass('active');
    animate('.nav__links', 'animate__fadeInDown', 'animate__fadeOutUp', 300, 'flex');
});



$('#add_user_form').submit(function(e) { 
    e.preventDefault();
    let username = $('#add_username').val();
    let password = $('#add_password').val();
    let chat_id = $('#add_chat_id').val();
    let bot_token = $('#add_bot_token').val();

    let note = $('#add_note').val();


    $.ajax({
        url: '/add_user',
        method: 'post',
        data: {
            username: username,
            password: password,
            chat_id: chat_id,
            bot_token: bot_token,
            note: note
        },
        success: function(data) {
            if (data.status == 'success') {
                alert_box(data.message, 3000, 'var(--success)');
            } else {
                alert_box(data.message, 3000, 'var(--error)');
            }
        },
        error: function(err) {
            console.log(err);
            alert_box(err, 3000, 'var(--error)');
        }
    });
})





$('#edit_user_form').submit(function(e) { 
    e.preventDefault();
    let user_id = $('#edit_user_id').val();
    let username = $('#edit_username').val();
    let password = $('#edit_password').val();
    let note = $('#edit_note').val();
    let city = $('#edit_city').val();
    let country = $('#edit_country').val();
    let chat_id = $('#edit_chat_id').val();
    let bot_token = $('#edit_bot_token').val();



    $.ajax({
        url: '/edit_user',
        method: 'post',
        data: {
            username: username,
            password: password,
            note: note,
            user_id: user_id,
            city: city,
            country: country,
            chat_id: chat_id,
            bot_token: bot_token
        },
        success: function(data) {
            if (data.status == 'success') {
                alert_box(data.message, 3000, 'var(--success)');
            } else {
                alert_box(data.message, 3000, 'var(--error)');
            }
        },
        error: function(err) {
            console.log(err);
            alert_box(err, 3000, 'var(--error)');
        }
    });
})







$('#remove_user_form').submit(function(e) { 
    e.preventDefault();
    let username = $('#username_to_remove').val();
    
    $.ajax({
        url: '/remove_user',
        method: 'post',
        data: {
            username: username
        },
        success: function(data) {
            if (data.status == 'success') {
                alert_box(data.message, 3000, 'var(--success)');
            } else {
                alert_box(data.message, 3000, 'var(--error)');
            }
        },
        error: function(err) {
            console.log(err);
            alert_box(err, 3000, 'var(--error)');
        }
    });
})



$('.datetime').each(function(){
    let dateString = $(this).text();
    var dateObj = new Date(dateString);
    var formattedDate = dateObj.toLocaleString({ hour12: false });
    $(this).text(formattedDate);
});














$('#download_session').click(function(){
    const logs = [];
    $('.logs-table').find('input:checked').each(function () {
        logs.push($(this).closest(".row").text());
    });

    if (logs.length <= 0) {
        alert_box("Выберите хотя бы один блог", 3000, 'var(--error)');
    } else {
        $.ajax({
           url: "/create_session",
           method: 'get',
           data: {
            logs: JSON.stringify(logs)
           },
           success: function(data) {
            if (data.status == 'success') {
                var win = window.open(data.url, '_blank');
                if (win) {
                    win.focus();
                } else {
                    alert('Разрешите всплывающие окна! Перейдите по ссылке для скачивания ' + data.url)
                }
            } else {
                alert_box(data.message, 3000, 'var(--error)');
            }
           }
        })
    }
});

$('#download_tdata').click(function(){
    const logs = [];
    $('.logs-table').find('input:checked').each(function () {
        logs.push($(this).closest(".row").text());
    });

    if (logs.length <= 0) {
        alert_box("Выберите хотя бы один блог", 3000, 'var(--error)');
    } else {
        $.ajax({
           url: "/create_tdata",
           method: 'get',
           data: {
            logs: JSON.stringify(logs)
           },
           success: function(data) {
            if (data.status == 'success') {
                var win = window.open(data.url, '_blank');
                if (win) {
                    win.focus();
                } else {
                    alert('Разрешите всплывающие окна! Перейдите по ссылке для скачивания ' + data.url)
                }
            } else {
                alert_box(data.message, 3000, 'var(--error)');
            }
           }
        })
    }
});




$('#remove_logs').click(function(){
    const logs = [];
    $('.logs-table').find('input:checked').each(function () {
        logs.push($(this).closest(".row").text());
        $(this).closest("tr").remove();
    });

    if (logs.length <= 0) {
        alert_box("Выберите хотя бы один блог", 3000, 'var(--error)');
    } else {
        $.ajax({
           url: "/remove_logs",
           method: 'post',
           data: {
            logs: JSON.stringify(logs)
           },
           success: function(data) {
            if (data.status == 'success') {
                alert_box(data.message, 3000, 'var(--success)');
            } else {
                alert_box(data.message, 3000, 'var(--error)');
            }
           }
        })
    }
});