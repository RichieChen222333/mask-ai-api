import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import traceback

app = Flask(__name__)
CORS(app)

# 設定 Gemini API Key（從環境變數讀）
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 建立 Gemini 模型）
model = genai.GenerativeModel("gemini-2.5-flash")


@app.post("/api/ai/mask-summary")
def mask_summary():
    data = request.get_json()

    city = data.get("city", "")
    area = data.get("area", "")
    pharmacies = data.get("pharmacies", [])

    prompt = f"""
            你是台灣在地生活小幫手，請用「繁體中文」回答，口吻簡單、清楚、給一般民眾看得懂。

            使用者問：「{area}現在口罩供應怎樣？」

            請依照下面格式輸出, 並且只推薦去一間藥局（請嚴格照格式，不要多話）：

            藥局數量：X 間
            成人口罩總量：X 個
            兒童口罩總量：X 個
            建議先去：藥局A（成人X 兒童X）

            以下是資料（JSON）：
            {pharmacies}
            """.strip()
    try:
        response = model.generate_content(prompt)
        return jsonify({"ok": True, "answer": response.text})

    except Exception as e:
        tb = traceback.format_exc()
        print("=== GEMINI ERROR ===")
        print(tb)
        return jsonify({"ok": False, "error": str(e), "trace": tb}), 500


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
