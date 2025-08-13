"""
EMG服务模块: 处理肌电信号的采集、处理和训练功能
"""
import logging
import time
import json
import numpy as np
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Union
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from joblib import dump

from utils.emg_processor import (
    collect_single_emg_sample, 
    collect_emg_data,
    featureRMS, featureWL, featureSSC, featureAR, 
    featureMeanFrequency, featureMeanPower, featureMAV
)
from utils.config import (
    ACTION_MAP, 
    NORMALIZATION_FACTOR,
    samples_per_gesture, 
    repeat, 
    single_gesture
)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量
GESTURE_LIST = None

def run_initial_assessment() -> float:
    """
    进行初始评估，采集5秒肌电信号

    Returns:
        float: 平均肌电值
    """
    logger.info("采集 5 秒肌电信号以评估握力...")

    all_data = []
    for i in range(5):
        logger.info(f"正在采集第{i+1}次")
        time.sleep(1)  # 等待设备稳定
        sample = collect_single_emg_sample(samples_per_gesture)  # shape: (4000, 3)
        if sample.shape != (samples_per_gesture, 3):
            raise ValueError(f"第{i+1}次采集的数据形状错误，应为({samples_per_gesture}, 3)，实际为{sample.shape}")
        all_data.append(sample)

    # 采集数据后
    full_data = np.vstack(all_data)
    mean_val = round(np.mean(featureMAV(full_data)), 1)  # 得到所有通道所有点的平均绝对值（标量）

    logger.info("预采集数据的平均值为：%s", mean_val)
    return mean_val / NORMALIZATION_FACTOR

def process_data_and_train_model(data_dict):
    """
    处理采集到的数据并进行模型训练
    1. 数据归一化
    2. 特征提取
    3. 模型训练（例如：随机森林）
    保存原始数据为三列800行的格式
    """
    # 2. 保存原始数据到Excel（每个动作sheet为3列800行）
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"data_{current_time}.xlsx"
    if not os.path.exists("data"):
        os.makedirs("data")
    file_path = os.path.join("data", file_name)
    with pd.ExcelWriter(file_path) as writer:
        for key, value in data_dict.items():
            # value: [repeat][samples][channels]，如4*200*3
            # 先合并repeat和samples维度
            arr = np.array(value)  # shape: (repeat, samples, channels)
            if arr.ndim == 3:
                arr = arr.reshape(-1, arr.shape[2])  # (repeat*samples, channels)
            elif arr.ndim == 2:
                # 已经是(samples, channels)
                pass
            else:
                # 其他情况，直接转为DataFrame
                arr = np.array(value)
            df_emg = pd.DataFrame(arr, columns=[f"{i+1}" for i in range(arr.shape[1])])
            df_emg.to_excel(writer, sheet_name=key, index=False)
    logger.info(f"原始数据已保存到 {file_path}")
    
    # 新增：从刚保存的xlsx重新读取数据
    logger.info(f"从 {file_path} 重新读取归一化后的数据")
    data_from_excel = {}
    xls = pd.ExcelFile(file_path)
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        # 转为numpy数组
        data_from_excel[sheet] = df.values.tolist()
    # 用新读取的数据进行后续归一化和特征提取
    data_dict = data_from_excel

    # 3. 数据归一化
    def normalizeData(data):
        emg = []
        label = []
        labelCount = 0
        expected_len = None
        for key, value in data.items():
            if expected_len is None:
                for v in value:
                    if isinstance(v, (list, np.ndarray)):
                        expected_len = len(v)
                        break
            filtered_value = [v for v in value if isinstance(v, (list, np.ndarray)) and len(v) == expected_len]
            label_value = np.full(len(filtered_value), labelCount)
            emg.extend(filtered_value)
            label.extend(label_value)
            labelCount += 1
        emg = np.array(emg)
        return emg, label

    emg, labels = normalizeData(data_dict)

    # 4. 窗口化
    def convertDataToImageData(emg, label, timeWindow=200, strideWindow=200):
        classes = max(label) + 1
        imageLabel = []
        imageData = []
        for i in range(classes):
            index = [j for j in range(len(label)) if label[j] == i]
            iemg = emg[index, :]
            length = int((iemg.shape[0] - (strideWindow - timeWindow)) / timeWindow)
            for j in range(length):
                subImage = iemg[timeWindow * j:strideWindow * (j + 1), :]
                imageData.append(subImage)
                imageLabel.append(i)
        imageData = np.array(imageData)
        return imageData, imageLabel

    imageData, imageLabel = convertDataToImageData(emg, labels)

    # 5. 特征提取
    def featureStackForImageData(imageData):
        rms = featureRMS(imageData)
        mav = featureMAV(imageData)
        wl = featureWL(imageData)
        ssc = featureSSC(imageData)
        ar_coeffs = featureAR(imageData)
        mf = featureMeanFrequency(imageData)
        mp = featureMeanPower(imageData)
        featureStack = np.hstack((rms, mav, wl, ssc, ar_coeffs, mf, mp))
        return featureStack

    featureData = []
    featureLabel = []
    for i in range(imageData.shape[0]):
        try:
            featureStack = featureStackForImageData(imageData[i])
            featureData.append(featureStack)
            featureLabel.append(imageLabel[i])
        except Exception as e:
            logger.warning(f"特征提取失败: {e}")
            pass
    featureData = np.array(featureData)

    # 6. 划分训练集/验证集
    logger.info(f"特征数据 shape: {featureData.shape}, 标签数量: {len(featureLabel)}")
    train_x, val_x, train_y, val_y = train_test_split(featureData, featureLabel, test_size=0.2, random_state=100)
    logger.info(f"训练集 shape: {train_x.shape}, 验证集 shape: {val_x.shape}")

    # 7. 训练随机森林模型
    logger.info("开始训练随机森林模型...")
    RF = RandomForestClassifier(
        n_estimators=180, criterion='gini', max_depth=None, min_samples_split=2,
        min_samples_leaf=1, max_features='sqrt', bootstrap=True, oob_score=True
    )
    RF.fit(train_x, train_y)
    logger.info("模型训练完成。")

    score = RF.score(train_x, train_y)
    logger.info(f"训练集准确率: {score:.4f}")

    predict = RF.predict(val_x)
    accuracy = metrics.accuracy_score(val_y, predict)
    logger.info(f"验证集准确率: {accuracy:.4f}")

    # 8. 保存模型
    save_dir = "model"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    model_path = os.path.join(save_dir, "best_model.joblib")
    dump(RF, model_path)
    logger.info(f"模型已保存到 {model_path}")

    return {"accuracy": accuracy, "model_path": model_path}
def run_prediction_session(action: Dict[str, Any]) -> List[float]:
    """
    执行预测过程，收集和预测单个动作

    Args:
        action: 包含action_id的动作信息

    Returns:
        List[float]: 预测结果和特征值
    """
    global GESTURE_LIST

    if GESTURE_LIST is None:
        raise ValueError("GESTURE_LIST 尚未初始化，请先运行训练")

    action_id = action['action_id']

    if action_id not in ACTION_MAP:
        raise ValueError(f"无效的手势编号: {action_id}，有效范围是 1 到 7")

    gesture_name = ACTION_MAP[action_id]

    if gesture_name not in GESTURE_LIST:
        raise ValueError(f"手势 '{gesture_name}' 不在训练用的手势列表 GESTURE_LIST 中")

    true_label = GESTURE_LIST.index(gesture_name)

    # 采集EMG数据
    raw_data = collect_single_emg_sample(single_gesture)
    segment = raw_data[:single_gesture]

    from utils.model_handler import predict_gesture

    # 预测手势
    pred_label = predict_gesture(segment, len(GESTURE_LIST))

    # 确定结果 (1表示成功匹配, 0表示失败)
    result = 1 if pred_label == true_label else 0

    logger.info(f"实际手势: {action_id}（{gesture_name}），预测手势: {pred_label + 1}（{GESTURE_LIST[pred_label]}）")

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

    return convert_numpy_arrays(features)

def convert_numpy_arrays(obj):
    """递归转换numpy数组为Python原生类型"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_arrays(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_numpy_arrays(value) for key, value in obj.items()}
    return obj

# 无需修改，调用链自动切换为UDP采集
