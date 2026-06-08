"""
updater.py
自更新模块 — 从 GitHub Releases 下载 ZIP 并替换当前程序文件。

Windows 上通过生成批处理脚本来实现"延迟替换"：
1. 下载最新版 ZIP 到临时目录
2. 解压到临时目录
3. 生成 .bat 脚本：等待旧进程退出 → 复制新文件覆盖 → 重启程序 → 清理
4. 运行 .bat 并退出当前进程
"""

from __future__ import annotations

import os
import sys
import shutil
import tempfile
import zipfile
import subprocess
import time
from io import BytesIO
from typing import Optional, Callable

import requests


class SelfUpdater:
    """自更新管理器"""

    def __init__(self, repo_url: str, current_version: str, app_exe_name: str = "魔裁文本框.exe"):
        self.repo_url = repo_url.rstrip("/")
        self.current_version = current_version
        self.app_exe_name = app_exe_name

        # 解析 GitHub 仓库信息
        parts = self.repo_url.split("/")
        self.username = parts[-2]
        self.repo_name = parts[-1]

        self._app_dir = self._get_app_dir()

        # 是否运行在打包后的 exe 中（而非源码 python gui.py）
        self.is_frozen = getattr(sys, "frozen", False)

    @staticmethod
    def _get_app_dir() -> str:
        """获取程序所在目录"""
        if getattr(sys, "frozen", False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def _get_zip_download_url(self) -> Optional[str]:
        """获取最新 release 中 ZIP 包的下载 URL"""
        api_url = f"https://api.github.com/repos/{self.username}/{self.repo_name}/releases/latest"
        try:
            resp = requests.get(api_url, timeout=15)
            if resp.status_code != 200:
                print(f"[Updater] API 请求失败: {resp.status_code}")
                return None
            data = resp.json()
            assets = data.get("assets", [])
            for asset in assets:
                name = asset.get("name", "")
                # 找 ZIP 包
                if name.lower().endswith(".zip"):
                    url = asset.get("browser_download_url")
                    print(f"[Updater] 找到 ZIP: {name} ({SelfUpdater._format_size(asset.get('size', 0))})")
                    return url
            print(f"[Updater] 未找到 ZIP 文件，release 包含 {len(assets)} 个资源")
            return None
        except requests.RequestException as e:
            print(f"[Updater] 获取 release 信息失败: {e}")
            return None

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    @staticmethod
    def _unwrap_single_folder(extract_dir: str) -> str:
        """
        如果解压后的目录里只有一个顶层文件夹（即 ZIP 打包时含了一层父目录），
        自动穿透进去，返回实际文件所在的目录。

        比如 ZIP 内容为 `manosaba_v2.3.0/exe文件...` 时，
        会返回 `extract_dir/manosaba_v2.3.0/` 而非 `extract_dir/`。
        """
        entries = os.listdir(extract_dir)
        if len(entries) == 1:
            single = os.path.join(extract_dir, entries[0])
            if os.path.isdir(single):
                print(f"[Updater] ZIP 含顶层文件夹 '{entries[0]}'，自动穿透")
                return single
        return extract_dir

    def download_and_update(self, progress_callback: Optional[Callable[[str, int], None]] = None) -> tuple[bool, str]:
        """
        下载最新版并准备更新。

        Args:
            progress_callback: (message, percentage) 进度回调

        Returns:
            (success, message)
        """
        # 源码运行时不允许自动更新（ZIP 里是 exe，会覆盖 py 文件）
        if not self.is_frozen:
            return False, (
                "当前为源码运行模式，自动更新仅支持打包后的 exe。\n"
                "请使用 git pull 获取最新代码。"
            )

        download_url = self._get_zip_download_url()
        if not download_url:
            return False, "未找到下载文件"

        # 1. 下载到临时目录
        tmp_dir = tempfile.mkdtemp(prefix="manosaba_update_")
        zip_path = os.path.join(tmp_dir, "update.zip")

        try:
            if progress_callback:
                progress_callback("正在下载更新...", 0)

            resp = requests.get(download_url, stream=True, timeout=120)
            total_size = int(resp.headers.get("content-length", 0))
            downloaded = 0

            with open(zip_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        pct = min(int(downloaded / total_size * 100), 99)
                        progress_callback(
                            f"正在下载... {SelfUpdater._format_size(downloaded)}/{SelfUpdater._format_size(total_size)}",
                            pct,
                        )

            if progress_callback:
                progress_callback("正在解压...", 100)

            # 2. 解压到临时目录
            extract_dir = os.path.join(tmp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)

            # 如果解压后只有一个顶层文件夹，自动穿透进去
            extract_dir = self._unwrap_single_folder(extract_dir)

            # 3. 创建替换脚本
            bat_path = self._create_replace_script(extract_dir, tmp_dir)
            if not bat_path:
                return False, "无法创建替换脚本"

            if progress_callback:
                progress_callback("正在启动更新...", 100)

            # 4. 执行脚本并退出
            self._launch_and_exit(bat_path)

            return True, "更新已启动"

        except requests.RequestException as e:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return False, f"下载失败: {e}"
        except zipfile.BadZipFile:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return False, "下载的文件损坏"
        except Exception as e:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return False, f"更新失败: {e}"

    def _create_replace_script(self, extract_dir: str, tmp_dir: str) -> Optional[str]:
        """
        创建 Windows 批处理脚本，用于在旧进程退出后替换文件。

        脚本逻辑：
        1. 等待旧进程退出
        2. 复制新文件到 app 目录
        3. 重启程序
        4. 删除临时文件
        5. 自毁
        """
        if sys.platform.startswith("win"):
            return self._create_windows_script(extract_dir, tmp_dir)
        else:
            return self._create_unix_script(extract_dir, tmp_dir)

    def _create_windows_script(self, extract_dir: str, tmp_dir: str) -> str:
        """创建 Windows 批处理脚本"""
        bat_path = os.path.join(tmp_dir, "update.bat")
        app_dir = self._app_dir

        # 确保路径使用反斜杠并且没有尾部斜杠
        app_dir = os.path.normpath(app_dir)
        extract_dir = os.path.normpath(extract_dir)

        # 当前进程 PID
        current_pid = os.getpid()

        # 用户配置文件 — 更新时不能覆盖，否则用户的快捷键、设置等会丢失
        protected_config_files = [
            "settings.yml",
            "keymap.yml",
            "styles.yml",
            "process_whitelist.yml",
        ]
        xf_flags = " ".join(f"/XF \"{f}\"" for f in protected_config_files)

        script = f"""@echo off
chcp 65001 >nul
title 魔裁文本框 - 更新中...

echo 等待旧进程退出...
:waitloop
timeout /t 1 /nobreak >nul
tasklist /fi "pid eq {current_pid}" 2>nul | find "{current_pid}" >nul
if not errorlevel 1 goto waitloop

echo 正在替换文件...
robocopy "{extract_dir}" "{app_dir}" /E /IS /IT {xf_flags} /NJH /NJS /NP /NC /NS >nul
set robocopy_exit=%ERRORLEVEL%
if %robocopy_exit% GEQ 8 (
    echo 文件替换出错 (code %robocopy_exit%)
    timeout /t 5 /nobreak >nul
    exit
)

echo 正在清理临时文件...
timeout /t 2 /nobreak >nul
rmdir /s /q "{tmp_dir}" 2>nul

echo 正在启动新版本...
start "" "{os.path.join(app_dir, self.app_exe_name)}"

echo 更新完成!
del "%~f0" 2>nul
exit
"""
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(script)

        print(f"[Updater] 替换脚本已创建: {bat_path}")
        return bat_path

    def _create_unix_script(self, extract_dir: str, tmp_dir: str) -> str:
        """创建 Unix/Linux shell 脚本（暂未完全测试）"""
        script_path = os.path.join(tmp_dir, "update.sh")
        app_dir = self._app_dir
        current_pid = os.getpid()

        script = f"""#!/bin/bash
echo "等待旧进程退出..."
while kill -0 {current_pid} 2>/dev/null; do sleep 1; done

echo "正在替换文件..."
cp -rf "{extract_dir}"/* "{app_dir}"/

echo "正在清理临时文件..."
sleep 2
rm -rf "{tmp_dir}"

echo "正在启动新版本..."
"{os.path.join(app_dir, self.app_exe_name)}" &

rm -f "$0"
"""
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)
        os.chmod(script_path, 0o755)

        print(f"[Updater] 替换脚本已创建: {script_path}")
        return script_path

    def _launch_and_exit(self, script_path: str):
        """启动替换脚本并退出当前进程"""
        if sys.platform.startswith("win"):
            # CREATE_NEW_CONSOLE=0x10, DETACHED_PROCESS=0x08
            subprocess.Popen(
                ["cmd.exe", "/c", script_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE | 0x00000200,  # CREATE_NO_WINDOW
                close_fds=True,
            )
        else:
            subprocess.Popen(["bash", script_path], close_fds=True)

        # 退出当前进程
        print("[Updater] 正在退出以完成更新...")
        os._exit(0)
