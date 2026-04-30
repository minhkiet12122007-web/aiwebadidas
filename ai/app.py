from flask import Flask, request, jsonify, render_template
from ai_thinking import analyze_intent
from ai_deepthink import deep_process

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_msg = data.get("message", "")
        analysis = analyze_intent(user_msg)
        result, error = deep_process(analysis)
        return jsonify(result)
    except:
        return jsonify({"reply": "Lỗi kết nối server!"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
