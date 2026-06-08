# pyqt_about.py
"""PyQt 关于窗口 — 含更新检查与自更新功能"""

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QThread, Signal
import sys
import traceback

from ui.about_window import Ui_AboutWindow
from config import CONFIGS
from utils.update_checker import update_checker


class CheckUpdateThread(QThread):
    """检查更新线程"""
    update_result = Signal(dict)

    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version

    def run(self):
        """执行更新检查"""
        try:
            result = update_checker.check_update(self.current_version)
            self.update_result.emit(result)
        except Exception as e:
            self.update_result.emit({"error": str(e)})


class DownloadUpdateThread(QThread):
    """下载更新线程"""
    progress = Signal(str, int)   # (message, percentage)
    finished = Signal(bool, str)  # (success, message)

    def __init__(self):
        super().__init__()
        self._updater = None

    def run(self):
        """执行下载和更新"""
        from utils.updater import SelfUpdater

        try:
            program_info = CONFIGS.get_program_info()
            self._updater = SelfUpdater(
                repo_url=program_info["github"],
                current_version=CONFIGS.version,
                app_exe_name="魔裁文本框.exe",
            )
            success, msg = self._updater.download_and_update(
                progress_callback=lambda msg, pct: self.progress.emit(msg, pct)
            )
            self.finished.emit(success, msg)
        except Exception as e:
            self.finished.emit(False, f"更新异常: {str(e)}")


class AboutWindow(QDialog):
    """关于窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置UI
        self.ui = Ui_AboutWindow()
        self.ui.setupUi(self)

        # 线程
        self.update_thread = None
        self.download_thread = None

        # 状态
        self.content_type = "original"  # original, version_history, update_check
        self.version_history_content = ""
        self.update_check_content = ""
        self.update_available = False  # 是否有可用更新

        # 初始化界面
        self._setup_ui()

        # 连接信号槽
        self._connect_signals()

    def _setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("关于 - 魔裁文本框生成器")
        self.setFixedSize(644, 738)

        program_info = CONFIGS.get_program_info()
        self.ui.label_2.setText(f"v{program_info['version']}")
        self._set_original_description()

        authors = program_info.get("author", [])
        authors_text = ", ".join(authors) if isinstance(authors, list) else str(authors)
        self.ui.label_contributers.setText(authors_text)

    def _set_original_description(self):
        """设置原始程序描述"""
        program_info = CONFIGS.get_program_info()

        description = (
            f"{program_info.get('description', '')}\n\n"
            "情感匹配使用说明：\n"
            "支持 Ollama / LM Studio / DeepSeek / ChatGPT 等兼容 OpenAI API 的服务\n"
            "1. 下载 ollama 或 LM Studio\n"
            "2. 运行情感分析模型（如 OmniDimen）\n"
            "3. 启用程序内的情感匹配功能\n"
            "   （在setting.yml中启用sentiment_matching的display）\n"
            "4. 勾选主界面的情感匹配即可\n\n"
            "注意事项：\n"
            "• 有bug请及时反馈\n"
            "• 检查更新按钮可能对网络有要求"
        )

        self.ui.textBrowser.setPlainText(description)
        self.content_type = "original"
        self.ui.textBrowser.verticalScrollBar().setValue(0)

    def _set_version_history_content(self):
        """设置版本历史内容"""
        try:
            version_history = CONFIGS.get_version_history()
            if not version_history:
                self.version_history_content = "暂无版本历史信息"
                return

            history_text = "版本历史：\n\n"
            for i, version in enumerate(version_history, 1):
                history_text += f"版本 {version.get('version', '未知')}\n"
                history_text += f"发布时间: {version.get('date', '未知')}\n"
                history_text += "更新说明:\n"

                descriptions = version.get("description", [])
                if isinstance(descriptions, list):
                    for desc in descriptions:
                        history_text += f"• {desc}\n"
                else:
                    history_text += f"• {descriptions}\n"

                if i < len(version_history):
                    history_text += "\n" + "=" * 50 + "\n\n"

            self.version_history_content = history_text
        except Exception as e:
            self.version_history_content = f"获取版本历史失败: {str(e)}"

    def _set_update_check_content(self, result):
        """设置更新检查内容"""
        try:
            if isinstance(result, dict) and "error" in result:
                self.update_check_content = f"更新检查结果：\n❌ 检查更新失败: {result['error']}"
                self.update_available = False
                return

            if result.get("has_update", False):
                self.update_available = True
                latest = result["latest_release"]

                update_info = (
                    f"更新检查结果：\n"
                    f"✅ 有新版本可用: {latest['version']}\n\n"
                    f"版本信息：\n"
                    f"• 版本: {latest['version']}\n"
                    f"• 名称: {latest['version_name']}\n"
                    f"• 发布时间: {latest.get('published_at', '未知')}\n"
                    f"• 预发布: {'是' if latest.get('is_prerelease', False) else '否'}\n\n"
                )

                notes = latest.get("release_notes", "无更新说明")
                if len(notes) > 500:
                    notes = notes[:500] + "..."
                update_info += f"发布说明：\n{notes}\n\n"

                # 文件列表
                assets = latest.get("assets", [])
                if assets:
                    has_zip = any(a.get("name", "").lower().endswith(".zip") for a in assets)
                    update_info += "文件列表：\n"
                    for i, asset in enumerate(assets[:5]):
                        update_info += f"• {asset.get('name', '未知文件')} "
                        update_info += f"({self._format_size(asset.get('size', 0))})\n"
                    if len(assets) > 5:
                        update_info += f"• ... 等 {len(assets)} 个文件\n"

                    if has_zip:
                        if getattr(sys, "frozen", False):
                            update_info += "\n点击下方「立即更新」自动下载并安装更新。\n"
                        else:
                            update_info += (
                                "\n当前为源码运行模式，不支持自动更新，请使用 git pull：\n"
                                "  git pull origin gui\n"
                            )
                    else:
                        update_info += (
                            f"\n未找到 ZIP 格式的更新包，请手动前往：\n"
                            f"{update_checker.repo_url}/releases/latest"
                        )
                else:
                    update_info += (
                        f"\n下载链接：\n"
                        f"{update_checker.repo_url}/releases/latest"
                    )

                self.update_check_content = update_info
            else:
                self.update_available = False
                self.update_check_content = (
                    f"更新检查结果：\n✅ 当前已是最新版本！\n"
                    f"当前版本: v{CONFIGS.version}"
                )
        except Exception as e:
            self.update_available = False
            self.update_check_content = f"更新检查结果：\n❌ 处理结果时出错: {str(e)}"

    def _connect_signals(self):
        """连接信号槽"""
        self.ui.pushButton.clicked.connect(self.toggle_version_history)
        self.ui.pushButton_2.clicked.connect(self._on_main_action)

    def toggle_version_history(self):
        """切换版本历史显示"""
        if self.content_type == "version_history":
            self._set_original_description()
            self._reset_update_button()
        else:
            if not self.version_history_content:
                self._set_version_history_content()
            self.ui.textBrowser.setPlainText(self.version_history_content)
            self.content_type = "version_history"
            self._reset_update_button()
        self.ui.textBrowser.verticalScrollBar().setValue(0)

    def _on_main_action(self):
        """
        主导操作按钮 — 根据当前状态执行不同操作:
        - 正常状态 → 检查更新
        - 有更新 → 下载并更新
        - 更新检查结果中 → 返回原始内容
        """
        if self.download_thread and self.download_thread.isRunning():
            return  # 正在下载，忽略

        if self.content_type == "update_check" and self.update_available and getattr(sys, "frozen", False):
            # 有更新可用且是 exe 运行 → 开始下载
            self._start_download_update()
        elif self.content_type == "update_check":
            # 已是最新版本或出错 → 返回原始内容
            self._set_original_description()
            self._reset_update_button()
        else:
            # 正常状态 → 检查更新
            self._check_update()

    def _check_update(self):
        """检查更新"""
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_2.setText("检查中...")
        self.ui.textBrowser.setPlainText("正在检查更新...")
        self.content_type = "update_check"

        self.update_thread = CheckUpdateThread(CONFIGS.version)
        self.update_thread.update_result.connect(self._on_update_check_complete)
        self.update_thread.finished.connect(self._on_update_thread_finished)
        self.update_thread.start()

    def _start_download_update(self):
        """开始下载和更新"""
        # 确认
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "确认更新",
            "即将下载最新版本并自动替换当前程序文件。\n\n"
            "更新过程中程序将自动关闭，请确保已保存所有工作。\n\n"
            "是否继续？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply != QMessageBox.Yes:
            return

        # 禁用按钮，显示下载进度
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_2.setText("下载中...")
        self.ui.pushButton.setEnabled(False)

        self.ui.textBrowser.setPlainText("正在准备下载...\n")
        self.content_type = "update_check"

        self.download_thread = DownloadUpdateThread()
        self.download_thread.progress.connect(self._on_download_progress)
        self.download_thread.finished.connect(self._on_download_finished)
        self.download_thread.start()

    def _on_update_check_complete(self, result):
        """更新检查完成"""
        try:
            self._set_update_check_content(result)
            self.ui.textBrowser.setPlainText(self.update_check_content)
            self.content_type = "update_check"
        except Exception as e:
            self.ui.textBrowser.setPlainText(f"更新检查结果：\n❌ 处理结果时出错: {str(e)}\n{traceback.format_exc()}")
            self.content_type = "update_check"
            self.update_available = False

    def _on_update_thread_finished(self):
        """更新检查线程完成 — 更新按钮状态"""
        self.ui.pushButton_2.setEnabled(True)
        if self.update_available and getattr(sys, "frozen", False):
            self.ui.pushButton_2.setText("立即更新")
            self.ui.pushButton_2.setStyleSheet(
                "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }"
                "QPushButton:hover { background-color: #45a049; }"
            )
        else:
            self._reset_update_button()

        if self.update_thread:
            self.update_thread.deleteLater()
            self.update_thread = None

    def _on_download_progress(self, message, percentage):
        """下载进度更新"""
        current_text = self.ui.textBrowser.toPlainText()
        # 替换最后一行进度
        lines = current_text.split("\n")
        progress_bar = self._make_progress_bar(percentage)
        new_line = f"[{progress_bar}] {percentage}% — {message}"

        # 找到最后一行进度并替换，或追加
        replaced = False
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith("[") and "%" in lines[i]:
                lines[i] = new_line
                replaced = True
                break

        if not replaced:
            lines.append(new_line)

        self.ui.textBrowser.setPlainText("\n".join(lines))
        # 滚动到底部
        sb = self.ui.textBrowser.verticalScrollBar()
        sb.setValue(sb.maximum())

    @staticmethod
    def _make_progress_bar(percentage: int, width: int = 30) -> str:
        """生成进度条字符串"""
        filled = int(width * percentage / 100)
        return "█" * filled + "░" * (width - filled)

    def _on_download_finished(self, success, message):
        """下载完成"""
        self.ui.pushButton_2.setEnabled(True)
        self.ui.pushButton.setEnabled(True)

        if success:
            # 成功的话程序已经退出了，这行不会执行到
            self.ui.textBrowser.setPlainText(f"更新已启动，程序即将重启...\n{message}")
        else:
            self.ui.textBrowser.setPlainText(
                self.ui.textBrowser.toPlainText() + f"\n\n❌ 更新失败: {message}"
            )
            self._reset_update_button()

        if self.download_thread:
            self.download_thread.deleteLater()
            self.download_thread = None

    def _reset_update_button(self):
        """重置更新按钮到默认状态"""
        self.ui.pushButton_2.setText("检查更新")
        self.ui.pushButton_2.setStyleSheet("")
        self.update_available = False

    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def closeEvent(self, event):
        """窗口关闭事件"""
        for thread in (self.update_thread, self.download_thread):
            if thread and thread.isRunning():
                thread.quit()
                thread.wait(2000)
        event.accept()
