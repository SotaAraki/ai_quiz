from flask import Flask, jsonify, request
import requests
import re
import json
from flask import Response
import random
from flask_cors import CORS
from flask import render_template

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"

# 難易度
# difficulty = f"難しい"

difficultys = [
    f"簡単",
    f"普通",
    f"難しい",
]

# ジャンル
genres = [
    "科学",
    "歴史",
    "生物",
    "宇宙",
    "地理",
    "化学",
    "物理",
    "人体",
    "IT",
    "数学",
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/quiz")
def quiz_page():
    return render_template("quiz.html")

@app.route("/setting")
def setting_page():
    return render_template("setting.html")

@app.route("/api/quiz")
def generate_quiz():

    genre = request.args.get("genre", "ランダム")
    difficulty = request.args.get("difficulty", "ランダム")

    if genre == "ランダム":
        genre = random.choice(genres)

    if difficulty == "ランダム":
        difficulty = random.choice(difficultys)

    PROMPT = f"""
        以下のJSONのみを出力してください。

        {{
        "question": "",
        "answer": true,
        "explanation": "",
        "difficulty": "{difficulty}",
        "genre": "{genre}"
        }}

        条件
        - 日本語の○×クイズを1問作成してください。
        - 難易度: "{difficulty}"
        - ジャンル: {genre}
        - explanationは理由を書く
        - 同じ問題を繰り返さない
        - 客観的に正誤が決定できる問題のみ作成する
        - 学校のテストで出題できるレベルの問題にする
        - 問題文だけで○×が判断できること
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3",
            "format": "json",
            "system": """
                    あなたはクイズ生成APIです。

                    必ずJSONのみを返してください。
                    説明や会話は禁止です。
                    thinkは禁止です。

                    毎回必ず異なる問題を生成してください。
                    同じ題材を繰り返してはいけません。

                    問題はランダムなジャンルから選んでください。
                    """,
            "prompt": PROMPT,
            "stream": False,
            # "think": False,
            "options": {
                "temperature": 0.3,     # 回答のランダム度合い
                "num_predict": 250,     #  出力トークン数（出力の長さに関わる）
            }
        },
        timeout=120
    )

    print(response.status_code)
    print(response.text)

    # AIの返答取得
    data = response.json()

    print("OLLAMA:", data)

    text = data.get("response")

    if text is None:
        return jsonify({
            "error": "responseキーがありません",
            "raw": data
        }), 500

    text = data.get("response", "").strip()

    print("----- RAW -----")
    print(text)
    print("---------------")

    # response が空だった場合
    if text == "":
        return jsonify({
            "error": "AIの返答が空です",
            "raw": data
        }), 500

    # think除去
    cleaned = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    ).strip()

    # JSON部分だけ取得
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)

    if not match:
        return jsonify({
            "error": "JSONの取得に失敗しました",
            "raw": cleaned
        }), 500

    quiz_json = match.group()

    try:
        quiz_data = json.loads(quiz_json)

##############################################################
# ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⠀⠀⢀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⠶⠿⠛⠛⠛⠛⠛⠛⠛⠿⠷⣶⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⠀⣠⡾⠟⠛⠛⠛⠿⣦⣄⠀⣠⣴⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⢷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⠀⣼⡟⠀⠀⠀⠀⠀⠀⠈⢙⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
# ⢰⣿⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣦⠀⠀⠀⠀⠀⠀⠀⠀
# ⢸⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡎⠉⢱⡀⠀⠀⠀⠀⡜⠁⠹⡄⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀
# ⠈⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⢸⡇⠀⠀⠀⢰⡇⠀⢠⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀
# ⠀⢹⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣶⣿⡇⠀⠀⠀⢸⣿⣶⣾⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣧⠀⠀⠀⠀⠀
# ⠀⠀⢻⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⡇⠀⠀⠀⠸⣿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣆⠀⠀⠀⠀
# ⠀⠀⠀⠹⣷⡴⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⠁⠀⠀⠀⠀⢿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣷⡀⠀⠀
# ⠀⠀⠀⠀⢸⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠁⢠⣶⣶⣶⣦⠈⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣷⡀⠀
# ⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣏⠀⢈⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣇⠀
# ⠀⠀⠀⠀⠘⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀
# ⠀⠀⠀⠀⠀⢹⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡟⠀
# ⠀⠀⠀⠀⠀⠀⢿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⠀⠀⠀⣀⣴⡿⠁⠀
# ⠀⠀⠀⠀⠀⠀⣸⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣨⣿⣿⡛⠛⠉⠀⠀⠀
# ⠀⠀⠀⢀⣴⣿⠋⠁⠙⢧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠏⠈⠙⠻⣶⣄⠀⠀⠀
# ⠀⢀⣴⣿⣯⣴⡆⠀⠀⠀⠙⢦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠟⠁⠀⠀⢰⣶⣬⣻⣷⡀⠀
# ⠀⣾⠏⢸⣿⠿⠃⠀⠀⠀⠀⠀⠙⠳⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠶⠋⠀⠀⠀⠀⠀⠈⠻⢿⡿⠹⣿⡀
# ⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠲⢦⣤⣤⣀⣀⠀⢀⣀⣠⣤⣤⠶⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣹⡇
# ⠀⠻⣷⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣬⣿⠟⠛⠻⣿⣯⣥⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣴⡿⠃
# ⠀⠀⠀⠉⠛⠛⠿⠿⠶⠶⠶⠶⠶⠿⠿⠿⠟⠛⠛⠋⠉⠀⠀⠀⠀⠀⠉⠉⠛⠛⠻⠿⠿⠿⠶⠶⠶⠶⠶⠾⠿⠛⠛⠋⠁⠀⠀
##############################################################


        # 実験用：答えをわざと反転する
        # quiz_data["answer"] = not quiz_data["answer"]

        quiz_data["difficulty"] = difficulty
        quiz_data["genre"] = genre
        return Response(
            json.dumps(quiz_data, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        return jsonify({
            "error": str(e),
            "raw": cleaned
        }), 500

# ファクトチェック機能
@app.route("/api/factcheck", methods=["POST"])
def fact_check():

    quiz = request.json

    prompt = f"""
        以下の○×クイズについて判定してください。

        問題:
        {quiz["question"]}

        AIの答え:
        {quiz["answer"]}

        解説:
        {quiz["explanation"]}

        判定基準:
        - 問題文が事実か確認する
        - answer が正しいか確認する
        - explanation が正しいか確認する
        - 実在しない制度・人物・事件・用語が含まれていないか確認する
        - 知識に確信が持てない場合は「誤り」とする
        - 推測で判定してはいけない

        すべて正しいなら:
        "result": "正しい"

        1つでも間違いがあれば:
        "result": "誤り"

        JSONのみ返してください。

        {{
            "result": "",
            "reason": ""
        }}
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3",
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.0,     # 回答のランダム度合い
                "num_predict": 150,     #  出力トークン数（出力の長さに関わる）
            },
        }
    )

    print(response.status_code)
    print(response.text)

    data = response.json()
    print("OLLAMA:", data)
    print(data)

    print("----- FACTCHECK RAW -----")
    print(data["response"])
    print("-------------------------")

    return Response(
        data["response"],
        content_type="application/json"
    )

if __name__ == "__main__":
    app.run(debug=True)