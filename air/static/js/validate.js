
function validate(){

var username = document.getElementById("inputEmail").value;
var password = document.getElementById("inputPassword").value;

window.open("/check_login?usr="+username+"&pass="+password,"_self");

return false;
}

