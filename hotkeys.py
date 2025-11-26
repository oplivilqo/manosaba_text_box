# -*- coding: utf-8 -*-
# 管理全局热键
import threading
import time
import keyboard
import logging
import win32gui
import win32process
import psutil
import os
import core
import clipboard

logger = logging.getLogger(__name__)

# 默认窗口白名单
DEFAULT_WINDOW_WHITELIST = ["TIM.exe", "WeChat.exe", "Weixin.exe", "WeChatApp.exe", "QQ.exe"]

# 存放已注册的热键句柄
_registered_hotkeys = []

#整合了一下全局变量
class AppState:
    def __init__(self):
        self.current_role = list(core.mahoshojo.keys())[2] #不知道为啥默认橘雪莉
        self.last_expression = -1
        self.auto_paste = True
        self.auto_send = True
        self.enable_whitelist = True
        self.window_whitelist = DEFAULT_WINDOW_WHITELIST
        self.busy = False
        self.delay = 0.1
        #热键
        self.paste_hotkey = 'ctrl+v'
        self.send_hotkey = 'enter'
        self.select_all_hotkey = 'ctrl+a'
        self.cut_hotkey = 'ctrl+x'


# 获取前台 exe 名称
def get_foreground_exe_name():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        exe_path = proc.exe()
        return os.path.basename(exe_path)
    except Exception as e:
        logger.debug("get_foreground_exe_name failed: %s", e)
        return None

#清除魔裁缓存文件夹
def _clear_magic_cut_folder():
    folder = core.get_magic_cut_folder()
    if not os.path.isdir(folder):
        return
    for entry in os.scandir(folder):
        if entry.is_file() and entry.name.lower().endswith('.jpg'):
            try:
                os.remove(entry.path)
            except Exception:
                logger.exception("failed to remove %s", entry.path)

#统一处理剪贴板操作
def _perform_keyboard_actions(png_bytes, state: AppState):
    if png_bytes is None:
        logger.warning("png_bytes is None, nothing to paste/send")
        return
    try:
        # 把图片写入剪贴板
        clipboard.copy_png_bytes_to_clipboard(png_bytes)
    except Exception:
        logger.exception("copy to clipboard failed")
        return

    if state.auto_paste:
        # 给系统一点时间
        keyboard.call_later(lambda: keyboard.send(state.paste_hotkey), delay=0.12)
        if state.auto_send:
            keyboard.call_later(lambda: keyboard.send(state.send_hotkey), delay=0.35)

#进行图片生成和发送的工作线程
def _worker_generate_and_send(text: str, state: AppState):
    try:
        font_path = core.get_resource_path(core.mahoshojo[state.current_role]["font"]) if state.current_role in core.mahoshojo else None
        png_bytes, expr = core.generate_image(text=text, content_image=None, role_name=state.current_role, font_path=font_path, last_value=state.last_expression, expression=-1)
        # 更新状态
        if expr is not None:
            state.last_expression = expr
    except Exception:
        logger.exception("generate_image failed")
        png_bytes = None
    finally:
        # 在 keyboard 的线程上下文安全地执行粘贴/发送
        keyboard.call_later(lambda: _perform_keyboard_actions(png_bytes, state), delay=0)
        state.busy = False

#enter触发处理
def _on_enter_trigger(state: AppState):
    if state.busy:
        logger.debug("Busy, ignoring enter trigger")
        return
    if state.enable_whitelist:
        exe = get_foreground_exe_name()
        if exe not in state.window_whitelist:
            logger.debug("Foreground exe %s not in whitelist, ignoring", exe)
            return
    try:
        text = clipboard.cut_all_and_get_text()
    except Exception:
        logger.exception("cut_all_and_get_text failed")
        return
    state.busy = True
    t = threading.Thread(target=_worker_generate_and_send, args=(text, state), daemon=True)
    t.start()

#切换角色
def switch_role_by_index(idx: int, state: AppState):
    roles = list(core.mahoshojo.keys())
    if 1 <= idx <= len(roles):
        state.current_role = roles[idx-1]
        # 异步预生成资源
        threading.Thread(target=core.generate_and_save_images, args=(state.current_role,), daemon=True).start()
        logger.info("switched role to %s", state.current_role)
        return True
    return False

#设置表情
def set_expression(expr: int, state: AppState):
    state.last_expression = -1
    try:
        state.last_expression = expr
        logger.info("set expression %s", expr)
    except Exception:
        logger.exception("set_expression failed")

#切换自动粘贴
def toggle_auto_paste(state: AppState):
    state.auto_paste = not state.auto_paste
    if not state.auto_paste:
        state.auto_send = False
    logger.info("auto_paste=%s auto_send=%s", state.auto_paste, state.auto_send)

#切换自动发送
def toggle_auto_send(state: AppState):
    if not state.auto_paste:
        logger.info("auto_send requires auto_paste on")
        return
    state.auto_send = not state.auto_send
    logger.info("auto_send=%s", state.auto_send)

#注册热键
def register_hotkeys(state: AppState = None):
    if state is None:
        state = AppState()
    for i in range(1, 10):
        hk = keyboard.add_hotkey(f'ctrl+{i}', lambda idx=i: switch_role_by_index(idx, state))
        _registered_hotkeys.append(hk)
    _registered_hotkeys.append(keyboard.add_hotkey('ctrl+q', lambda: switch_role_by_index(10, state)))
    _registered_hotkeys.append(keyboard.add_hotkey('ctrl+e', lambda: switch_role_by_index(11, state)))
    _registered_hotkeys.append(keyboard.add_hotkey('ctrl+r', lambda: switch_role_by_index(12, state)))
    _registered_hotkeys.append(keyboard.add_hotkey('ctrl+t', lambda: switch_role_by_index(13, state)))
    _registered_hotkeys.append(keyboard.add_hotkey('ctrl+y', lambda: switch_role_by_index(14, state)))

    # alt+1..9 设置表情
    for i in range(1, 10):
        _registered_hotkeys.append(keyboard.add_hotkey(f'alt+{i}', lambda idx=i: set_expression(idx, state)))

    # 切换
    _registered_hotkeys.append(keyboard.add_hotkey('ctrl+g', lambda: toggle_auto_paste(state)))
    _registered_hotkeys.append(keyboard.add_hotkey('ctrl+h', lambda: toggle_auto_send(state)))

    # 清缓存
    _registered_hotkeys.append(keyboard.add_hotkey('ctrl+tab', lambda: _clear_magic_cut_folder()))

    # show current
    _registered_hotkeys.append(keyboard.add_hotkey('ctrl+0', lambda: logger.info('current role: %s', state.current_role)))
    
    #启动！！
    _registered_hotkeys.append(keyboard.add_hotkey('enter', lambda: _on_enter_trigger(state), suppress=False))

    return _registered_hotkeys

#注销热键
def unregister_hotkeys():
    for hk in list(_registered_hotkeys):
        try:
            keyboard.remove_hotkey(hk)
        except Exception:
            logger.exception("remove_hotkey failed for %s", hk)
    _registered_hotkeys.clear()


# 设置一个defaultstate
_default_state = AppState()

def start_default():
    register_hotkeys(_default_state)


def stop_default():
    unregister_hotkeys()
