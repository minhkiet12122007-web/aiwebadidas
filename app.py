from flask import Flask, request, jsonify, render_template
from ai_thinking import analyze_intent
from ai_deepthink import deep_process
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_msg = data.get("message", "")
        # Phân tích ý định người dùng
        analysis = analyze_intent(user_msg)
        # Xử lý chuyên sâu và trả về kết quả
        result, error = deep_process(analysis)

        if error:
            print(f"Lỗi logic: {error}")
            return jsonify({"reply": "Xin lỗi, mình gặp chút trục trặc hệ thống."}), 200

        return jsonify(result)
    except Exception as e:
        print(f"Lỗi Server: {e}")
        return jsonify({"reply": "Lỗi kết nối server!"}), 500


if __name__ == '__main__':
    # Chạy trên Render cần host '0.0.0.0'
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
