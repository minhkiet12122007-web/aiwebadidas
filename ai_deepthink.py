import json
from google import genai

client = genai.Client(
    api_key="AIzaSyCzlJypKS5QpLMd08SgpvOONi6MUP2FaPQ"
)

MODEL_CANDIDATES = [
    "models/gemini-flash-latest",
    "models/gemini-2.5-flash"
]


def generate_content(prompt):
    last_error = None
    for model_id in MODEL_CANDIDATES:
        try:
            return client.models.generate_content(model=model_id, contents=prompt)
        except Exception as e:
            last_error = e
            print(f"Model {model_id} failed: {e}")
    raise last_error


def deep_process(analysis):
    user_msg = analysis.get("keyword", "")
    is_greeting = analysis.get("is_greeting", False)

    # 1. Đọc database sản phẩm[cite: 21, 25]
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            db = json.load(f)
    except:
        db = {"products": []}

    internal_matches = []
    # Chỉ tìm kiếm nếu không phải là lời chào đơn thuần
    if not is_greeting:
        targets = ([analysis.get("specific_model")] if analysis.get(
            "specific_model") else []) + analysis.get("suggested_models", [])
        for t in targets:
            if not t:
                continue
            for p in db["products"]:
                if t.lower() in p["name"].lower() and p not in internal_matches:
                    internal_matches.append(p)

    # 2. Tạo phản hồi từ AI[cite: 21]
    context = f"Câu hỏi khách: {user_msg}\nSản phẩm có sẵn: {json.dumps(internal_matches[:3], ensure_ascii=False)}"
    prompt = f"Bạn là trợ lý ảo Adidas. Hãy phản hồi thân thiện. Nếu là lời chào, hãy chào lại và hỏi họ cần tìm giày gì. Nếu có sản phẩm: {context}, hãy giới thiệu chúng. Không dùng JSON."

    try:
        response = generate_content(prompt)
        return {
            "reply": response.text,
            "images": [p["img"] for p in internal_matches[:3]]
        }, None
    except Exception as e:
        return {"reply": "Xin lỗi, mình đang gặp chút trục trặc. Bạn nhắn lại nhé!"}, str(e)
