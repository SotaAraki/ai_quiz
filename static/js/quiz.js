let question = document.getElementById("question");         // 問題文
// let answer = document.getElementById("answer");             // 成否（〇✕）
const result = document.getElementById("result");           // 成否結果
let explanation = document.getElementById("explanation");   // 解説
let genre = document.getElementById("genre");               // ジャンル
let difficulty = document.getElementById("difficulty");     // 難易度

const trueButton = document.getElementById("true_button");      // 〇ボタン
const falseButton = document.getElementById("false_button");    // ✕ボタン

const factCheck = document.getElementById("fact_check");        // 確認ボタン
const nextQuiz = document.getElementById("next_quiz");          // 次の問題ボタン

// ファクトチェック部分
const factModal = document.getElementById("factModal");
const factStatus = document.getElementById("factStatus");
const factResult = document.getElementById("factResult");
const factJudge = document.getElementById("factJudge");
const factReason = document.getElementById("factReason");
const closeModal = document.getElementById("closeModal");
const loadingSpinner = document.getElementById("loader");

let currentQuiz = null; // クイズ結果の一時保存先

async function fetchQuiz() {
    try{
        // 空白にする
        question.textContent = "読み込み中...";
        result.textContent = "";
        // answer.textContent = "";
        explanation.textContent = "";
        genre.textContent = "";
        difficulty.textContent = "";

        // 読み込み中ボタンを押せなくする
        trueButton.disabled = true;
        falseButton.disabled = true;
        factCheck.disabled = true;
        nextQuiz.disabled = true;

        const savedGenre =
            localStorage.getItem("genre") || "ランダム";

        const savedDifficulty =
            localStorage.getItem("difficulty") || "ランダム";

        const response = await fetch(
            `http://127.0.0.1:5000/api/quiz?genre=${savedGenre}&difficulty=${savedDifficulty}`
        );
        const quiz = await response.json();
        console.log(savedGenre);
        console.log(savedDifficulty);
        console.log(quiz);

        currentQuiz = quiz;  // クイズ内容保存

        question.textContent = quiz.question;
        // answer.textContent = quiz.answer ? "○" : "×";
        // explanation.textContent = quiz.explanation;
        genre.textContent = quiz.genre;
        difficulty.textContent = quiz.difficulty;

        // 回答ボタン有効化
        trueButton.disabled = false;
        falseButton.disabled = false;
    } catch (e){
        console.error(e);
        alert("クイズ取得失敗")
    }
};

// 〇✕ボタンを押した時
function checkAnswer(userAnswer) {
    if (!currentQuiz) {
        alert("クイズがまだ読み込まれていません");
        return;
    }

    if (userAnswer === currentQuiz.answer) {
        result.textContent = "正解！";
    } else {
        result.textContent = "不正解";
    }

    // document.getElementById("explanation").textContent = currentQuiz.explanation;
    // answer.textContent = currentQuiz.answer ? "○" : "×";
    explanation.textContent = currentQuiz.explanation;

    // 回答後ボタン無効化
    trueButton.disabled = true;
    falseButton.disabled = true;

    // 次の問題ボタンを押せるように
    nextQuiz.disabled = false;
    factCheck.disabled = false;
}

// 次の問題を押した時にもう一度出す
nextQuiz.onclick = function() {
    fetchQuiz();
}

// ファクトチェック閉じるボタン
closeModal.onclick = function () {
    factModal.style.display = "none";
}
//開く
factCheck.onclick = async function () {

    factModal.style.display = "flex";

    factStatus.textContent = "ファクトチェック中...";
    factResult.style.display = "none";

    try {
        const response = await fetch(
            "http://127.0.0.1:5000/api/factcheck",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(currentQuiz)
            }
        );

        const data = await response.json();
        console.log(data);

        factJudge.textContent = data.result;

        if (data.result === "正しい") {
            factJudge.style.color = "green";
        } else {
            factJudge.style.color = "red";
        }

        factStatus.textContent = "";
        loadingSpinner.style.display = "none";

        factJudge.textContent = data.result;
        factReason.textContent = data.reason;

        factResult.style.display = "block";

    } catch (e) {
        factStatus.textContent = "ファクトチェックに失敗しました";
        console.error(e);
    }
}

fetchQuiz();
trueButton.onclick = () => checkAnswer(true);
falseButton.onclick = () => checkAnswer(false);
