from flask import Flask, jsonify, request
import random

app = Flask(__name__)

# ʾ�� API ·�ɣ�GET ����
@app.route('/api/emg', methods=['GET'])
def get_emg_data():
    # ���ɶ�̬�� EMG ���ݣ�ģ�⼡���ź�
    data = {
        "gesture": random.choice(["grip", "wave", "pinch"]),
        "emg_value": [random.randint(50, 300) for _ in range(3)]  # ����������������ź�����
    }
    return jsonify(data)

# ʾ�� API ·�ɣ�POST ����
@app.route('/api/emg', methods=['POST'])
def post_emg_data():
    # ��ȡǰ�˴����� JSON ����
    data = request.get_json()  
    print("Received EMG data:", data)
    
    # ���ؽ��յ������ݣ�������һ��ȷ����Ϣ
    return jsonify({
        "status": "success",
        "received_data": data,
        "message": "Data received successfully"
    })

if __name__ == '__main__':
    # ���� Flask Ӧ��
    app.run(host='0.0.0.0', port=5000)
