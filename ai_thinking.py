import os
import json
import re
from google import genai

# LẤY API KEY TỪ BIẾN MÔI TRƯỜNG (An toàn)
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)


def analyze_intent(user_input):
    prompt = f"""
    Bạn là chuyên gia Adidas. Hãy phân tích yêu cầu: "{user_input}"
    Trả về DUY NHẤT JSON:
    {{
        "specific_model": "tên model hoặc null",
        "category": "running/lifestyle hoặc null",
        "price_limit": null,
        "suggested_models": ["samba", "ultraboost", "superstar"],
        "is_greeting": true/false
    }}
    """
    try:
        # Sử dụng model gemini-1.5-flash ổn định hơn
        response = client.models.generate_content(
            model="gemini-1.5-flash", contents=prompt)
        clean_text = re.search(r'\{.*\}', response.text, re.DOTALL).group()
        data = json.loads(clean_text)
        data["keyword"] = user_input
        return data
    except Exception as e:
        print(f"Lỗi analyze_intent: {e}")
        return {"keyword": user_input, "suggested_models": [], "is_greeting": True}
