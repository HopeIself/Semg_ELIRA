"""main.py - 康复训练主控流程"""

import os
import json
import logging
import time
from typing import Any, List, Dict
import pandas as pd
from deepseek import DeepSeekSession
from volcano import VolcanoSession
from tongyi import TongyiSession

from EMG_config import run1, run_training, run_prediction, ACTION_MAP
import pyttsx3
from video import play_video  # 假设你有一个video.py文件处理视频播放

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# os.environ["DEEPSEEK_API_KEY"] = "sk-24fa19bacfaa41c1a9c70bbf98b3800f"
# API_KEY_ENV = "DEEPSEEK_API_KEY"
NORMALIZATION_FACTOR = 1.0


AI_MODELS = {
    "deepseek": {
        "name": "DeepSeek",
        "session_class": DeepSeekSession,
        "env_var": "DEEPSEEK_API_KEY",
        "default_key": "sk-24fa19bacfaa41c1a9c70bbf98b3800f"  # 如果需要可以设置默认密钥
    },
    "tongyi": {
        "name": "通义千问",
        "session_class": TongyiSession,  # 需要实现这个类
        "env_var": "TONGYI_API_KEY",
        "default_key": "sk-3b2b5fd8fd2e42fc8d53541b595095b5"
    },
    "doubao": {
        "name": "豆包",
        "session_class": VolcanoSession,  # 需要实现这个类
        "env_var": "DOUBAO_API_KEY",
        "default_key": "7e4f2567-ca82-442e-b179-1f034177b4dd"
    }
}
def text_to_speech(text: str) -> None:
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def select_ai_model():
    print("请选择要使用的AI模型：")
    for idx, (model_id, model_info) in enumerate(AI_MODELS.items(), 1):
        print(f"{idx}. {model_info['name']}")
    
    while True:
        try:
            choice = int(input("请输入选项编号: "))
            if 1 <= choice <= len(AI_MODELS):
                selected_model = list(AI_MODELS.keys())[choice-1]
                return selected_model
            else:
                print(f"请输入1-{len(AI_MODELS)}之间的数字")
        except ValueError:
            print("请输入有效的数字")

def get_ai_session(model_id):
    model_info = AI_MODELS[model_id]
    
    # 尝试从环境变量获取API密钥
    api_key = os.getenv(model_info["env_var"])
    
    # 如果环境变量没有设置，使用默认密钥或提示用户输入
    if not api_key:
        if model_info["default_key"]:
            api_key = model_info["default_key"]
            print(f"使用默认的{model_info['name']}密钥")
        else:
            api_key = input(f"请输入{model_info['name']}的API密钥: ")
    
    # 创建会话实例
    session_class = model_info["session_class"]
    return session_class(api_key=api_key)


def extract_action_ids(plan_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    actions = plan_response.get("actions", [])
    # 增加动作名称映射
    return [
        {
            "action_id": a.get("action_id", -1),
            "action_name": ACTION_MAP.get(a.get("action_id", -1), "未知动作"),
            "time": a.get("time", 5)
        }
        for a in actions if isinstance(a, dict)
    ]


def calculate_average_amount(features: List[float]) -> float:
    if len(features) < 2:
        return features[0] / NORMALIZATION_FACTOR if features else 0.5
    sorted_features = sorted(features, reverse=True)
    avg = (sorted_features[0] + sorted_features[1]) / 2
    return avg / NORMALIZATION_FACTOR


def request_plan(session: DeepSeekSession, avg: float) -> Dict[str, Any]:
    # 确保avg是Python原生float类型
    avg = float(avg)
    return session.send_input({"average_amount": avg})


def request_feedback(session: DeepSeekSession, action_id: int, feature_vector: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "type": "feedback",
        "action_id": action_id,
        **feature_vector
    }
    return session.send_input(payload)

def save_report_to_excel(report_response: dict, filename: str = "rehab_report.xlsx"):
    # 先确认 response 里有动作评估列表
    action_evals = report_response.get("action_evaluations", [])
    if not action_evals:
        print("无动作评估数据，无法生成Excel")
        return

    # 准备列表，存储每行数据
    rows = []
    for action in action_evals:
        row = {
            "动作ID": action.get("action_id", ""),
            "结果": action.get("result", ""),
            "评分": action.get("score", 0.0),
            "评语": action.get("comment", ""),
            "建议调整-时长(分钟)": action.get("suggested_adjustment", {}).get("time", ""),
            "建议调整-日训练频率(次)": action.get("suggested_adjustment", {}).get("daily_frequency", "")
        }
        rows.append(row)

    # 转成DataFrame
    df = pd.DataFrame(rows)

    # 写入Excel
    df.to_excel(filename, index=False)
    print(f"Excel文件已保存：{filename}")
    text_to_speech(f"康复训练报告已保存为 {filename}。请查看。")

def main() -> None:

    selected_model = select_ai_model()
    session = get_ai_session(selected_model)

    # choice = input("是否开始训练？(Y/N): ").strip().upper()
    # if choice != 'Y':
    #     print("已退出训练流程。")
    #     return

    # print("是否需要教学视频？(Y/N): ", end="")
    # choice = input().strip().upper()
    # if choice == 'Y':
    #     print("请观看教学视频。")
    #     video_player = play_video("training_video.mp4", width=800, height=600, title="康复训练教学视频")
    # else:
    #     print("跳过教学视频。")

    logger.info("采集 5 秒肌电信号以评估握力...")
    text_to_speech("请开始采集肌电信号，持续5秒钟。")
    emg_values = run1()
    logger.info("归一化 emg_values: %.4f", emg_values)

    plan_response = request_plan(session, emg_values)
    print("🤖 AI 训练计划:", plan_response.get("message", "无计划信息"))
    text_to_speech(plan_response.get("message", "无计划信息"))
    actions = extract_action_ids(plan_response)
    text_to_speech("训练计划已生成，请准备开始训练。")
    training_result = run_training(actions)

    print("\n=== 训练结果 ===")
    print("格式: [动作编号, RMS, 波形长度, 斜率符号变化次数, AR系数(8个), 平均频率, 平均功率]")
    for row in training_result:
        print(row)
    print("===============\n")
    
    # 确保training_result已经是Python原生类型
    with open("training_record.json", "w", encoding="utf-8") as f:
        json.dump(training_result, f, indent=2, ensure_ascii=False)

    session.send_input({"type": "summary", "record": training_result})

    # 存储康复训练过程中的特征值
    rehabilitation_results = []
    
    # 引导用户执行每个动作，进行实时识别与反馈
    index = 0
    retry_count = 0  # 识别率不足的重试计数
    fail_count = 0   # 动作未达标的连续计数
    
    while index < len(actions):
        action = actions[index]
        action_id = action["action_id"]
        action_name = action["action_name"]
        duration = action["time"]

        print(f"➡️ 开始执行动作 {action_name}（ID: {action_id}）")
        # print(f"当前已训练的手势列表: {GESTURE_LIST}")  # 添加这行来显示当前可用的手势列表

        all_pred_results = []
        for _ in range(duration):
            try:
                pred_result = run_prediction(action)
                all_pred_results.append(pred_result)
                time.sleep(0.8)
            except ValueError as e:
                print(f"预测出错: {e}")
                break

        match_count = sum(1 for row in all_pred_results if row[0] == 1)
        success_rate = match_count / len(all_pred_results)
        print(f"识别成功率: {success_rate:.2%}")

        if success_rate >= 0.10:
            retry_count = 0  # 重置重试计数

            # 计算最佳特征值（从识别成功的样本中获取最大值）
            success_results = [row for row in all_pred_results if row[0] == 1]
            if success_results:  # 确保有成功的样本
                avg_feature = {
                    "rms": float(max(row[1] for row in success_results)),
                    "waveform_length": float(max(row[2] for row in success_results)),
                    "slope_sign_changes": float(max(row[3] for row in success_results)),
                    "ar_coeff": [
                        float(max(row[i] for row in success_results))
                        for i in range(4, 12)
                    ],
                    "mean_frequency": float(max(row[-2] for row in success_results)),
                    "mean_power": float(max(row[-1] for row in success_results))
                }
            else:  # 如果没有成功的样本，使用所有样本中的最大值
                avg_feature = {
                    "rms": float(max(row[1] for row in all_pred_results)),
                    "waveform_length": float(max(row[2] for row in all_pred_results)),
                    "slope_sign_changes": float(max(row[3] for row in all_pred_results)),
                    "ar_coeff": [
                        float(max(row[i] for row in all_pred_results))
                        for i in range(4, 12)
                    ],
                    "mean_frequency": float(max(row[-2] for row in all_pred_results)),
                    "mean_power": float(max(row[-1] for row in all_pred_results))
                }

            # 保存康复训练结果
            rehabilitation_results.append({
                "action_id": action_id,
                "rehabilitation_features": avg_feature
            })

            feedback = request_feedback(session, action_id, avg_feature)
            print("🧠 AI反馈:", feedback.get("message", "无反馈"))
            text_to_speech(feedback.get("message", "无反馈"))

            if feedback.get("result_id") == 9:
                print("🎉 训练提前结束，达到最佳结果！")
                break
            elif feedback.get("result_id", 0) >= 4:
                index += 1
                fail_count = 0  # 重置未达标计数
            else:
                print("⚠️ 动作未达标，请再做一次。")
                fail_count += 1
                if fail_count >= 5:
                    print("\n⚠️ 连续5次动作未达标，建议休息调整后再继续。")
                    break
        else:
            retry_count += 1
            if retry_count >= 5:
                print("\n⚠️ 连续5次识别成功率不足，今天可能状态不佳。")
                print("建议休息一下，调整状态后再继续训练。")
                text_to_speech("建议休息一下，调整状态后再继续训练。")
                break
            print("⚠️ 识别成功率不足（<75%），请再试一次。")
            text_to_speech("识别成功率不足，请再试一次。")

    from datetime import datetime

    # 当前时间
    now = datetime.now().strftime("%Y-%m-%d")

    # 确定训练状态
    completed_all_actions = "true" if index >= len(actions) else "false"
    interrupted = "true" if retry_count >= 5 or fail_count >= 5 else "false"
    early_optimal_achieved = "true" if any(r.get("result_id") == 9 for r in rehabilitation_results) else "false"

    # 准备初始训练数据
    initial_training_data = []
    for r in rehabilitation_results:
        if r.get("initial_features"):
            features = r["initial_features"]
            initial_training_data.append({
                "action_id": r["action_id"],
                "features": {
                    "rms": features.get("rms", 0.0),
                    "waveform_length": features.get("waveform_length", 0.0),
                    "slope_sign_changes": features.get("slope_sign_changes", 0.0),
                    "ar_coefficients": features.get("ar_coefficients", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                    "mean_frequency": features.get("mean_frequency", 0.0),
                    "mean_power": features.get("mean_power", 0.0)
                }
            })

    # 准备康复训练数据
    rehab_training_data = []
    for r in rehabilitation_results:
        if r.get("rehabilitation_features"):
            features = r["rehabilitation_features"]
            rehab_training_data.append({
                "action_id": r["action_id"],
                "features": {
                    "rms": features.get("rms", 0.0),
                    "waveform_length": features.get("waveform_length", 0.0),
                    "slope_sign_changes": features.get("slope_sign_changes", 0.0),
                    "ar_coefficients": features.get("ar_coefficients", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
                    "mean_frequency": features.get("mean_frequency", 0.0),
                    "mean_power": features.get("mean_power", 0.0)
                }
            })

    #构建最终报告结构
    final_report = {
        "all_amount": {
            "patient_id": "anonymous_001",
            "training_status": {
                "completed_all_actions": completed_all_actions,
                "interrupted": interrupted,
                "early_optimal_achieved": early_optimal_achieved
            },
            "initial_training_data": initial_training_data,
            "rehab_training_data": rehab_training_data
        }
    }


    # 输出确认信息
    # print("\n=== 发送给AI的康复报告数据（新版格式） ===")
    # print(json.dumps(final_report, indent=2, ensure_ascii=False))

    # 发送报告
    # 注意将report_response = session.send_input(final_report) 修改为符合deepseek格式的请求
    report_response = session.send_input({"user": json.dumps(final_report)})
    # print("\n📋 康复报告生成结果:", report_response.get("message", "无报告信息"))
    save_report_to_excel(report_response)

    # if retry_count >= 5 or fail_count >= 5:
    #     print("\n🌙 训练提前结束，请好好休息。明天再来继续加油！")
    #     text_to_speech("训练提前结束，请好好休息。明天再来继续加油！")
    # else:
    #     print("训练流程结束。")
    #     text_to_speech("训练流程已结束。请查看康复训练报告。")

if __name__ == "__main__":
    main()
