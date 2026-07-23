console.log("setting.js 読み込み");
const saveButton = document.getElementById("save");

saveButton.onclick = () => {
    console.log("保存ボタン押下");
    localStorage.setItem(
        "genre",
        document.getElementById("genre").value
    );

    localStorage.setItem(
        "difficulty",
        document.getElementById("difficulty").value
    );

    alert("保存しました");
    console.log(localStorage.getItem("genre"));
    console.log(localStorage.getItem("difficulty"));
};