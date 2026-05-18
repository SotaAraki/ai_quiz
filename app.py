from flask import Flask, jsonify
import requests
import re
import json
from flask import Response

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

PROMPT = """
以下のJSONのみを出力してください。

{
  "question": "",
  "answer": true,
  "explanation": ""
}

日本語の難しい○×クイズを1問作成してください。

例:
{
  "question": "日本の首都は東京である。",
  "answer": true,
  "explanation": "日本の首都は東京です。"
}
解説では理由や補足説明を書いてください。
"""

@app.route("/quiz")
def generate_quiz():

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3",
            "system": "あなたはJSONのみを返すAPIです。thinkは禁止です。",
            "prompt": PROMPT,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 150
            }
        },
        timeout=120
    )

    # AIの返答取得
    print(response.json())

    text = response.json()["response"]

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
        return Response(
            json.dumps(quiz_data, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        return jsonify({
            "error": str(e),
            "raw": cleaned
        }), 500


if __name__ == "__main__":
    app.run(debug=True)