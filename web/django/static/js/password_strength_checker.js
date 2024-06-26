var strength = {
  0: "Worst",
  1: "Bad",
  2: "Weak",
  3: "Good",
  4: "Strong"
}

var password = document.getElementById('floatingPassword-register');
var meter = document.getElementById('password-strength-meter');
var text = document.getElementById('password-strength-text');

text.innerHTML = "Password Strength ";
password.addEventListener('input', function() {
  var val = password.value;
  var result = zxcvbn(val);

  // Update the password strength meter
  meter.value = result.score;
  // Update the text indicator
  if (val !== "") {
    text.innerHTML = "Password Strength " + strength[result.score];
  } else {
    text.innerHTML = "Password Strength "
  }
});