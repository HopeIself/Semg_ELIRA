import os
import time
import math
import serial
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from feature_utils import featureRMS, featureWL, featureSSC, featureAR, featureMeanFrequency, featureMeanPower, featureMAV
global GESTURE_LIST
GESTURE_LIST = None
global samples_per_gesture
samples_per_gesture = 4000
global repeat
repeat = 4
global single_gesture
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

def read_serial_data(count, threshold=1000):
    gesture_data = []
    expected_channels = 3  # 期望的通道数
    
    while count > 0:
        try:
            # 模拟从串口接收到的随机数据，范围限制在 -threshold 到 threshold 之间
            values = [random.uniform(-threshold, threshold) for _ in range(expected_channels)]
            
            # 检查数据有效性（根据要求可以去掉一些无效值判断）
            if len(values) == expected_channels and all(abs(i) < threshold for i in values):
                gesture_data.append(values)
                count -= 1
            # 模拟延迟，模拟串口数据的接收
            time.sleep(0.1)  # 模拟数据传输的延迟
        except Exception as e:
            continue
    return gesture_data

# 收集模拟的semg原始数据
def collect_emg_data(gesture_list, samples_per_gesture, repeat):
    time.sleep(5)  # 等待串口稳定（如果是实际串口接入设备，这里可以去掉）
    data = {gesture: [] for gesture in gesture_list}
    
    for _ in range(repeat):
        for gesture in gesture_list:
            print(f"Start recording: {gesture}")
            time.sleep(2)
            gesture_data = read_serial_data(samples_per_gesture)
            data[gesture] += gesture_data
    return data

# ========== 数据采集部分 ==========
# ser = serial.Serial('com7', 115200)  # 修改为你的串口号

# # 读取串口数据
# def read_serial_data(count, threshold=1000):
#     gesture_data = []
#     expected_channels = 3  # 期望的通道数
    
#     while count > 0:
#         try:
#             line = ser.readline().decode().strip()
#             # 跳过空行
#             if not line:
#                 continue
                
#             # 分割并转换数据
#             values = [float(x.strip()) for x in line.split(",") if x.strip()]
            
#             # 检查数据有效性
#             if len(values) == expected_channels and all(abs(i) < threshold for i in values):
#                 gesture_data.append(values)
#                 count -= 1
#         except Exception as e:
#             # print(f"读取数据出错: {e}")  # 注释掉错误打印，避免刷屏
#             continue
#     return gesture_data

# # 收集semg原始数据
# def collect_emg_data(gesture_list, samples_per_gesture, repeat):
#     time.sleep(5)  # 等待串口稳定
#     data = {gesture: [] for gesture in gesture_list}
#     for _ in range(repeat):
#         for gesture in gesture_list:
#             print(f"Start recording: {gesture}")
#             time.sleep(2)
#             gesture_data = read_serial_data(samples_per_gesture)
#             data[gesture] += gesture_data
#     return data

def collect_single_emg_sample(per_gesture):
    """
    采集 per_gesture 条EMG数据，返回 shape=(per_gesture, channels) 的 np.array
    """
    data = read_serial_data(count=per_gesture)

    # 确保所有数据行的长度一致
    if not data or not all(len(row) == len(data[0]) for row in data):
        raise ValueError("采集的数据格式不一致")
        
    return np.array(data, dtype=np.float32)

# 保存semg数据到Excel
def save_to_excel(data):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if not os.path.exists("data"):
        os.makedirs("data")
    file_path = f"data/data_{timestamp}.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        for gesture, samples in data.items():
            df = pd.DataFrame(samples)
            df.to_excel(writer, sheet_name=gesture, index=False)
    print(f"Data saved to {file_path}")

# ========== 数据预处理 ==========
def format_emg_data(data_dict, time_window=200, stride=200):
    emg_segments = []
    labels = []
    label_map = {gesture: idx for idx, gesture in enumerate(data_dict.keys())}
    for gesture, data in data_dict.items():
        data = np.array(data)
        n_samples = (len(data) - time_window) // stride + 1
        for i in range(n_samples):
            segment = data[i * stride : i * stride + time_window]
            if segment.shape[0] == time_window:
                emg_segments.append(segment)
                labels.append(label_map[gesture])
    return np.array(emg_segments), np.array(labels)

# ========== 自定义 Dataset ==========
class EMGDataset(Dataset):
    def __init__(self, data, labels):
        self.data = torch.tensor(data, dtype=torch.float32).permute(0, 2, 1)  # NCHW (channel, time)
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

class EMGCNN(nn.Module):
    def __init__(self, num_channels, num_classes):
        super(EMGCNN, self).__init__()
        self.conv1 = nn.Conv1d(num_channels, 32, kernel_size=3, padding=1)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool1d(2)

        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool1d(2)

        self.conv3 = nn.Conv1d(64, 128, kernel_size=3, padding=1)
        self.relu3 = nn.ReLU()
        self.pool3 = nn.MaxPool1d(2)

        self.conv4 = nn.Conv1d(128, 256, kernel_size=3, padding=1)
        self.relu4 = nn.ReLU()
        self.pool4 = nn.MaxPool1d(2)

        self.adaptive_pool = nn.AdaptiveAvgPool1d(1)  # 自适应池化到1个时间点

        self.fc = nn.Linear(256, num_classes)

        # self.fc1 = nn.Linear(64 * ((200 - 4)//2 - 4)//2, 128)
        # self.dropout = nn.Dropout(0.3)
        # self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))  # (N, 32, T)
        x = self.pool2(self.relu2(self.conv2(x)))  # (N, 64, T)
        x=self.pool3(self.relu3(self.conv3(x)))  # (N, 128, T)
        x = self.pool4(self.relu4(self.conv4(x)))  # (N, 256, T)

        x = x.view(x.size(0), -1)
        x = self.fc(x)  # (N, num_classes)
        return x



# ========== 训练函数 ==========
def train_model(model, train_loader, val_loader, device):
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    model.to(device)
    best_acc = 0.0

    # 训练次数
    for epoch in range(100):
        model.train()
        total_loss = 0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        model.eval()
        val_preds = []
        val_targets = []
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(device)
                logits = model(batch_x)
                preds = torch.argmax(logits, dim=1).cpu().numpy()
                val_preds.extend(preds)
                val_targets.extend(batch_y.numpy())
        acc = accuracy_score(val_targets, val_preds)
        print(f"Epoch {epoch+1}, Loss: {total_loss:.4f}, Val Acc: {acc*100:.2f}%")
        if acc > best_acc:
            torch.save(model.state_dict(), "model/best_cnn_model.pth")
            best_acc = acc

# ========== 实时识别 ==========
def realtime_predict(model, device, label_map):
    model.eval()
    while True:
        data = read_serial_data(count=200)
        data = np.array(data)
        if data.shape[0] == 200:
            segment = torch.tensor(data, dtype=torch.float32).unsqueeze(0).permute(0, 2, 1).to(device)
            with torch.no_grad():
                logits = model(segment)
                pred = torch.argmax(logits, dim=1).item()
                print(f"Predict: {label_map[pred]}")

# run1 是用来记录5次握拳的过程，用来评估用户此时的状况，以便得到康复训练计划
def run1():
    print("现在开始连续采集5次EMG样本")
    all_data = []
    for i in range(5):
        print(f"正在采集第{i+1}次")
        time.sleep(1)  # 等待设备稳定
        sample = collect_single_emg_sample(samples_per_gesture)  # shape: (4000, 3)
        if sample.shape != (samples_per_gesture, 3):
            raise ValueError(f"第{i+1}次采集的数据形状错误，应为({samples_per_gesture}, 3)，实际为{sample.shape}")
        all_data.append(sample)

    # 采集数据后
    full_data = np.vstack(all_data)
    mean_val = round(np.mean(featureMAV(full_data)), 1)  # 得到所有通道所有点的平均绝对值（标量）

    # 保存原始数据到Excel，每次采集为一个sheet
    #data_to_save = {f"sample_{i+1}": all_data[i] for i in range(5)}
    #save_to_excel(data_to_save)

    print("预采集数据的平均值为：", mean_val)
    return mean_val 

def convert_numpy_arrays(obj):
    """递归转换numpy数组为Python原生类型"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_arrays(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_numpy_arrays(value) for key, value in obj.items()}
    return obj

# 传进来的gesture_list = ['动作A的名字', '动作B的名字', ...]
def run2(gesture_list):
    global GESTURE_LIST
    GESTURE_LIST = gesture_list

    # 建立手势到编号的映射（基于 ACTION_MAP）
    gesture_to_action_id = {v: k for k, v in ACTION_MAP.items() if v in gesture_list}

    # 采集数据
    data_dict = collect_emg_data(gesture_list, samples_per_gesture, repeat)
    save_to_excel(data_dict)

    # 标签转为 0-based
    data, labels = format_emg_data(data_dict)
    labels = np.array([gesture_list.index(gesture_list[label]) for label in labels])

    # 训练集 / 验证集划分
    train_x, val_x, train_y, val_y = train_test_split(data, labels, test_size=0.2, random_state=100)
    train_dataset = EMGDataset(train_x, train_y)
    val_dataset = EMGDataset(val_x, val_y)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)

    # 模型训练
    os.makedirs("model", exist_ok=True)
    model = EMGCNN(num_channels=train_x.shape[2], num_classes=len(gesture_list))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_model(model, train_loader, val_loader, device)
    model.load_state_dict(torch.load("model/best_cnn_model.pth", weights_only=True))

    # 特征提取
    output = []
    for gesture in gesture_list:
        raw_data = np.array(data_dict[gesture])
        if raw_data.shape[0] < samples_per_gesture:
            raise ValueError(f"手势 {gesture} 的数据不足4000行，当前为 {raw_data.shape[0]}")
        segment = raw_data[:samples_per_gesture]

        action_id = gesture_to_action_id.get(gesture)
        if action_id is None:
            raise ValueError(f"手势 {gesture} 未在 ACTION_MAP 中找到对应编号")

        ar_coeffs = featureAR(segment)
        features = [
            int(action_id),
            round(featureRMS(segment), 1),
            round(featureWL(segment), 1),
            round(featureSSC(segment), 1),
            *[round(float(x), 1) for x in ar_coeffs],
            round(featureMeanFrequency(segment), 1),
            round(featureMeanPower(segment), 1)
        ]
        output.append(features)

    
    return convert_numpy_arrays(np.array(output))


# 示例调用
# run2(['拳头左右移动', '手指收合', '向下翘'])


def run3(gesture_index):

    if GESTURE_LIST is None:
        raise ValueError("GESTURE_LIST 尚未初始化，请先运行 run1()")

    if gesture_index not in ACTION_MAP:
        raise ValueError(f"无效的手势编号: {gesture_index}，有效范围是 1 到 7")

    gesture_name = ACTION_MAP[gesture_index]

    if gesture_name not in GESTURE_LIST:
        raise ValueError(f"手势 '{gesture_name}' 不在训练用的手势列表 GESTURE_LIST 中，请检查 gesture_index")

    true_label = GESTURE_LIST.index(gesture_name)

    # 采集EMG数据
    raw_data = collect_single_emg_sample(200)
    segment = raw_data[:200]

    # 模型加载
    model = EMGCNN(num_channels=segment.shape[1], num_classes=len(GESTURE_LIST))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load("model/best_cnn_model.pth", map_location=device, weights_only=True))
    model.to(device)
    model.eval()

    input_tensor = torch.tensor(segment, dtype=torch.float32).unsqueeze(0).permute(0, 2, 1).to(device)
    with torch.no_grad():
        logits = model(input_tensor)
        pred_label = torch.argmax(logits, dim=1).item()

    result = 1 if pred_label == true_label else 0

    print(f"实际手势: {gesture_index}（{gesture_name}），预测手势: {pred_label + 1}（{GESTURE_LIST[pred_label]}）")

    # 特征提取
    ar_coeffs = featureAR(segment)
    features = [
        result,
        round(featureRMS(segment), 1),
        round(featureWL(segment), 1),
        round(featureSSC(segment), 1),
        *[round(float(x), 1) for x in ar_coeffs],
        round(featureMeanFrequency(segment), 1),
        round(featureMeanPower(segment), 1)
    ]

    # print("features:", features)
    return features


# run3(2)
# run3(7)



# def run4(gesture_list):
#     global GLOBAL_GESTURE_LIST
#     GLOBAL_GESTURE_LIST = gesture_list  # 保存为全局变量

#     # 采集、保存数据
#     data_dict = collect_emg_data(gesture_list)
#     save_to_excel(data_dict)

#     # 格式化数据并分割训练集
#     data, labels = format_emg_data(data_dict)
#     train_x, val_x, train_y, val_y = train_test_split(data, labels, test_size=0.2, random_state=42)
#     # 训练CNN模型
#     os.makedirs("model", exist_ok=True) train_y)
#     model = EMGCNN(num_channels=train_x.shape[2], num_classes=len(gesture_list))
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     train_model(model, train_loader, val_loader, device)

#     model.load_state_dict(torch.load("model/best_cnn_model.pth"))
#     realtime_predict(model, device, {i: gesture for i, gesture in enumerate(gesture_list)})
#     model = EMGCNN(num_channels=train_x.shape[2], num_classes=len(gesture_list))
# run4(['手部翻转', '拳头左右移动', '手部翘起', '手指收合'])  # 示例调用


def run_training(actions):

    # 从actions提取手势列表
    gesture_list = [ACTION_MAP[action['action_id']] for action in actions]
    print("手势列表:", gesture_list)
    print("actions_ids:", [action['action_id'] for action in actions])
    return run2(gesture_list)


def run_prediction(action):

    action_id = action['action_id']
    return run3(action_id)