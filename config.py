"""配置管理模块"""
import os
from typing import Dict, Any, Optional
import yaml
import json
from sys import platform
from path_utils import get_resource_path, ensure_path_exists, get_background_list
from image_processor import update_dll_gui_settings, update_style_config, clear_cache

class StyleConfig:
    """样式配置类"""
    
    def __init__(self):
        self.default_config = self._load_default_style_config()
        if self.default_config:
            default = self.default_config.get("default", {})
            # 设置属性
            for key, value in default.items():
                setattr(self, key, value)

    def _load_default_style_config(self):
        """从 defaultstyle.yml 加载默认样式配置"""
        try:
            filepath = get_resource_path(os.path.join("config", "defaultstyle.yml"))
            if filepath:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                print(f"警告：默认样式文件不存在: {filepath}")
                return None
        except Exception as e:
            print(f"加载默认样式配置失败: {e}")
            return None

class ConfigLoader:
    """配置加载器"""
    
    def __init__(self):
        self.AUTO_PASTE_IMAGE = True
        self.AUTO_SEND_IMAGE = True
        self.ASSETS_PATH = get_resource_path("assets")

        # 规范化平台键
        self.platform = platform
        if platform.startswith('win'):
            self.platform = 'win32'
        elif platform == 'darwin':
            self.platform = 'darwin'
        else:
            self.platform = 'win32'

        # 情感匹配相关
        # self.emotion_list = ["平静", "喜悦", "喜爱", "惊讶", "困惑", "无语", "悲伤", "愤怒", "恐惧"]

        # 状态变量(为None时为随机选择,否则为手动选择) 这两个需要移除
        self.selected_emotion = None
        self.selected_background = None
        
        # 样式配置
        self.style_configs = {}
        self.current_style = "default"
        self.style = StyleConfig()

        # 加载版本信息
        self.version_info = self._load_yaml_file("version.yml")
        # 设置版本号属性
        self.version = self.version_info["version"] # 需要存在version.yml文件

        # 配置加载
        from utils.chara_loader import load_all_characters
        self.mahoshojo = load_all_characters()
        self.keymap = self._load_config("keymap")
        self.process_whitelist = self._load_config("process_whitelist")
        self.gui_settings = self._load_config("settings")

        # 确保enabled只有在display为True时才可能为True
        sm = self.gui_settings["sentiment_matching"]
        sm["enabled"] &= sm["display"]
        self.ai_models = self.gui_settings.get("sentiment_matching", {}).get("model_configs", {})
        
        # 角色和背景列表
        self.background_list = get_background_list()
        self.character_list = list(self.mahoshojo.keys())

        # 加载样式配置
        self._load_style_configs()
        
        # 加载psd信息
        self.psd_meta = {}
        self.psd_surface_cache = {}
        self._load_psd_if_needed()

    def _load_psd_if_needed(self):
        """遍历角色，遇到 emotion_count==0 就去读同名 psd"""
        from utils.psd_utils import inspect_psd
        for chara_id, meta in self.mahoshojo.items():
            if meta.get("emotion_count", 0) == 0:          # PSD 模式
                psd_file = os.path.join(self.ASSETS_PATH, "chara", chara_id, f"{chara_id}.psd")
                if os.path.isfile(psd_file):
                    self.psd_meta[chara_id] = inspect_psd(psd_file)
                else:
                    print(f"[WARN] PSD文件不存在: {psd_file}")

    def get_psd_info(self, chara_id):
        """外部统一入口：返回该角色的 PSD 解析 dict，没有就返回 None"""
        return self.psd_meta.get(chara_id)

    def _get_current_character_from_layers(self):
        """从角色图层组件获取当前角色（第一个非固定角色的图层）"""
        preview_style = self.style_configs[self.current_style]
        if not preview_style or 'image_components' not in preview_style:
            return self.character_list[1] if len(self.character_list) > 1 else self.character_list[0]
        # 查找第一个角色组件
        for component in preview_style['image_components']:
            if component.get("type") == "character":
                # 如果不使用固定角色，返回该角色的名称
                if not component.get("use_fixed_character", False):
                    return component.get("character_name", self.character_list[1] if len(self.character_list) > 1 else self.character_list[0])
                # 如果使用固定角色，返回固定角色的名称
                else:
                    return component.get("character_name", self.character_list[1] if len(self.character_list) > 1 else self.character_list[0])
        
        # 如果没有找到角色组件，返回默认角色
        return self.character_list[1] if len(self.character_list) > 1 else self.character_list[0]

    def get_sorted_preview_components(self):
        """获取排序后的图片组件列表（按图层顺序）"""
        import copy
        style = copy.deepcopy(self.style_configs[self.current_style])
        if style and 'image_components' in style:
            components = style["image_components"]
            return sorted(components, key=lambda x: x.get("layer", 0))
        return []
    
    def apply_style(self, style_name: str):
        """应用指定的样式配置"""
        if style_name in self.style_configs:
            style_data = self.style_configs[style_name]

            self.current_style = style_name

            clear_cache()

            # 更新样式对象
            for key, value in style_data.items():
                if hasattr(self.style, key):
                    setattr(self.style, key, value)
            
            # 如果使用角色颜色作为强调色，更新强调色
            if not self.update_bracket_color_from_character():
                update_style_config(self.style)
            
            # 保存上次选择的样式到GUI设置
            self.gui_settings["last_style"] = style_name
            self.save_gui_settings()

    def update_style(self, style_name: str, style_data: Dict[str, Any]):
        """更新样式配置"""
        if style_name in self.style_configs:
            if self.style_configs[style_name] == style_data:
                return False

            # 确保有image_components字段
            if "image_components" not in style_data:
                style_data["image_components"] = self.style_configs[style_name].get("image_components", [])
            
            self.style_configs[style_name] = style_data
            
            # 如果更新的是当前样式，立即应用
            if self.current_style == style_name:
                self.apply_style(style_name)
        
            return self._save_yaml_file("styles.yml", self.style_configs)
    
    def _load_style_configs(self):
        """加载样式配置"""
        # 加载styles.yml文件
        styles_data = self._load_yaml_file("styles.yml") or {}
        
        if not styles_data:
            # 如果没有样式配置，创建默认配置
            styles_data = {"default": self.style.default_config.get("default", {})}
            self._save_yaml_file("styles.yml", styles_data)
        
        self.style_configs = styles_data
        self.current_style = self.gui_settings.get("last_style","default")
        
        # 应用当前样式
        self.apply_style(self.current_style)
    
    def update_bracket_color_from_character(self):
        """根据当前角色的文本颜色更新强调色"""
        if not self.style.use_character_color:
            return False
        
        character_name = self.get_character()
        print("当前角色：", character_name)  # 调试输出
        if character_name in self.mahoshojo and self.mahoshojo[character_name]["text"]:
            # 获取第一个文本配置的颜色
            first_config = self.mahoshojo[character_name]["text"][0]
            font_color = first_config.get("font_color", (255, 255, 255))
            # 将RGB转换为十六进制
            self.style.bracket_color = f"#{font_color[0]:02x}{font_color[1]:02x}{font_color[2]:02x}"
            # 单独更新括号颜色
            update_style_config(self.style)
            return True
        return False

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """递归合并两个字典，override 中的值优先但不会删除 base 中的键"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigLoader._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _load_config(self, config_type: str, *args) -> Any:
        """
        通用配置加载函数
        
        Args:
            config_type: 配置类型，支持: 'keymap', 'process_whitelist', 'settings'
            *args: 额外参数，如平台类型或配置键名
        
        Returns:
            配置数据
        """
        config_list = ["keymap", "process_whitelist", "settings"]
        if config_type not in config_list:
            raise ValueError(f"不支持的配置类型: {config_type}")
        
        # 加载配置文件
        config = self._load_yaml_file(f"{config_type}.yml")
        
        if config_type in ["keymap", "process_whitelist"]:
            # 处理平台特定配置
            if config:
                config = config.get(self.platform, {})
            else:
                config = self._get_default_setting(config_type)
                if config_type == "keymap":
                    self._save_yaml_file("keymap.yml", {self.platform: config})
        elif config_type == "settings":
            # 处理settings配置，确保所有字段都存在
            default_settings = self._get_default_setting("settings")
            if config:
                # 深度合并：default 提供缺失键，文件值优先
                config = self._deep_merge(default_settings, config)
            else:
                config = default_settings
                self.gui_settings = config
                self.save_gui_settings()
        
        return config
    
    def _get_default_setting(self, config_type: str) -> Dict[str, Any]:
        """获取默认设置"""
        # print(f"获取默认配置：{config_type}")

        if config_type == "settings":
            return {
                "cut_settings": {
                    "cut_mode": "全选剪切"
                },
                "image_compression": {
                    "pixel_reduction_enabled": True,
                    "pixel_reduction_ratio": 40
                },
                "quick_characters": {
                    "character_1": "ema",
                    "character_2": "hiro", 
                    "character_3": "sherry",
                    "character_4": "yuki",
                    "character_5": "meruru",
                    "character_6": "reia"
                },
                "sentiment_matching": {
                    "display": False,
                    "enabled": False,
                    "ai_model": "ollama",
                    "model_configs": {
                        "chatGPT": {
                            "api_key": '',
                            "base_url": "https://api.openai.com/v1/",
                            "model": "gpt-3.5-turbo"
                        },
                        "deepseek": {
                            "api_key": '',
                            "base_url": "https://api.deepseek.com",
                            "model": "deepseek-chat"
                        },
                        "ollama": {
                            "api_key": '',
                            "base_url": "http://localhost:11434/v1/",
                            "model": "OmniDimen"
                        },
                        "lmstudio": {
                            "api_key": '',
                            "base_url": "http://localhost:1234/v1/",
                            "model": ""
                        }
                    }
                }
            }
        elif config_type == "keymap":
            if self.platform == "win32":
                return {
                    "start_generate": "<ctrl>+e",
                    "next_character": "<ctrl>+<shift>+l",
                    "prev_character": "<ctrl>+<shift>+j",
                    "next_emotion": "<ctrl>+<shift>+o",
                    "prev_emotion": "<ctrl>+<shift>+u",
                    "next_background": "<ctrl>+<shift>+k",
                    "prev_background": "<ctrl>+<shift>+i",
                    "toggle_listener": "<ctrl>+<alt>+p",
                    "character_1": "<ctrl>+1",
                    "character_2": "<ctrl>+2",
                    "character_3": "<ctrl>+3",
                    "character_4": "<ctrl>+4",
                    "character_5": "<ctrl>+5",
                    "character_6": "<ctrl>+6"
                }
            elif self.platform == "darwin":
                return {
                        "start_generate": "<cmd>+e",
                        "next_character": "<cmd>+<shift>+l",
                        "prev_character": "<cmd>+<shift>+j",
                        "next_emotion": "<cmd>+<shift>+o",
                        "prev_emotion": "<cmd>+<shift>+u",
                        "next_background": "<cmd>+<shift>+k",
                        "prev_background": "<cmd>+<shift>+i",
                        "toggle_listener": "<cmd>+<alt>+p",
                        "character_1": "<cmd>+1",
                        "character_2": "<cmd>+2",
                        "character_3": "<cmd>+3",
                        "character_4": "<cmd>+4",
                        "character_5": "<cmd>+5",
                        "character_6": "<cmd>+6"
                    }
        else:
            return {}

    def _load_yaml_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """通用YAML文件加载函数"""
        filepath = get_resource_path(os.path.join("config", filename))
        
        if not filepath:
            return None
        
        try:
            with open(filepath, 'r', encoding="utf-8") as fp:
                return yaml.safe_load(fp) or {}
        except Exception as e:
            print(f"加载配置文件 {filename} 失败: {e}")
            return None
    
    def _save_yaml_file(self, filename: str, data: Dict[str, Any]) -> bool:
        """通用YAML文件保存函数"""
        try:
            filepath = ensure_path_exists(get_resource_path(os.path.join("config", filename)))
            
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            return True
        except Exception as e:
            print(f"保存配置文件 {filename} 失败: {e}")
            return False

    def get_character(self, index: str | None = None, full_name: bool = False) -> str:
        """获取角色名称"""
        if index is not None:
            return self.mahoshojo[index]["full_name"] if full_name else index
        else:
            # 直接返回 当前角色
            chara = self._get_current_character_from_layers()
            return self.mahoshojo[chara]["full_name"] if full_name else chara
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """获取可用模型配置"""
        # 直接从配置中获取，无需额外处理
        model_configs = self.gui_settings.get("sentiment_matching", {}).get("model_configs", {})
        
        # 构建模型信息字典
        available_models = {}
        model_descriptions = {
            "ollama": "本地运行的Ollama服务",
            "deepseek": "DeepSeek在线API",
            "chatGPT": "OpenAI ChatGPT服务",
            "lmstudio": "本地运行的LM Studio服务"
        }
        
        for model_type, model_config in model_configs.items():
            available_models[model_type] = {
                "name": model_type.capitalize(),
                "base_url": model_config.get("base_url", ""),
                "api_key": model_config.get("api_key", ""),
                "model": model_config.get("model", ""),
                "description": model_config.get("description", model_descriptions.get(model_type, f"{model_type} AI服务"))
            }
        
        return available_models
        
    def save_keymap(self, new_hotkeys=None):
        """保存快捷键设置到keymap.yml"""
        if new_hotkeys is None:
            return False
            
        # 加载现有配置
        keymap_data = self._load_yaml_file("keymap.yml") or {self.platform: self._get_default_setting("keymap")}
        
        # 检查是否有变化
        current_hotkeys = keymap_data.get(self.platform, {})
        have_change=False
        for key,value in new_hotkeys.items():
            if current_hotkeys.get(key,None) != value:
                have_change = True
                break
        if not have_change:
            return False

        # 合并新的快捷键设置到当前平台
        if self.platform not in keymap_data:
            keymap_data[self.platform] = {}
        keymap_data[self.platform] |= new_hotkeys

        CONFIGS.keymap = keymap_data[self.platform]

        # 保存回文件
        return self._save_yaml_file("keymap.yml", keymap_data)

    def save_process_whitelist(self, processes):
        """保存进程白名单"""
        # 加载现有配置
        existing_data = self._load_yaml_file("process_whitelist.yml") or {}
        
        # 检查是否有变化
        current_processes = existing_data.get(self.platform, [])
        if sorted(processes) == sorted(current_processes):
            return False
        
        # 更新当前平台的白名单
        existing_data[self.platform] = processes
        CONFIGS.process_whitelist = processes

        # 保存回文件
        return self._save_yaml_file("process_whitelist.yml", existing_data)
        
    def save_gui_settings(self):
        """保存GUI设置到settings.yml"""
        # 加载现有配置
        existing_data = self._load_yaml_file("settings.yml") or {}
        
        # 没有变化就返回个False
        if json.dumps(existing_data, sort_keys=True) == json.dumps(self.gui_settings, sort_keys=True):
            return False
        
        # 新设置到现有数据中
        existing_data |= self.gui_settings
        
        update_dll_gui_settings(self.gui_settings)
        # 保存回文件
        return self._save_yaml_file("settings.yml", existing_data)

    def get_program_info(self) -> Dict[str, Any]:
        """获取程序信息"""
        program_info = self.version_info["program"]
        return {
            "version": self.version,
            "author": program_info["author"],
            "description": program_info["description"],
            "github": program_info["github"],
        }

    def get_version_history(self) -> list:
        """获取版本历史"""
        return self.version_info.get("history", [])

CONFIGS = ConfigLoader()