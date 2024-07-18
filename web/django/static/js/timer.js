let mailSend = document.getElementById("mailSend");

let divtimerinfo = document.getElementById("divtimerInfo");

mailSend.addEventListener("click", function(){
    var timeleft = 30;
    mailSend.classList.add("disabled");
    divtimerinfo.classList.remove("d-none");
    divtimerinfo.classList.remove("d-xxl-none");
    var timer = setInterval(function function1(){
    timeleft -= 1;
    document.getElementById("seconds").innerHTML = timeleft + "&nbsp"+"seconds";
        if(timeleft === 0){
            clearInterval(timer);
            mailSend.classList.remove("disabled");
            divtimerinfo.classList.add("d-none");
            divtimerinfo.classList.add("d-xxl-none");
        }
    }, 1000);
});
