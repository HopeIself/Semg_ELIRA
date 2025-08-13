from flask import Flask, jsonify, request
import random

app = Flask(__name__)

# 示例 API 路由，GET 请求
@app.route('/api/emg', methods=['GET'])
def get_emg_data():
    # 生成动态的 EMG 数据，模拟肌电信号
    data = {
        "gesture": random.choice(["grip", "wave", "pinch"]),
        "emg_value": [random.randint(50, 300) for _ in range(3)]  # 随机生成三个肌电信号数据
    }
    return jsonify(data)

# 示例 API 路由，POST 请求
@app.route('/api/emg', methods=['POST'])
def post_emg_data():
    # 获取前端传来的 JSON 数据
    data = request.get_json()  
    print("Received EMG data:", data)
    
    # 返回接收到的数据，并返回一个确认消息
    return jsonify({
        "status": "success",
        "received_data": data,
        "message": "Data received successfully"
    })

if __name__ == '__main__':
    # 运行 Flask 应用
    app.run(host='0.0.0.0', port=5000)
