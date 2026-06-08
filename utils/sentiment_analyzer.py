from typing import Optional, Dict, Any, List
import re

import requests
import openai
from config import CONFIGS


class AIClientManager:
    """AI客户端管理器"""

    def __init__(self):
        self.clients = {}
        self.current_client = None

    def initialize_client(self, client_type: str, config: Dict[str, Any]) -> tuple[bool, str]:
        """初始化AI客户端 — 通过 GET /models 端点验证连接"""
        try:
            base_url = config.get("base_url", "http://localhost:11434/v1/")
            model_name = config.get("model", "")

            # 设置 openai 全局配置（用于后续的 chat.completions 调用）
            openai.api_key = config.get("api_key", "")
            openai.base_url = base_url
            self.current_client = client_type

            # 通过 /models 端点快速检测服务可用性（不消耗 token）
            return self._test_connection(base_url, model_name)

        except Exception as e:
            print(f"初始化AI客户端失败: {e}")
            return False, str(e)

    @staticmethod
    def _test_connection(base_url: str, model_name: str) -> tuple[bool, str]:
        """
        通过 GET /models 检测 API 可用性。

        相比发送 chat completion 消息的方式：
        - 几乎即时返回，不受模型推理速度影响
        - 不消耗 token
        - 同时可以验证目标模型是否在可用列表中
        """
        # 构建 models 端点 URL
        url = base_url.rstrip("/") + "/models"

        try:
            resp = requests.get(url, timeout=8)
            if resp.status_code != 200:
                return False, f"服务返回状态码 {resp.status_code}"

            data = resp.json()

            # 尝试从响应中提取模型列表
            models = _extract_model_list(data)
            if models is None:
                # 无法解析模型列表，但至少服务可达
                return True, ""

            if not models:
                return False, "服务未返回可用模型"

            # 检查目标模型是否在列表中
            if model_name and not _model_in_list(model_name, models):
                return False, f"模型 '{model_name}' 不在可用列表中（可用: {', '.join(models[:5])}{'...' if len(models) > 5 else ''}）"

            print(f"[AI] 连接成功，可用模型 {len(models)} 个")
            return True, ""

        except requests.Timeout:
            return False, "连接超时（请确认服务已启动）"
        except requests.ConnectionError:
            return False, f"无法连接到 {url}（请确认服务地址和端口）"
        except Exception as e:
            return False, f"连接测试异常: {e}"


def _extract_model_list(data: dict) -> Optional[list[str]]:
    """
    从 /models 响应中提取模型名称列表。
    兼容不同服务商的响应格式：
    - OpenAI: {"data": [{"id": "gpt-4", ...}, ...]}
    - Ollama: {"models": [{"name": "llama2:latest", ...}, ...]}
    - LM Studio: {"data": [{"id": "model-name", ...}, ...]}
    """
    # OpenAI / LM Studio 格式
    if "data" in data and isinstance(data["data"], list):
        return [item["id"] for item in data["data"] if isinstance(item, dict) and "id" in item]

    # Ollama 格式
    if "models" in data and isinstance(data["models"], list):
        return [item["name"] for item in data["models"] if isinstance(item, dict) and "name" in item]

    return None


def _model_in_list(model_name: str, models: list[str]) -> bool:
    """检查模型名是否在列表中（支持部分匹配，兼容 ollama 的 name:tag 格式）"""
    for m in models:
        if model_name == m:
            return True
        # Ollama 模型名格式: "name:tag"，检查 name 部分
        if ":" in m and model_name == m.split(":")[0]:
            return True
    return False


class SentimentAnalyzer:
    def __init__(self):
        self.client_manager = AIClientManager()
        self.is_initialized = False
        self.selected_emotion = None  # 在 generate_image 里显示选择的表情

    def initialize(self, client_type: str, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        初始化情感分析器。
        通过 /models 端点验证连接（不发消息，不消耗 token）。
        """
        try:
            success, error_msg = self.client_manager.initialize_client(client_type, config)

            if success:
                self.is_initialized = True
                print(f"[AI] {client_type} 情感分析器初始化成功")
                return True, ""
            else:
                self.is_initialized = False
                print(f"[AI] {client_type} 客户端初始化失败: {error_msg}")
                return False, error_msg

        except Exception as e:
            print(f"[AI] 初始化失败: {e}")
            self.is_initialized = False
            return False, str(e)

    def _send_request_with_prompt(self, message: str, custom_prompt: str = None) -> str:
        """发送请求到对应的API，可使用自定义提示词"""
        prompt = custom_prompt if custom_prompt is not None else "请任意回复"

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ]

        # 获取模型配置
        models = CONFIGS.get_available_models()
        current_client = self.client_manager.current_client
        model_name = models[current_client]["model"] if current_client in models else "deepseek-chat"

        response = openai.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.2,
            stream=False
        )

        return response.choices[0].message.content.strip()

    def analyze_sentiment_with_options(self, text: str, options: List[str]) -> Optional[str]:
        """
        分析文本并从给定选项中选择最匹配的一项

        Args:
            text: 用户输入文本
            options: 可选的表情/情感列表

        Returns:
            选中的选项，如果失败返回第一个选项
        """
        if not self.client_manager.current_client:
            print("未设置AI客户端，请先调用initialize函数")
            return None

        if not options:
            print("没有提供选项列表")
            return None

        try:
            options_str = ', '.join(options)
            custom_prompt = f"""你是一个聊天文本情感分析助手。请分析用户输入文本的情感，并从以下选项列表中选择最接近的一个能表现这个情感的动作、表情等内容的选项：[{options_str}]。

    规则：
    1. 只返回选项中的词汇，不要添加其他内容
    2. 无法判断或无内容时返回第一个选项
    3. 选项列表总是以最新的为准

    请开始分析随后的用户输入："""

            response = self._send_request_with_prompt(text, custom_prompt)
            print(f"AI原始回复: {response}")

            selected_option = self._extract_option(response, options)
            return selected_option if selected_option else (options[0] if options else None)

        except Exception as e:
            print(f"情感分析请求失败: {e}")
            return options[0] if options else None

    @staticmethod
    def _extract_option(response: str, options: List[str]) -> Optional[str]:
        """从AI回复中提取选项"""
        cleaned_response = response.strip()

        # 直接匹配（完全匹配）
        for option in options:
            if option == cleaned_response:
                return option

        # 包含匹配
        for option in options:
            if option in cleaned_response:
                return option

        # 忽略大小写匹配
        for option in options:
            if option.lower() in cleaned_response.lower():
                return option

        return None
