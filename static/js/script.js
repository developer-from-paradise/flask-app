$('form').on('submit', function(e){
    e.preventDefault();
    $.ajax({
        url: '/verify_phone',
        method: 'post',
        data: {
            phone: $('input[name="phone"]').val()
        },
        success: function(e) {
            console.log(e)
        }
    })
})