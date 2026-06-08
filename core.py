"""魔裁文本框核心逻辑"""
from config import CONFIGS
from utils.clipboard_utils import ClipboardManager
from utils.sentiment_analyzer import SentimentAnalyzer
from image_processor import get_enhanced_loader, generate_image_with_dll, set_dll_global_config, clear_cache, update_dll_gui_settings, draw_content_auto

import time
import re
import random
import psutil
import threading
from pynput.keyboard import Key, Controller
from sys import platform
from PIL import Image
from typing import Dict, Any
from PySide6.QtCore import QObject, Signal

if platform.startswith("win"):
    try:
        import win32gui
        import win32process
    except ImportError:
        print("[red]请先安装 Windows 运行库: pip install pywin32[/red]")
        raise

def _calculate_canvas_size():
    """根据样式配置计算画布大小"""
    ratio = CONFIGS.style.aspect_ratio

    # 固定宽度为2560，根据比例计算高度
    if ratio == "5:4":
        height = 2048
    elif ratio == "16:9":
        height = 1440
    else:  # "3:1" 或默认
        height = 854
    
    return (2560, height)

class ManosabaCore(QObject):  # 继承 QObject 以支持信号
    """魔裁文本框核心类"""
    
    # 定义信号
    status_updated = Signal(str)  # 状态更新信号
    gui_notification = Signal(bool, bool, str)  # GUI通知信号(情感分析器状态)

    def __init__(self):
        super().__init__()  # 初始化 QObject
        # 初始化配置
        self.kbd_controller = Controller()
        self.clipboard_manager = ClipboardManager()

        # 情感分析器 - 简单状态管理
        self.sentiment_analyzer = SentimentAnalyzer()
        self.sentiment_enabled = False  # 功能是否启用
        self.sentiment_available = False  # 分析器是否可用
        self.current_model = CONFIGS.gui_settings.get("sentiment_matching",{}).get("ai_model", "")  # 当前模型名称
        self.force_use = {} # 强制使用表情（情感分析后使用）

        # 初始化DLL加载器
        set_dll_global_config(CONFIGS.ASSETS_PATH, min_image_ratio=0.2)
        update_dll_gui_settings(CONFIGS.gui_settings)

    def update_status(self, message: str):
        """更新状态 - 使用信号"""
        self.status_updated.emit(message)

    def _notify_gui(self, enabled, available, error_message=""):
        """通知GUI情感分析器状态变化 - 使用信号"""
        self.gui_notification.emit(enabled, available, error_message)

    def init_sentiment_analyzer(self):
        """初始化情感分析器（程序启动时调用）"""
        sentiment_settings = CONFIGS.gui_settings.get("sentiment_matching", {})
        if not sentiment_settings.get("display", False):
            # 功能不显示，直接返回
            return
        
        enabled = sentiment_settings.get("enabled", False)
        if not enabled:
            # 功能未启用，直接返回
            self._notify_gui(False, True, "")
            return

        # 如果分析器已可用，直接通知 GUI 即可（不需要重新初始化）
        if self.sentiment_available:
            self._notify_gui(True, True, "")
            self.sentiment_enabled = True
            return

        # 启动初始化（委托给 toggle_sentiment_matching，它会在后台线程中初始化）
        self.toggle_sentiment_matching(True)

    def toggle_sentiment_matching(self, enabled):
        """切换情感匹配状态"""
        model = CONFIGS.gui_settings.get("sentiment_matching",{}).get("ai_model", "")
        if model != self.current_model:
            self.current_model = model
            self.sentiment_available = False
            self.sentiment_enabled = False
            print("模型切换，情感分析器重置")

        if enabled and not self.sentiment_available:
            # 如果启用但分析器不可用，尝试初始化
            self.update_status(f"正在初始化({model})情感分析器...")
            self._notify_gui(True, False, "")

            def try_init():
                try:
                    sentiment_settings = CONFIGS.gui_settings.get("sentiment_matching", {})
                    client_type = sentiment_settings.get("ai_model", "ollama")
                    model_configs = sentiment_settings.get("model_configs", {})
                    config = model_configs.get(client_type, {})
                    
                    success,error_msg = self.sentiment_analyzer.initialize(client_type, config)
                    
                    if success:
                        self.sentiment_available = True
                        self.sentiment_enabled = True
                        self._notify_gui(True, True, "")
                    else:
                        self.sentiment_available = False
                        self.sentiment_enabled = False
                        error_msg = f"情感分析器初始化失败({error_msg})"
                        self._notify_gui(False, True, error_msg)
                        
                except Exception as e:
                    error_msg = f"初始化异常: {str(e)}"
                    self.sentiment_available = False
                    self.sentiment_enabled = False
                    self._notify_gui(False, True, error_msg)
            
            # 在后台线程中初始化
            thread = threading.Thread(target=try_init, daemon=True)
            thread.start()
        else:
            # 禁用功能或分析器已可用
            self.sentiment_enabled = enabled
            self._notify_gui(enabled, True, "")

    def test_ai_connection(self, client_type: str, config: Dict[str, Any]) -> bool:
        """测试AI连接"""
        try:
            result, error_msg = self.sentiment_analyzer.initialize(client_type, config)
            
            self.sentiment_enabled = result
            self.sentiment_available = result
            self._notify_gui(result, result, "" if result else f"{client_type}连接测试失败({error_msg})")
            return result
                
        except Exception as e:
            error_msg = f"连接测试异常: {str(e)}"
            self._notify_gui(False, False, error_msg)
            return False

    def _update_emotion_by_sentiment(self, text: str) -> bool:
        """根据文本情感更新表情 - 统一PSD和普通角色逻辑"""
        if not self.sentiment_available:
            self.update_status("情感分析器未初始化")
            return False
        
        try:
            updated = False
            self.base_msg = ""
            
            # 获取所有角色图层
            preview_components = CONFIGS.get_sorted_preview_components()
            
            for component in preview_components:
                if not component.get("enabled", True):
                    continue

                if component.get("type") == "character":
                    # 使用固定表情/固定角色的图层跳过AI情感选择
                    if component.get("use_fixed_character", False):
                        continue

                    layer_index = component.get("layer", 1)
                    character_tabs = self.gui.get_character_tab_widgets()

                    # 直接从UI获取当前可用表情列表
                    char_widget = character_tabs[layer_index]
                    if not char_widget:
                        continue
                    
                    # 获取UI中当前显示的所有可用表情
                    available_filters = char_widget.get_available_filters()
                    filters = available_filters if available_filters else char_widget.get_available_emotions()
                    if not filters:
                        continue
                    
                    # 使用统一的情感分析函数从可用表情中选择
                    selected_emotion = self.sentiment_analyzer.analyze_sentiment_with_options(text, filters)
                    
                    if selected_emotion:
                        emo = ""
                        character_name = component.get("character_name", "")
                        if not available_filters:
                            emo = selected_emotion
                        else:
                            emo_list = char_widget.get_filtered_emotions(selected_emotion)
                            if emo_list:
                                emo = random.choice(emo_list)
                        self.force_use[layer_index] = emo
                        updated = True
                        
                        # 显示更新信息
                        char_full_name = CONFIGS.mahoshojo.get(character_name, {}).get("full_name", character_name)
                        info = f"角色 {char_full_name} | 表情: {selected_emotion} |"
                        self.base_msg += info
                        print(info)
            
            return updated
                
        except Exception as e:
            self.update_status(f"情感分析失败: {str(e)}")
            return False

    def _active_process_allowed(self) -> bool:
        """校验当前前台进程是否在白名单"""
        if not CONFIGS.process_whitelist:
            return True
        
        wl = {name.lower() for name in CONFIGS.process_whitelist}

        if platform.startswith("win"):
            try:
                hwnd = win32gui.GetForegroundWindow()
                if not hwnd:
                    return False
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                name = psutil.Process(pid).name().lower()
                return name in wl
            except (psutil.Error, OSError):
                return False

        elif platform == "darwin":
            try:
                import subprocess

                result = subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events" to get name of first process whose frontmost is true',
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                name = result.stdout.strip().lower()
                return name in wl
            except subprocess.SubprocessError:
                return False

        else:
            # Linux 支持
            return True

    def compose_psd_chara(self, chara, pose, cloth, action, expr) -> int:
        """
        合成PSD角色图片并返回缓存索引
        """
        st = time.time()
        import os 
        from utils.psd_utils import compose_image
        psd_path = os.path.join(CONFIGS.ASSETS_PATH, "chara", chara, f"{chara}.psd")
        
        try:
            psd_index = compose_image(psd_path, pose, cloth, action, expr)
            print(f"PSD图片合成用时: {int((time.time() - st)*1000)}")
            return psd_index
        except Exception as e:
            print(f"PSD合成失败: {str(e)}")
            return -1

    def generate_preview(self) -> tuple:
        """生成预览图片和相关信息"""
        st = time.time()
        use_cache = get_enhanced_loader().layer_cache
        try:
            compress_layer = False

            # 获取所有组件配置
            components = CONFIGS.get_sorted_preview_components()
            
            if not components:
                print("警告：没有找到预览组件")
                return self._create_empty_preview()
            
            cp_components = []
            
            # 从图层获取当前角色（用于namebox）
            current_character_name = CONFIGS._get_current_character_from_layers()
            
            # 用于收集信息的变量
            character_info = ""
            background_info = ""

            # 关键修改：获取UI组件引用
            character_tab_widgets = {}
            background_tab_widgets = {}
            
            if hasattr(self, 'gui') and hasattr(self.gui, 'get_character_tab_widgets'):
                character_tab_widgets = self.gui.get_character_tab_widgets()
            
            if hasattr(self, 'gui') and hasattr(self.gui, 'get_background_tab_widgets'):
                background_tab_widgets = self.gui.get_background_tab_widgets()

            # 确定每个组件的具体参数
            for component in components:
                if not component.get("enabled", True):
                    continue
                
                comp_type = component.get("type")

                # 图层缓存
                if comp_type in ["background", "character"]:
                    compress_layer = False
                elif use_cache:
                    if not compress_layer:
                        cp_components.append({"use_cache": True})
                        compress_layer = True
                    continue

                # 处理组件内容
                if comp_type == "namebox":
                    # 添加角色文本配置
                    if current_character_name in CONFIGS.mahoshojo:
                        component["textcfg"] = CONFIGS.mahoshojo[current_character_name]["text"]
                        component["font_name"] = CONFIGS.mahoshojo[current_character_name]["font"]
                
                elif comp_type == "character":
                    layer_index = component.get("layer", 1)
                    ui_values = character_tab_widgets[layer_index].get_current_values()
                    if not ui_values:
                        raise ValueError("无法获取角色UI组件值")

                    character_name = ui_values.get("character_name", current_character_name)
                    psd_info = CONFIGS.get_psd_info(character_name)
                    emotion_index = ui_values.get("emotion_index", 1 if not psd_info else "表情 1")
                    use_fixed = ui_values.get("use_fixed_character", False)
                    
                    # 检查是否强制使用
                    force_use = layer_index in self.force_use.keys()
                    if force_use:
                        emotion_index = self.force_use[layer_index]
                        # component.get("emotion_index")
                        self.force_use.pop(layer_index)
                    elif not use_fixed:
                        emo_list = character_tab_widgets[layer_index].get_available_emotions()
                        random_selected_emotion = random.choice(emo_list) if emo_list else ""

                        if psd_info:
                            # PSD角色：直接使用表情名称字符串
                            emotion_index = random_selected_emotion
                        else:
                            # 普通角色：从"表情 N"格式中提取数字N
                            match = re.search(r'(\d+)', random_selected_emotion)
                            emotion_index = int(match.group(1)) if match else 1
                    
                    if psd_info:
                        pose = ui_values.get("pose", "")
                        clothing = ui_values.get("clothing")
                        action = ui_values.get("action")
                        
                        # 直接合成PSD并获取索引
                        psd_index = self.compose_psd_chara(character_name, pose, clothing, action, emotion_index)
                        
                        # 将索引存入组件，而不是图片数据
                        component["psd_index"] = psd_index
                        component["overlay"] = ""  # 清空overlay，使用psd_index
                        
                        print(f"PSD 组件: {character_name}, 姿势: {pose}, 服装: {clothing}, 动作: {action}, 表情: {emotion_index}, 索引: {psd_index}")
                        
                    component["emotion_index"] = emotion_index
                        
                    # 收集角色信息
                    character_info = f"角色: {character_name}, 表情: ({emotion_index}) |"
                    
                    # 获取角色配置
                    character_config = CONFIGS.mahoshojo.get(character_name, {})
                    component["scale1"] = float(character_config.get("scale", 1.0))
                    
                    # 设置偏移
                    offset = character_config.get("offset", (0, 0))
                    emotion_offsets_X = character_config.get("offsetX", {})
                    emotion_offsets_Y = character_config.get("offsetY", {})
                    
                    component["offset_x1"] = emotion_offsets_X.get(str(emotion_index), 0) + offset[0]
                    component["offset_y1"] = emotion_offsets_Y.get(str(emotion_index), 0) + offset[1]
                
                elif comp_type == "background":
                    # 完全从UI获取值
                    layer_index = component.get("layer", 0)
                    
                    bg_widget = background_tab_widgets[layer_index]
                    overlay = bg_widget.get_overlay_value() or ""
                    use_fixed = bg_widget.is_fixed_background()

                    print(f"背景设置: 固定: {use_fixed}, 选择: {overlay}")
                    if not (use_fixed and overlay):
                        # 使用随机背景
                        if len(CONFIGS.background_list) > 0:
                            overlay = random.choice(CONFIGS.background_list)
                    background_info = f"背景: {overlay} |"
                    component["overlay"] = overlay

                cp_components.append(component)
            
            # 使用DLL生成图像
            preview_image = generate_image_with_dll(_calculate_canvas_size(), cp_components,)
            
            get_enhanced_loader().layer_cache = True

            info = f"{character_info if character_info else ""} {background_info if background_info else ""} | 生成{"成功" if preview_image else "失败"}"
            if preview_image:
                print(f"预览生成用时: {int((time.time()-st)*1000)}ms")
            else:
                print("CPP端预览图生成失败")
            
            # 预览返回前，清掉本次用到的 PSD 图
            for comp in cp_components:
                comp.pop("__psd_image__", None)
            CONFIGS.psd_surface_cache.clear()
        except Exception as e:
            print(f"预览图生成出错: {e}")
            import traceback
            traceback.print_exc()
            preview_image, info = self._create_empty_preview()
            info = f"错误: {str(e)}"
        
        return preview_image, info

    def _create_empty_preview(self):
        """创建空的预览图像"""
        canvas_size = _calculate_canvas_size()
        preview_image = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        info = "没有找到组件配置"
        return preview_image, info

    def generate_image(self) -> str:
        """生成并发送图片"""
        if not self._active_process_allowed():
            return "前台应用不在白名单内"

        self.base_msg=""

        # 开始计时
        start_time = time.time()
        print(f"[{int((time.time()-start_time)*1000)}] 开始生成图片")

        # 清空剪贴板
        self.clipboard_manager.clear_clipboard()

        time.sleep(0.005)

        # 获取剪切模式设置
        cut_settings = CONFIGS.gui_settings.get("cut_settings", {})
        cut_mode = cut_settings.get("cut_mode", "full")
        
        # 根据剪切模式执行不同的剪切操作
        if cut_mode == "direct":
            # 手动剪切模式：不执行任何剪切操作，等待用户自行剪切
            self.kbd_controller.press(Key.ctrl)
            self.kbd_controller.press('x')
            self.kbd_controller.release('x')
            self.kbd_controller.release(Key.ctrl)
        else:
            # 执行剪切操作
            if cut_mode == "single_line":
                # 单行剪切模式：模拟 Shift+Home 选择当前行
                if platform.startswith("win"):
                    self.kbd_controller.press(Key.end)
                    self.kbd_controller.release(Key.end)
                    self.kbd_controller.press(Key.shift)
                    self.kbd_controller.press(Key.home)
                    self.kbd_controller.release(Key.home)
                    self.kbd_controller.release(Key.shift)
                    time.sleep(0.01)
                    self.kbd_controller.press(Key.ctrl)
                    self.kbd_controller.press('x')
                    self.kbd_controller.release('x')
                    self.kbd_controller.release(Key.ctrl)
                else:
                    self.kbd_controller.press(Key.shift)
                    self.kbd_controller.press(Key.home)
                    self.kbd_controller.release(Key.home)
                    self.kbd_controller.release(Key.shift)
                    time.sleep(0.01)
                    self.kbd_controller.press(Key.cmd)
                    self.kbd_controller.press('x')
                    self.kbd_controller.release('x')
                    self.kbd_controller.release(Key.cmd)
            else:
                # 全选剪切模式（默认）
                if platform.startswith("win"):
                    self.kbd_controller.press(Key.ctrl)
                    self.kbd_controller.press('a')
                    self.kbd_controller.release('a')
                    self.kbd_controller.press('x')
                    self.kbd_controller.release('x')
                    self.kbd_controller.release(Key.ctrl)
                else:
                    self.kbd_controller.press(Key.cmd)
                    self.kbd_controller.press('a')
                    self.kbd_controller.release('a')
                    self.kbd_controller.press('x')
                    self.kbd_controller.release('x')
                    self.kbd_controller.release(Key.cmd)

        print(f"[{int((time.time()-start_time)*1000)}] 开始读取剪切板")
        deadline = time.time() + 2.5
        while time.time() < deadline:
            text, image = self.clipboard_manager.get_clipboard_all()
            if (text and text.strip()) or image is not None:
                print(f"[{int((time.time()-start_time)*1000)}] 剪切板内容获取完成")
                break
            time.sleep(0.005)
        
        # 情感匹配处理
        sentiment_settings = CONFIGS.gui_settings.get("sentiment_matching", {})

        if (sentiment_settings.get("enabled", False) and self.sentiment_enabled and text.strip()):
            
            emotion_updated = self._update_emotion_by_sentiment(text)
            
            if emotion_updated:
                print(f"[{int((time.time()-start_time)*1000)}] 情感分析完成")
                # 刷新预览以显示新的表情
                self.generate_preview()
            else:
                print(f"[{int((time.time()-start_time)*1000)}] 情感分析失败")

        if text == "" and image is None:
            return "错误: 没有文本或图像"

        try:
            print(f"[{int((time.time()-start_time)*1000)}] 开始图像合成")
            
            bmp_bytes = draw_content_auto(text=text,content_image=image,)

            print(f"[{int((time.time()-start_time)*1000)}] 图片合成完成")

        except Exception as e:
            return f"生成图像失败: {e}"

        # 复制到剪贴板
        if not self.clipboard_manager.copy_image_to_clipboard(bmp_bytes):
            return "复制到剪贴板失败"
        
        print(f"[{int((time.time()-start_time)*1000)}] 图片复制到剪切板完成")

        # 等待剪贴板确认（最多等待2.5秒）
        wait = 0.01
        total = 0
        while total < 0.5:
            if self.clipboard_manager.has_image_in_clipboard():
                break
            time.sleep(wait)
            total += wait
            wait = min(wait * 1.5, 0.08)
        print(f"[{int((time.time()-start_time)*1000)}] 剪切板确认完成")

        # 自动粘贴和发送
        if CONFIGS.AUTO_PASTE_IMAGE:
            self.kbd_controller.press(Key.ctrl if platform != "darwin" else Key.cmd)
            self.kbd_controller.press("v")
            self.kbd_controller.release("v")
            self.kbd_controller.release(Key.ctrl if platform != "darwin" else Key.cmd)

            if not self._active_process_allowed():
                return "前台应用不在白名单内"
            if CONFIGS.AUTO_SEND_IMAGE:
                time.sleep(0.4)
                self.kbd_controller.press(Key.enter)
                self.kbd_controller.release(Key.enter)

                print(f"[{int((time.time()-start_time)*1000)}] 自动发送完成")
        
        # 构建状态消息
        self.base_msg += f"角色: {CONFIGS.get_character()}, 用时: {int((time.time() - start_time) * 1000)}ms"
        
        return self.base_msg