# pyqt_setting.py
from PySide6.QtWidgets import QDialog, QDialogButtonBox
from PySide6.QtCore import Signal, QThread, QTimer
import threading
import requests
from pynput import keyboard

from ui.setting_window import Ui_SettingWindow
from config import CONFIGS


class HotkeyConfigThread(QThread):
    """热键配置线程"""
    hotkey_configured = Signal(str, str)  # key, hotkey_value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.key_name = ""
        self.original_value = ""
        self._running = True
        self._listener = None
    
    def configure_hotkey(self, key_name, original_value):
        """开始配置热键"""
        self.key_name = key_name
        self.original_value = original_value
        self._running = True
        self.start()
    
    def stop(self):
        """停止监听"""
        self._running = False
        if self._listener:
            self._listener.stop()
    
    def run(self):
        """线程运行函数"""
        key_combo = []
        
        def on_press(key):
            if not self._running:
                return False
            
            try:
                # 处理特殊键
                if hasattr(key, 'name'):
                    # 修饰键处理
                    if key.name in ['ctrl_l', 'ctrl_r', 'ctrl']:
                        key_str = '<ctrl>'
                    elif key.name in ['alt_l', 'alt_r', 'alt']:
                        key_str = '<alt>'
                    elif key.name in ['shift_l', 'shift_r', 'shift']:
                        key_str = '<shift>'
                    elif key.name in ['cmd_l', 'cmd_r', 'cmd', 'win', 'windows']:
                        key_str = '<cmd>' if CONFIGS.platform == 'darwin' else '<win>'
                    elif key.name.startswith('f') and key.name[1:].isdigit():
                        key_str = f'<{key.name}>'
                    elif key.name in ['space', 'enter', 'esc', 'tab', 'backspace', 'delete', 'insert',
                                    'pageup', 'pagedown', 'home', 'end', 'left', 'right', 'up', 'down']:
                        key_str = f'<{key.name}>'
                    else:
                        # 对于字母键，直接使用名称
                        if key.name.isalpha() and len(key.name) == 1:
                            key_str = key.name.lower()
                        else:
                            key_str = key.name
                else:
                    # 处理普通字符键
                    if hasattr(key, 'char') and key.char:
                        char_val = key.char
                        if isinstance(char_val, str) and len(char_val) == 1:
                            code = ord(char_val)
                            # Ctrl+A 到 Ctrl+Z 对应 1-26
                            if 1 <= code <= 26:
                                # 转换为对应字母
                                key_str = chr(code - 1 + ord('a'))
                            elif code >= 32:  # 可打印字符
                                key_str = char_val.lower() if char_val.isalpha() else char_val
                            else:
                                key_str = None
                        else:
                            key_str = char_val
                    else:
                        key_str = str(key)
                
                # 去重并添加到组合
                if key_str and key_str not in key_combo:
                    key_combo.append(key_str)
                    
            except Exception as e:
                print(f"按键处理错误: {e}")
        
        def on_release(key):
            # 如果已经有按键组合，停止监听
            if key_combo:
                self._running = False
                return False
            return True
        
        # 清空按键组合
        key_combo.clear()
        
        # 启动监听器
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            self._listener = listener
            listener.join()
        
        # 生成热键字符串
        if key_combo:
            # 确保修饰键在前面
            modifiers = [k for k in key_combo if k.startswith('<')]
            regular_keys = [k for k in key_combo if not k.startswith('<')]
            final_combo = modifiers + regular_keys
            hotkey_value = '+'.join(final_combo)
            
            # 发送信号
            self.hotkey_configured.emit(self.key_name, hotkey_value)
        else:
            # 如果没有按键，恢复原值
            self.hotkey_configured.emit(self.key_name, self.original_value)


class SettingWindow(QDialog):
    """设置窗口"""
    ai_test_completed = Signal(bool, str)
    
    def __init__(self, parent, core):
        super().__init__(parent)
        self.ui = Ui_SettingWindow()
        self.ui.setupUi(self)
        
        self.core = core
        self.settings_changed = False
        
        # 热键配置线程
        self.hotkey_thread = HotkeyConfigThread(self)
        self.hotkey_thread.hotkey_configured.connect(self._on_hotkey_configured)
        
        # 存储LineEdit控件引用
        self.hotkey_edits = {}
        
        # 存储ComboBox控件引用
        self.character_combos = {}
        
        # 初始化UI
        self._init_ui()

        # 连接信号槽
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        # 初始化剪切模式下拉框
        cut_settings = CONFIGS.gui_settings.get("cut_settings", {})
        cut_mode = cut_settings.get("cut_mode", "full")
        cut_mode_text = {
            "full": "全选剪切",
            "single_line": "单行剪切", 
            "direct": "直接剪切"
        }.get(cut_mode, "全选剪切")
        
        self.ui.comboBox_pasteModeSelect.addItems(["全选剪切", "单行剪切", "直接剪切"])
        index = self.ui.comboBox_pasteModeSelect.findText(cut_mode_text)
        if index >= 0:
            self.ui.comboBox_pasteModeSelect.setCurrentIndex(index)
        
        # 初始化情感匹配设置
        sentiment_settings = CONFIGS.gui_settings.get("sentiment_matching", {})
        if sentiment_settings.get("display", False):
            # 加载模型列表
            available_models = list(CONFIGS.ai_models.keys())
            self.ui.comboBox_ModelSelect.addItems(available_models)
            
            # 设置当前模型
            current_model = sentiment_settings.get("ai_model", "ollama")
            index = self.ui.comboBox_ModelSelect.findText(current_model)
            if index >= 0:
                self.ui.comboBox_ModelSelect.setCurrentIndex(index)
            
            # 初始化模型参数
            self._update_model_parameters(current_model)
            
            # 显示情感匹配设置
            self.ui.groupBox_EmoMatch.show()
        else:
            # 隐藏情感匹配设置
            self.ui.groupBox_EmoMatch.hide()
        
        # 初始化图像压缩设置
        compression_settings = CONFIGS.gui_settings.get("image_compression", {})
        self.ui.checkBox_enableImgCompression.setChecked(
            compression_settings.get("pixel_reduction_enabled", True)
        )
        ratio = compression_settings.get("pixel_reduction_ratio", 40)
        self.ui.horizontalSlider_ReductionRatio.setValue(ratio)
        self.ui.label_ReductRate.setText(f"{ratio}%")
        
        # 初始化进程白名单
        self.ui.textEdit_processList.setPlainText('\n'.join(CONFIGS.process_whitelist))
        
        # 初始化快捷键设置
        self._init_hotkey_ui()
        
        # 初始化角色快速选择
        self._init_quick_characters()
    
    def _init_hotkey_ui(self):
        """初始化快捷键UI"""
        hotkeys = CONFIGS.keymap
        
        # 映射控件名称到配置键
        hotkey_mapping = {
            'lineEdit_generateImgKey': 'start_generate',
            'lineEdit_listenerCtrlKey': 'toggle_listener',
            'lineEdit_previCharaKey': 'prev_character',
            'lineEdit_nextCharaKey': 'next_character', 
            'lineEdit_previEmoKey': 'prev_emotion',
            'lineEdit_nextEmoKey': 'next_emotion',
            'lineEdit_previBgKey': 'prev_background',
            'lineEdit_nextBgKey': 'next_background'
        }
        
        # 设置热键显示
        for control_name, config_key in hotkey_mapping.items():
            line_edit = getattr(self.ui, control_name, None)
            if line_edit:
                hotkey_value = hotkeys.get(config_key, "")
                line_edit.setText(hotkey_value)
                line_edit.setReadOnly(True)
                self.hotkey_edits[config_key] = line_edit
    
    def _init_quick_characters(self):
        """初始化角色快速选择"""
        quick_chars = CONFIGS.gui_settings.get("quick_characters", {})
        
        # 获取所有角色选项
        character_options = [""]  # 空选项
        for char_id in CONFIGS.character_list:
            full_name = CONFIGS.get_character(char_id, full_name=True)
            character_options.append(f"{full_name} ({char_id})")
        
        # 设置下拉框
        for i in range(1, 7):
            combo_name = f"comboBox_Chara{i}"
            combo = getattr(self.ui, combo_name, None)
            if combo:
                combo.addItems(character_options)
                
                # 设置当前值
                char_id = quick_chars.get(f"character_{i}", "")
                if char_id and char_id in CONFIGS.character_list:
                    display_text = f"{CONFIGS.get_character(char_id, full_name=True)} ({char_id})"
                    index = combo.findText(display_text)
                    if index >= 0:
                        combo.setCurrentIndex(index)
                
                self.character_combos[f"character_{i}"] = combo

    def _query_models(self):
        """查询 API 可用模型列表并填充下拉框"""
        url = self.ui.lineEdit_apiUrl.text().strip().rstrip("/") + "/models"

        self.ui.pushButton_query.setEnabled(False)
        self.ui.pushButton_query.setText("…")
        self.ui.comboBox_modelName.setEnabled(False)

        def query():
            try:
                resp = requests.get(url, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    from utils.sentiment_analyzer import _extract_model_list
                    models = _extract_model_list(data)
                    self._on_models_queried(models)
                else:
                    self._on_models_queried(None, f"HTTP {resp.status_code}")
            except requests.Timeout:
                self._on_models_queried(None, "查询超时")
            except requests.ConnectionError:
                self._on_models_queried(None, "无法连接")
            except Exception as e:
                self._on_models_queried(None, str(e))

        thread = threading.Thread(target=query, daemon=True)
        thread.start()

    def _on_models_queried(self, models, error=None):
        """模型查询结果回调（在主线程）"""
        self.ui.pushButton_query.setEnabled(True)
        self.ui.pushButton_query.setText("查询")
        self.ui.comboBox_modelName.setEnabled(True)

        if models is None or error:
            self.ui.comboBox_modelName.setToolTip(f"查询失败: {error}")
            return

        if not models:
            self.ui.comboBox_modelName.setToolTip("服务未返回可用模型")
            return

        current = self.ui.comboBox_modelName.currentText()

        self.ui.comboBox_modelName.blockSignals(True)
        self.ui.comboBox_modelName.clear()
        self.ui.comboBox_modelName.addItems(models)

        if current:
            idx = self.ui.comboBox_modelName.findText(current)
            if idx >= 0:
                self.ui.comboBox_modelName.setCurrentIndex(idx)
            else:
                self.ui.comboBox_modelName.setCurrentText(current)
        self.ui.comboBox_modelName.blockSignals(False)

        self.ui.comboBox_modelName.setToolTip(f"已加载 {len(models)} 个模型")
        self.settings_changed = True

    def _update_model_parameters(self, model_name):
        """更新模型参数显示"""
        if model_name not in CONFIGS.ai_models:
            return

        model_config = CONFIGS.ai_models[model_name]
        sentiment_settings = CONFIGS.gui_settings.get("sentiment_matching", {})
        model_settings = sentiment_settings.get("model_configs", {}).get(model_name, {})

        # 设置参数
        self.ui.lineEdit_apiUrl.setText(model_settings.get("base_url", model_config.get("base_url", "")))
        self.ui.lineEdit_apiKey.setText(model_settings.get("api_key", model_config.get("api_key", "")))
        # 允许手动输入，把当前模型名加入下拉列表
        self.ui.comboBox_modelName.setEditable(True)
        self.ui.comboBox_modelName.setInsertPolicy(self.ui.comboBox_modelName.InsertPolicy.NoInsert)
        current_model = model_settings.get("model", model_config.get("model", ""))
        if current_model and self.ui.comboBox_modelName.findText(current_model) < 0:
            self.ui.comboBox_modelName.addItem(current_model)
        self.ui.comboBox_modelName.setCurrentText(current_model)

    def _connect_signals(self):
        """连接信号槽"""
        # 剪切模式
        self.ui.comboBox_pasteModeSelect.currentIndexChanged.connect(lambda: setattr(self, 'settings_changed', True))
        
        # 情感匹配
        if CONFIGS.gui_settings["sentiment_matching"].get("display", False):
            self.ui.comboBox_ModelSelect.currentIndexChanged.connect(self._on_model_changed)
            self.ui.pushButton_testConn.clicked.connect(self._test_ai_connection)
            self.ui.lineEdit_apiUrl.textChanged.connect(lambda: setattr(self, 'settings_changed', True))
            self.ui.lineEdit_apiKey.textChanged.connect(lambda: setattr(self, 'settings_changed', True))
            self.ui.comboBox_modelName.currentTextChanged.connect(lambda: setattr(self, 'settings_changed', True))
            self.ui.pushButton_query.clicked.connect(self._query_models)
        
        # 图像压缩
        self.ui.checkBox_enableImgCompression.stateChanged.connect(lambda: setattr(self, 'settings_changed', True))
        self.ui.horizontalSlider_ReductionRatio.valueChanged.connect(self._on_compression_ratio_changed)
        
        # 进程白名单
        self.ui.textEdit_processList.textChanged.connect(lambda: setattr(self, 'settings_changed', True))
        
        # 快捷键修改按钮
        modify_buttons = [
            (self.ui.pushButton_modifiy1, 'start_generate'),
            (self.ui.pushButton_modify2, 'toggle_listener'),
            (self.ui.pushButton_modify3, 'prev_character'),
            (self.ui.pushButton_modify4, 'next_character'),
            (self.ui.pushButton_modify5, 'prev_emotion'),
            (self.ui.pushButton_modify6, 'next_emotion'),
            (self.ui.pushButton_modify7, 'prev_background'),
            (self.ui.pushButton_modify8, 'next_background')
        ]
        
        for button, key in modify_buttons:
            button.clicked.connect(lambda checked, k=key: self._start_hotkey_config(k))
        
        # 角色快速选择
        for i in range(1, 7):
            combo = self.character_combos.get(f"character_{i}")
            if combo:
                combo.currentIndexChanged.connect(lambda: setattr(self, 'settings_changed', True))
        
        # 对话框按钮
        self.ui.buttonBox.accepted.connect(self._on_save)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self._on_apply)

        # 连接AI测试信号
        self.ai_test_completed.connect(self._on_ai_test_completed)
    
    def _on_model_changed(self, index):
        """模型选择改变"""
        model_name = self.ui.comboBox_ModelSelect.currentText()
        self._update_model_parameters(model_name)
        self.settings_changed = True
    
    def _on_compression_ratio_changed(self, value):
        """压缩比例改变"""
        self.ui.label_ReductRate.setText(f"{value}%")
        self.settings_changed = True
    
    def _start_hotkey_config(self, key_name):
        """开始配置热键"""
        # 获取当前值
        line_edit = self.hotkey_edits.get(key_name)
        if not line_edit:
            return
        
        original_value = line_edit.text()
        
        # 显示提示
        line_edit.setText("请按下按键组合...")
        
        # 启动配置线程
        self.hotkey_thread.configure_hotkey(key_name, original_value)
    
    def _on_hotkey_configured(self, key_name, hotkey_value):
        """热键配置完成"""
        line_edit = self.hotkey_edits.get(key_name)
        if line_edit:
            line_edit.setText(hotkey_value)
            self.settings_changed = True
    
    def _test_ai_connection(self):
        """测试AI连接"""
        if not CONFIGS.gui_settings["sentiment_matching"].get("display", False):
            return
        
        model_name = self.ui.comboBox_ModelSelect.currentText()
        if model_name not in CONFIGS.ai_models:
            return
        
        # 获取配置
        config = {
            "base_url": self.ui.lineEdit_apiUrl.text(),
            "api_key": self.ui.lineEdit_apiKey.text(),
            "model": self.ui.comboBox_modelName.currentText()
        }
        
        # 禁用按钮
        self.ui.pushButton_testConn.setEnabled(False)
        self.ui.pushButton_testConn.setText("测试中...")
        
        # 用于取消线程的标志
        self._test_cancelled = False
        
        def test_in_thread():
            success = self.core.test_ai_connection(model_name, config)
            
            # 如果已经被取消，不再发送信号
            if not self._test_cancelled:
                self.ai_test_completed.emit(success, "连接成功" if success else "连接失败")
        
        # 启动测试线程
        thread = threading.Thread(target=test_in_thread, daemon=True, name="AIConnectionTest")
        thread.start()
        
        # 10秒后强制取消（使用QTimer，线程安全）
        QTimer.singleShot(10000, self._cancel_ai_test)

    def _cancel_ai_test(self):
        """取消AI测试"""
        self._test_cancelled = True
        if not self.ui.pushButton_testConn.isEnabled():
            self.ui.pushButton_testConn.setEnabled(True)
            self.ui.pushButton_testConn.setText("连接超时")
            QTimer.singleShot(2000, lambda: self.ui.pushButton_testConn.setText("测试连接"))

    def _on_ai_test_completed(self, success, message):
        """AI测试完成后的处理（在主线程执行）"""
        # 如果已经被取消，不再处理
        if self._test_cancelled:
            return
        
        self.ui.pushButton_testConn.setEnabled(True)
        self.ui.pushButton_testConn.setText(message)
        QTimer.singleShot(2000, lambda: self.ui.pushButton_testConn.setText("测试连接"))
    
    def _collect_settings(self):
        """收集所有设置"""
        settings = {
            "cut_settings": {
                "cut_mode": {
                    "全选剪切": "full",
                    "单行剪切": "single_line", 
                    "直接剪切": "direct"
                }.get(self.ui.comboBox_pasteModeSelect.currentText(), "full")
            },
            "image_compression": {
                "pixel_reduction_enabled": self.ui.checkBox_enableImgCompression.isChecked(),
                "pixel_reduction_ratio": self.ui.horizontalSlider_ReductionRatio.value()
            },
            "quick_characters": self._collect_quick_characters(),
        }
        
        # 情感匹配设置
        model_name = self.ui.comboBox_ModelSelect.currentText()
        
        # 获取现有的模型配置
        existing_model_configs = CONFIGS.gui_settings.get("sentiment_matching", {}).get("model_configs", {}).copy()
        
        # 更新当前模型配置
        current_model_config = {
            "base_url": self.ui.lineEdit_apiUrl.text(),
            "api_key": self.ui.lineEdit_apiKey.text(),
            "model": self.ui.comboBox_modelName.currentText()
        }
        
        existing_model_configs[model_name] = current_model_config
        
        settings["sentiment_matching"] = {
            "display": True,
            "enabled": CONFIGS.gui_settings["sentiment_matching"].get("enabled", False),
            "ai_model": model_name,
            "model_configs": existing_model_configs
        }

        return settings
    
    def _collect_quick_characters(self):
        """收集快速角色设置"""
        quick_characters = {}
        for i in range(1, 7):
            combo = self.character_combos.get(f"character_{i}")
            if combo:
                text = combo.currentText()
                if text and "(" in text and ")" in text:
                    char_id = text.split("(")[-1].rstrip(")")
                    quick_characters[f"character_{i}"] = char_id
                else:
                    quick_characters[f"character_{i}"] = ""
        return quick_characters
    
    def _collect_hotkeys(self):
        """收集热键设置"""
        new_hotkeys = {}
        
        # 收集所有热键
        hotkey_mapping = {
            'lineEdit_generateImgKey': 'start_generate',
            'lineEdit_listenerCtrlKey': 'toggle_listener',
            'lineEdit_previCharaKey': 'prev_character',
            'lineEdit_nextCharaKey': 'next_character', 
            'lineEdit_previEmoKey': 'prev_emotion',
            'lineEdit_nextEmoKey': 'next_emotion',
            'lineEdit_previBgKey': 'prev_background',
            'lineEdit_nextBgKey': 'next_background'
        }
        
        for control_name, config_key in hotkey_mapping.items():
            line_edit = getattr(self.ui, control_name, None)
            if line_edit:
                hotkey_value = line_edit.text()
                if hotkey_value and hotkey_value != "请按下按键组合...":
                    new_hotkeys[config_key] = hotkey_value
        
        return new_hotkeys
    
    def _collect_whitelist(self):
        """收集进程白名单"""
        text = self.ui.textEdit_processList.toPlainText().strip()
        processes = [p.strip() for p in text.split('\n') if p.strip()]
        return processes
    
    def _on_save(self):
        """保存设置"""
        if self._on_apply():
            self.accept()
    
    def _on_apply(self):
        """应用设置"""
        changes_made = True
        
        # 保存常规设置
        if self.settings_changed:
            new_settings = self._collect_settings()
            CONFIGS.gui_settings |= new_settings
            if CONFIGS.save_gui_settings():
                self.core.update_status("设置已保存")

        # 保存进程白名单
        processes = self._collect_whitelist()
        if CONFIGS.save_process_whitelist(processes):
            self.core.update_status("白名单更新")
        
        # 保存热键
        hotkeys = self._collect_hotkeys()
        if CONFIGS.save_keymap(hotkeys):
            self.core.update_status("热键更新")
        
        # 重置修改标志
        self.settings_changed = False
        
        return changes_made
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止热键配置线程
        if self.hotkey_thread.isRunning():
            self.hotkey_thread.stop()
            self.hotkey_thread.wait()
        
        event.accept()