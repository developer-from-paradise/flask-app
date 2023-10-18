window.history.pushState("object or string", "Title", "/"+window.location.href.substring(window.location.href.lastIndexOf('/') + 1).split("?")[0]);
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