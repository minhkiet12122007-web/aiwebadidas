from google import genai
import json
import re

# Khởi tạo Client với model Gemini hiện tại
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


def analyze_intent(user_input):
    # Prompt yêu cầu AI xử lý linh hoạt hơn với tin nhắn chào hỏi[cite: 23]
    prompt = f"""
    Bạn là chuyên gia Adidas. Hãy phân tích yêu cầu: "{user_input}"
    Chỉ trả về DUY NHẤT một khối JSON:
    {{
        "specific_model": "tên model hoặc null",
        "category": "running/lifestyle hoặc null",
        "price_limit": con số VNĐ hoặc null,
        "suggested_models": ["samba", "ultraboost", "superstar"],
        "is_greeting": true/false
    }}
    """
    try:
        response = generate_content(prompt)
        clean_text = re.search(r'\{.*\}', response.text, re.DOTALL).group()
        data = json.loads(clean_text)
        data["keyword"] = user_input
        return data
    except Exception as e:
        print(f"Lỗi phân tích intent: {e}")
        return {"keyword": user_input, "suggested_models": [], "is_greeting": True}
