
"""
配置文件: 包含系统所需的全局配置
"""
import os

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'model')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# EMG相关配置
NORMALIZATION_FACTOR = 1.0
samples_per_gesture = 200
repeat = 4
single_gesture = 200

# 动作映射字典
ACTION_MAP = {
    1: '手部翻转',
    2: '拳头左右移动',
    3: '手部翘起',
    4: '手指收合',
    5: '肩部屈曲外展',
    6: '压掌',
    7: '向下翘'
}

# 随机生成模式（仅用于开发和测试）
MOCK_DATA_MODE = True

# 串口配置（使用真实设备时取消注释）
# SERIAL_PORT = 'COM7'
# SERIAL_BAUD_RATE = 115200
