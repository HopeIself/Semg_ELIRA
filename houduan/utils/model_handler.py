
"""
模型处理模块: 提供模型训练和预测功能
"""
import os
import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Any, Tuple

# 定义CNN模型架构
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

    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))  # (N, 32, T)
        x = self.pool2(self.relu2(self.conv2(x)))  # (N, 64, T)
        x = self.pool3(self.relu3(self.conv3(x)))  # (N, 128, T)
        x = self.pool4(self.relu4(self.conv4(x)))  # (N, 256, T)

        x = x.view(x.size(0), -1)
        x = self.fc(x)  # (N, num_classes)
        return x

def predict_gesture(segment: np.ndarray, num_classes: int) -> int:
    """
    预测手势类别

    Args:
        segment: EMG信号数据, shape=(time_steps, channels)
        num_classes: 手势类别数量

    Returns:
        int: 预测的手势类别索引
    """
    # 确保模型目录存在
    model_path = "model/best_cnn_model.pth"
    if not os.path.exists(model_path):
        # 如果模型不存在，返回随机预测（仅用于测试）
        print("警告: 模型文件不存在，使用随机预测")
        return np.random.randint(0, num_classes)

    # 加载模型
    model = EMGCNN(num_channels=segment.shape[1], num_classes=num_classes)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    # 准备输入数据
    input_tensor = torch.tensor(segment, dtype=torch.float32).unsqueeze(0).permute(0, 2, 1).to(device)

    # 进行预测
    with torch.no_grad():
        logits = model(input_tensor)
        pred_label = torch.argmax(logits, dim=1).item()

    return pred_label

def train_model(train_loader, val_loader, num_channels, num_classes, epochs=100):
    """
    训练EMG模型

    Args:
        train_loader: 训练数据加载器
        val_loader: 验证数据加载器
        num_channels: 输入通道数
        num_classes: 类别数量
        epochs: 训练轮数

    Returns:
        nn.Module: 训练好的模型
    """
    model = EMGCNN(num_channels=num_channels, num_classes=num_classes)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    model.to(device)
    best_acc = 0.0

    for epoch in range(epochs):
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

        # 计算准确率
        correct = sum(1 for p, t in zip(val_preds, val_targets) if p == t)
        acc = correct / len(val_targets)

        print(f"Epoch {epoch+1}, Loss: {total_loss:.4f}, Val Acc: {acc*100:.2f}%")

        # 保存最佳模型
        if acc > best_acc:
            os.makedirs("model", exist_ok=True)
            torch.save(model.state_dict(), "model/best_cnn_model.pth")
            best_acc = acc

    # 加载最佳模型
    model.load_state_dict(torch.load("model/best_cnn_model.pth", map_location=device))
    return model
