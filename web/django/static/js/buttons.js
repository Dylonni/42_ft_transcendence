function showPassword(){
    var show = document.getElementById('floatingPassword-register');
    if (show.type == 'password'){
        show.type = 'text';
    }
    else{
        show.type = 'password';
    }
};