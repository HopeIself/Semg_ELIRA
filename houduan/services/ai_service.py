
"""
AI服务模块: 处理AI模型的选择和交互
"""
import os
from typing import Dict, Any

# 导入不同的AI模型会话类
from models.deepseek_model import DeepSeekSession
from models.tongyi_model import TongyiSession
from models.volcano_model import VolcanoSession

# 定义可用的AI模型
AI_MODELS = {
    "DeepSeek": {
        "name": "DeepSeek",
        "session_class": DeepSeekSession,
        "env_var": "DEEPSEEK_API_KEY",
        "default_key": "sk-24fa19bacfaa41c1a9c70bbf98b3800f"  # 如果需要可以设置默认密钥
    },
    "通义千问": {
        "name": "通义千问",
        "session_class": TongyiSession,
        "env_var": "TONGYI_API_KEY",
        "default_key": "sk-3b2b5fd8fd2e42fc8d53541b595095b5"
    },
    "豆包": {
        "name": "豆包",
        "session_class": VolcanoSession,
        "env_var": "DOUBAO_API_KEY",
        "default_key": "c6a25fc5-a553-4eb4-9d3d-82e362b0c6ce"
    }
}

def get_available_models() -> Dict[str, Dict[str, Any]]:
    """获取所有可用的AI模型信息"""
    models_info = {}
    for model_id, model_info in AI_MODELS.items():
        models_info[model_id] = {
            "name": model_info["name"],
            "env_var": model_info["env_var"],
            "has_default_key": bool(model_info.get("default_key"))
        }
    return models_info

def select_ai_model_api(model_id: str, api_key: str = None):
    """
    选择AI模型并创建会话

    Args:
        model_id: 模型ID
        api_key: API密钥，如果为None则尝试从环境变量获取

    Returns:
        AI模型会话实例

    Raises:
        ValueError: 如果模型ID无效或无法获取API密钥
    """
    if model_id not in AI_MODELS:
        raise ValueError(f"无效的模型ID: {model_id}")

    model_info = AI_MODELS[model_id]

    # 确定API密钥
    if api_key is None:
        # 尝试从环境变量获取API密钥
        api_key = os.getenv(model_info["env_var"])

        # 如果环境变量没有设置，使用默认密钥
        if not api_key and model_info.get("default_key"):
            api_key = model_info["default_key"]

    if not api_key:
        raise ValueError(f"未提供API密钥，且环境变量{model_info['env_var']}未设置")

    # 创建会话实例
    session_class = model_info["session_class"]
    return session_class(api_key=api_key)

def get_ai_session(model_id: str):
    """
    获取AI模型会话

    Args:
        model_id: 模型ID

    Returns:
        AI模型会话实例
    """
    model_info = AI_MODELS[model_id]

    # 尝试从环境变量获取API密钥
    api_key = os.getenv(model_info["env_var"])

    # 如果环境变量没有设置，使用默认密钥
    if not api_key:
        if model_info["default_key"]:
            api_key = model_info["default_key"]
        else:
            raise ValueError(f"请提供{model_info['name']}的API密钥")

    # 创建会话实例
    session_class = model_info["session_class"]
    return session_class(api_key=api_key)
