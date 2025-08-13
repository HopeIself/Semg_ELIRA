"""
EMG处理模块: 提供肌电信号采集和特征提取功能
"""
import os
import time
import numpy as np
import pandas as pd
import random
from datetime import datetime
from typing import Dict, List, Tuple, Any

from utils.config import MOCK_DATA_MODE

# 如果不是模拟模式，使用真实串口
if not MOCK_DATA_MODE:
    import serial
    try:
        from utils.config import SERIAL_PORT, SERIAL_BAUD_RATE
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD_RATE)
    except (ImportError, AttributeError):
        print("警告: 未定义串口配置，将使用模拟数据")
        MOCK_DATA_MODE = True

# 从feature_utils.py导入特征提取函数
from scipy import signal
from statsmodels.tsa.ar_model import AutoReg

#均方根
def featureRMS(data):
    val = np.mean(np.sqrt(np.mean(data**2, axis=0)))
    print(f"[featureRMS] 计算结果: {val}")
    return val

#波形长
def featureWL(data):
    val = np.mean(np.sum(np.abs(np.diff(data, axis=0)),axis=0)/data.shape[0])
    print(f"[featureWL] 计算结果: {val}")
    return val

#斜率符号变化次数
def featureSSC(data,threshold=10e-7):
    numOfSSC = []
    channel = data.shape[1]
    length  = data.shape[0]
    for i in range(channel):
        count = 0
        for j in range(2,length):
            diff1 = data[j,i]-data[j-1,i]
            diff2 = data[j-1,i]-data[j-2,i]
            sign  = diff1 * diff2
            if sign>0:
                if(np.abs(diff1)>threshold or np.abs(diff2)>threshold):
                    count=count+1
        numOfSSC.append(count/length)
    result = np.mean(np.array(numOfSSC))
    print(f"[featureSSC] 计算结果: {result}")
    return result

#自回归模型系数ARC
def featureAR(data):
    AR_num = 7
    row = []
    for j in range(data.shape[1]):
        x = data[:, j]
        AR7_model = AutoReg(x, AR_num).fit()
        AR_params = AR7_model.params[1:AR_num + 1]
        row.append(AR_params)
    row=np.array(row)
    result = tuple(np.mean(row, axis=0))
    print(f"[featureAR] 计算结果: {result}")
    return result

# 平均频率
def featureMeanFrequency(data):
    fs = 2000
    mean_freq_all = []
    for i in range(data.shape[1]):
        f, Pxx = signal.welch(data[:, i], fs, nperseg=200)
        mean_frequency = np.trapz(f * Pxx, f) / np.trapz(Pxx, f)
        mean_freq_all.append(mean_frequency)
    result = np.mean(np.array(mean_freq_all))
    print(f"[featureMeanFrequency] 计算结果: {result}")
    return result

# 平均功率
def featureMeanPower(data):
    fs = 2000
    mean_power_all = []
    for i in range(data.shape[1]):
        f, Pxx = signal.welch(data[:, i], fs, nperseg=200)
        mean_power = np.trapz(Pxx, f)
        mean_power_all.append(mean_power)
    result = np.mean(np.array(mean_power_all))
    print(f"[featureMeanPower] 计算结果: {result}")
    return result

# 平均绝对值
def featureMAV(data):
    val = np.mean(np.abs(data), axis=0)
    print(f"[featureMAV] 计算结果: {val}")
    return val

def read_serial_data(count, threshold=1000):
    """
    读取UDP队列数据或串口数据或生成模拟数据

    Args:
        count: 需要读取的数据点数
        threshold: 数据阈值，用于过滤噪声

    Returns:
        List: 收集到的数据列表，每个元素是一个通道的数据
    """
    gesture_data = []
    expected_channels = 3  # 期望的通道数

    # 优先从UDP队列获取
    try:
        from app import UDP_DATA_QUEUE
        use_udp = True
    except ImportError:
        use_udp = False

    if use_udp:
        import time
        for _ in range(count):
            try:
                # 最多等2秒
                emg = UDP_DATA_QUEUE.get(timeout=2)
                if isinstance(emg, list) and len(emg) == expected_channels:
                    gesture_data.append(emg)
                else:
                    gesture_data.append([0.0] * expected_channels)
            except Exception:
                gesture_data.append([0.0] * expected_channels)
    elif MOCK_DATA_MODE:
        # 模拟数据模式
        while count > 0:
            # 模拟从串口接收到的随机数据
            values = [random.uniform(-threshold, threshold) for _ in range(expected_channels)]

            # 检查数据有效性
            if len(values) == expected_channels and all(abs(i) < threshold for i in values):
                gesture_data.append(values)
                count -= 1

            # 模拟延迟
            time.sleep(0.01)  # 降低延迟以加快模拟速度
    else:
        # 实际串口模式
        while count > 0:
            try:
                line = ser.readline().decode().strip()
                # 跳过空行
                if not line:
                    continue

                # 分割并转换数据
                values = [float(x.strip()) for x in line.split(",") if x.strip()]

                # 检查数据有效性
                if len(values) == expected_channels and all(abs(i) < threshold for i in values):
                    gesture_data.append(values)
                    count -= 1
            except Exception as e:
                # 静默处理异常，避免刷屏
                continue

    print(f"[read_serial_data] 返回数据长度: {len(gesture_data)}")
    return gesture_data

def collect_single_emg_sample(per_gesture):
    """
    采集单次EMG样本

    Args:
        per_gesture: 每个手势需要采集的样本数

    Returns:
        np.ndarray: 采集的数据，shape=(per_gesture, channels)
    """
    data = read_serial_data(count=per_gesture)
    print(f"[collect_single_emg_sample] 采集到数据 shape: {np.array(data).shape}")

    # 确保所有数据行的长度一致
    if not data or not all(len(row) == len(data[0]) for row in data):
        raise ValueError("采集的数据格式不一致")

    return np.array(data, dtype=np.float32)

def collect_emg_data(gesture_list, samples_per_gesture, repeat):
    """
    采集多个手势的EMG数据

    Args:
        gesture_list: 手势列表
        samples_per_gesture: 每个手势需要采集的样本数
        repeat: 重复采集次数

    Returns:
        Dict: 手势名称到采集数据的映射
    """
    time.sleep(2)  # 等待串口稳定
    data = {gesture: [] for gesture in gesture_list}

    for _ in range(repeat):
        for gesture in gesture_list:
            print(f"开始记录手势: {gesture}")
            time.sleep(1)
            gesture_data = read_serial_data(samples_per_gesture)
            data[gesture] += gesture_data

    # 保存数据到Excel
    save_to_excel(data)

    print(f"[collect_emg_data] 采集数据 keys: {list(data.keys())}")
    return data

def save_to_excel(data):
    """
    保存EMG数据到Excel文件

    Args:
        data: 手势名称到采集数据的映射
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if not os.path.exists("data"):
        os.makedirs("data")
    file_path = f"data/data_{timestamp}.xlsx"

    with pd.ExcelWriter(file_path) as writer:
        for gesture, samples in data.items():
            df = pd.DataFrame(samples)
            df.to_excel(writer, sheet_name=gesture, index=False)

    print(f"[save_to_excel] 已保存数据到 {file_path}")
