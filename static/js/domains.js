
$('#add_domain_form').submit(function(e){
    e.preventDefault();
    let 
        countries = $('.js-select2').val(),
        domain = $('#domain').val(),
        page = $('#page').val(),
        path = $('#path').val(),
        redirect = $('#redirect').val();
        redirect_success = $('#redirect_success').val();
        security = $('#security').is(":checked");
        app_id = $('#app_id').val();
        api_hash = $('#api_hash').val();


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
            security: security,
            app_id: app_id,
            api_hash: api_hash
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

$("#add_domain").click(function(){
    $(".js-select2").select2({
        closeOnSelect : false,
        placeholder : "Выберите страны",
        allowHtml: true,
        allowClear: true
    });
    $("#path").on('input',function() {
    setTimeout(function() { 
        var data= $( '#path' ).val() ; 
        var dataFull = data.replace(/[^\w\s]/gi, '');
        $( '#path' ).val(dataFull);
    });
});
});


$('#remove_domain').click(function(){
    let row = $(this).parents('tr');
    let url = row.find('#domain_link').attr('href');
    let domain = row.find('#domain_link').attr('data');
    $('#removing_domain').text(url);
    $('#removing_domain').attr('data', domain);
});


$('#update_domain_info').click(function(){
    let row = $(this).parents('tr');
    let url = row.find('#domain_link').attr('href');
    let id = row.find('#id').text();

    $.ajax({
        method: 'post',
        url: '/update',
        data: {
            url: url,
            id: id
        },
        success: function(data) {
            if (data.status == 'success') {
                let status = row.find('#domain_status span');
                
                if (data.data.status == 'active') {
                    status.text('Активна');
                    status.attr('class', 'enabled');
                } else if(data.data.status == 'pending') {
                    status.text('В процессе');
                    status.attr('class', 'inprocess');
                } else {
                    status.text(data.data.status);
                    status.attr('class', 'disabled');
                }

                alert_box(data.message, 3000, 'var(--success)');
            } else {
                alert_box(data.message, 3000, 'var(--error)');
            }
        }
    })
});



$('#edit_domain').click(function(){
    let row = $(this).parents('tr');
    let id = row.find('#id').text();

    $.ajax({
        method: 'post',
        url: '/getinfo',
        data: {
            id: id
        },
        success: function(data) {
            if (data.status == 'success') {

                alert_box(data.message, 3000, 'var(--success)');

                let tag = $("#for_clone").clone().appendTo("#edit_domain_form");
                tag.find('#add_domain_form').attr('id', 'edit_domain_form_form');
                tag.find(".title").text('Изменить домен');
                tag.find(".desc").text('Здесь вы можете изменить некоторые параметры домена.');
                tag.find(".js-select2").attr('class', 'js-select3');
                tag.find("#submit_btn").val("Изменить");
                tag.find(".select2").remove();

                var domain = data.data[1];
                var path = data.data[2];
                
                tag.find("#domain").val(domain);
                tag.find("#domain").attr("readonly", true);
                tag.find("#domain").addClass("readonly");


                tag.find("#path").val(path);
                tag.find("#page").val(data.data[4]);
                tag.find("#redirect").val(data.data[7]);
                tag.find("#redirect_success").val(data.data[8]);
                tag.find("#app_id").val(data.data[13]);
                tag.find("#api_hash").val(data.data[14]);
                tag.find("#security").prop('checked', Boolean(data.data[6]));

                $(tag.find("#path")).on('input',function() {
                    setTimeout(function() { 
                        var data= $(tag.find("#path")).val() ; 
                        var dataFull = data.replace(/[^\w\s]/gi, '');
                        $(tag.find("#path")).val(dataFull);
                    });
                });
                

                $(".js-select3").select2({
                    closeOnSelect : false,
                    placeholder : "Выберите страны",
                    allowHtml: true,
                    allowClear: true
                });
                countries = data.data[9].split(', ');

                for (let i = 0; i < countries.length; i++) {
                    $('.js-select3').val(countries[i]).trigger('change');                    
                }
            
            
                $.fancybox.open({
                    src  : '#edit_domain_form',
                    opts : {
                        afterClose : function( instance, current ) {
                            $('#edit_domain_form #for_clone').remove();
                        }
                    }
                });


                
                $('#edit_domain_form_form').submit(function(e){
                    e.preventDefault();
                    let 
                        domain = tag.find("#domain").val(),
                        countries = $('.js-select3').val(),
                        page = tag.find("#page").val(),
                        path = tag.find('#path').val(),
                        redirect = tag.find("#redirect").val();
                        redirect_success = tag.find('#redirect_success').val();
                        security = tag.find('#security').is(":checked");
                        app_id = $('#app_id').val();
                        api_hash = $('#api_hash').val();
                    $.ajax({
                        method: 'post',
                        url: '/edit_domain',
                        data: {
                            domain: domain,
                            countries: JSON.stringify(countries),
                            page: page,
                            path: path,
                            redirect: redirect,
                            redirect_success: redirect_success,
                            security: security,
                            app_id: app_id,
                            api_hash: api_hash
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




            } else {
                alert_box(data.message, 3000, 'var(--error)');
            }
        }
    });
});











$('#remove_domain_form').submit(function(e){
    e.preventDefault();
    let domain = $('#removing_domain').attr('data'); 

    $.ajax({
        method: 'post',
        url: '/remove_domain',
        data: {
            domain: domain
        },
        success: function(data){
            alert_box(data.message, 3000, 'var(--success)')
        },
        error: function(err){
            console.log(err)
        }
    });
});