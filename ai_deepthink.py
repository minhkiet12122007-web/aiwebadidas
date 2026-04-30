import os
import json
from google import genai

API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)


def deep_process(analysis):
    user_msg = analysis.get("keyword", "")
    is_greeting = analysis.get("is_greeting", False)

    # Đọc database sản phẩm
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
    except Exception as e:
        print(f"Lỗi đọc DB: {e}")
        db = {"products": []}

    internal_matches = []
    if not is_greeting:
        targets = ([analysis.get("specific_model")] if analysis.get(
            "specific_model") else []) + analysis.get("suggested_models", [])
        for t in targets:
            if not t:
                continue
            for p in db["products"]:
                if t.lower() in p["name"].lower() and p not in internal_matches:
                    internal_matches.append(p)

    # Tạo phản hồi
    context = f"Câu hỏi: {user_msg}\nSản phẩm có sẵn: {json.dumps(internal_matches[:3], ensure_ascii=False)}"
    prompt = f"Bạn là trợ lý Adidas. Phản hồi thân thiện. Nếu là lời chào, hãy chào lại. Nếu có sản phẩm: {context}, hãy giới thiệu kèm ưu điểm. Không dùng JSON trong câu trả lời."

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash", contents=prompt)
        return {
            "reply": response.text,
            "images": [p["img"] for p in internal_matches[:3] if "img" in p]
        }, None
    except Exception as e:
        return None, str(e)
