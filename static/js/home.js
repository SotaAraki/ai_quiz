const quizButton = document.getElementById("quiz_go");
const settingButton = document.getElementById("setting_go");

quizButton.onclick = function(){
    location.href = '/quiz';
}

settingButton.onclick = function(){
    location.href = '/setting';
}