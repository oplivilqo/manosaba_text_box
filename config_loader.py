import os
import sys
import re
import yaml
import logging
from typing import Callable, Dict, List, Tuple, Set

logger = logging.getLogger(__name__)

# ===== PyInstaller 资源路径处理函数 =====
def get_resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# -----------------
# 全局配置变量（加载后供全局使用）
# -----------------
MAHOSHOJO: Dict[str, Dict] = {}
TEXT_CONFIGS: Dict[str, List[Dict]] = {}
PROCESS_WHITELIST: List[str] = []
BACKGROUND_INDEXES: Set[int] = set()

# -----------------
# YAML 读取
# -----------------

def _read_yaml(path: str) -> Dict | None:
    candidates: List[str] = []
    if os.path.isabs(path):
        candidates.append(path)
    candidates.append(get_resource_path(path))

    abs_path = next((p for p in candidates if os.path.isfile(p)), None)
    if abs_path is None:
        logger.warning("配置文件未找到: %s", path)
        return None

    try:
        with open(abs_path, 'r', encoding='utf-8-sig') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError:
        logger.exception("读取配置文件失败: %s", abs_path)
        return None
    except OSError:
        logger.exception("打开配置文件失败: %s", abs_path)
        return None

    if data is None:
        logger.warning("配置文件为空: %s", abs_path)
        return None

    if not isinstance(data, dict):
        logger.warning("配置文件格式错误（应为字典）: %s", abs_path)
        return None

    logger.debug("成功加载配置文件: %s", abs_path)
    return data

# -----------------
# 小工具
# -----------------

def _to_tuple2(v) -> Tuple[int, int]:
    if not isinstance(v, (list, tuple)) or len(v) != 2:
        raise ValueError("需要长度为2的序列")
    return int(v[0]), int(v[1])


def _to_tuple3(v) -> Tuple[int, int, int]:
    if not isinstance(v, (list, tuple)) or len(v) != 3:
        raise ValueError("需要长度为3的序列")
    return int(v[0]), int(v[1]), int(v[2])

# -----------------
# 加载配置
# -----------------

def load_chara_meta() -> Dict[str, Dict]:
    data = _read_yaml("config/chara_meta.yml")
    if not data:
        return {}
    root = data.get("mahoshojo")
    if not isinstance(root, dict):
        logger.warning("chara_meta.yml 顶层缺少 mahoshojo")
        return {}

    result: Dict[str, Dict] = {}
    for role, cfg in root.items():
        if not isinstance(cfg, dict):
            logger.warning("角色配置应为字典: %s", role)
            continue
        try:
            ec = int(cfg.get("emotion_count"))
            if ec <= 0:
                raise ValueError("emotion_count 必须为正数")
            font = cfg.get("font")
            if not isinstance(font, str) or not font:
                raise ValueError("font 必须为非空字符串")
            full_name = cfg.get("full_name", "")
            if not isinstance(full_name, str):
                full_name = ""
            result[role] = {"emotion_count": ec, "font": font, "full_name": full_name}
        except Exception as e:
            logger.warning("角色配置无效 %s: %s", role, e)
            continue

    logger.info("已加载角色配置：%d 个角色", len(result))
    return result


def load_text_configs() -> Dict[str, List[Dict]]:
    data = _read_yaml("config/text_configs.yml")
    if not data:
        return {}
    root = data.get("text_configs")
    if not isinstance(root, dict):
        logger.warning("text_configs.yml 顶层缺少 text_configs")
        return {}

    result: Dict[str, List[Dict]] = {}
    for role, items in root.items():
        if not isinstance(items, list):
            logger.warning("角色文字配置应为列表: %s", role)
            continue
        out: List[Dict] = []
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                logger.warning("文字配置项应为字典: %s[%d]", role, idx)
                continue
            try:
                text = item.get("text", "")
                if text is None:
                    text = ""
                position = _to_tuple2(item.get("position"))
                font_color = _to_tuple3(item.get("font_color"))
                font_size = int(item.get("font_size"))
                out.append({
                    "text": text,
                    "position": position,
                    "font_color": font_color,
                    "font_size": font_size,
                })
            except Exception as e:
                logger.warning("无效的文字配置 %s[%d]: %s", role, idx, e)
                continue
        result[role] = out
    logger.info("已加载文字配置：%d 个角色", len(result))
    return result


def load_process_whitelist(os_name: str) -> List[str]:
    data = _read_yaml("config/process_whitelist.yml")
    if not data:
        return []
    key = (os_name or "").lower()
    items = data.get(key)
    if not isinstance(items, list):
        return []
    result: List[str] = []
    for it in items:
        if isinstance(it, str) and it.strip():
            result.append(it.strip())
    logger.info("已加载白名单(%s)：%d 个", key, len(result))
    return result

# -----------------
# 资产扫描
# -----------------

def _scan_backgrounds(assets_dir: str) -> Set[int]:
    bg_dir = os.path.join(assets_dir, "background")
    found: Set[int] = set()
    if not os.path.isdir(bg_dir):
        logger.warning("背景目录不存在: %s", bg_dir)
        return found
    rex = re.compile(r"^c(\d+)\.png$", re.IGNORECASE)
    for name in os.listdir(bg_dir):
        m = rex.match(name)
        if m:
            try:
                found.add(int(m.group(1)))
            except Exception:
                pass
    return found


def _scan_roles_in_assets(assets_dir: str) -> Set[str]:
    chara_dir = os.path.join(assets_dir, "chara")
    roles: Set[str] = set()
    if not os.path.isdir(chara_dir):
        logger.warning("角色目录不存在: %s", chara_dir)
        return roles
    for name in os.listdir(chara_dir):
        path = os.path.join(chara_dir, name)
        if os.path.isdir(path):
            roles.add(name)
    return roles


def _scan_role_diffs(assets_dir: str, role: str) -> Set[int]:
    role_dir = os.path.join(assets_dir, "chara", role)
    diffs: Set[int] = set()
    if not os.path.isdir(role_dir):
        return diffs
    rex = re.compile(rf"^{re.escape(role)}\s*\((\d+)\)\.png$", re.IGNORECASE)
    for name in os.listdir(role_dir):
        m = rex.match(name)
        if m:
            try:
                diffs.add(int(m.group(1)))
            except Exception:
                pass
    return diffs

# -----------------
# 校验
# -----------------

def validate_assets(meta: Dict[str, Dict], text_cfg: Dict[str, List[Dict]] | None, assets_dir: str) -> Dict:
    errors: List[str] = []
    warnings: List[str] = []
    stats: Dict = {"backgrounds": {}, "roles": {}}

    # 背景图校验
    bg_found = _scan_backgrounds(assets_dir)
    expected_bg = set(range(1, 17))
    stats["backgrounds"] = {"found": len(bg_found)}
    miss_bg = sorted(expected_bg - bg_found)
    extra_bg = sorted(bg_found - expected_bg)
    if miss_bg:
        errors.append(f"缺少背景: {miss_bg}")
    if extra_bg:
        warnings.append(f"多余背景: {extra_bg}")

    # 角色目录校验
    cfg_roles = list(meta.keys())
    assets_roles = _scan_roles_in_assets(assets_dir)
    miss_roles = sorted(set(cfg_roles) - assets_roles)
    extra_roles = sorted(assets_roles - set(cfg_roles))
    if miss_roles:
        errors.append(f"缺少角色目录: {miss_roles}")
    if extra_roles:
        warnings.append(f"资产中存在未配置角色: {extra_roles}")

    # 字体校验
    fonts = {meta[r].get("font") for r in cfg_roles if isinstance(meta.get(r), dict)}
    for font in fonts:
        font_path = os.path.join(assets_dir, "fonts", str(font))
        if not os.path.isfile(font_path):
            errors.append(f"缺少字体文件: {font}")

    # 差分校验
    for role in cfg_roles:
        ec = int(meta[role]["emotion_count"]) if "emotion_count" in meta[role] else 0
        expected = set(range(1, ec + 1))
        found = _scan_role_diffs(assets_dir, role)
        stats["roles"][role] = {"expected": len(expected), "found": len(found)}
        miss = sorted(expected - found)
        extra = sorted(found - expected)
        if miss:
            errors.append(f"角色 {role} 缺少差分: {miss}")
        if extra:
            warnings.append(f"角色 {role} 多余差分: {extra}")

    # 文本配置角色集合差异（警告级别）
    if text_cfg:
        text_roles = set(text_cfg.keys())
        cfg_roles_set = set(cfg_roles)
        diff_a = sorted(text_roles - cfg_roles_set)
        diff_b = sorted(cfg_roles_set - text_roles)
        if diff_a:
            warnings.append(f"文字配置存在未配置角色: {diff_a}")
        if diff_b:
            warnings.append(f"角色配置缺少文字配置: {diff_b}")

    ok = len(errors) == 0
    return {"ok": ok, "errors": errors, "warnings": warnings, "stats": stats}

# -----------------
# 统一加载与校验入口
# -----------------

def load_all_and_validate(os_name: str = "win32", assets_dir: str | None = None, callback: Callable[[str], None] | None = None) -> Tuple[Dict, Dict]:
    global MAHOSHOJO, TEXT_CONFIGS, PROCESS_WHITELIST, BACKGROUND_INDEXES

    assets_dir = assets_dir or get_resource_path("assets")

    # 加载配置
    MAHOSHOJO = load_chara_meta()
    TEXT_CONFIGS = load_text_configs()
    PROCESS_WHITELIST = load_process_whitelist(os_name)

    # 扫描背景用于快速使用
    BACKGROUND_INDEXES = _scan_backgrounds(assets_dir)

    # 校验
    report = validate_assets(MAHOSHOJO, TEXT_CONFIGS, assets_dir)

    # 回调输出
    if callback:
        for w in report["warnings"]:
            try:
                callback(f"[警告] {w}")
            except Exception:
                logger.exception("回调警告输出失败")
        for e in report["errors"]:
            try:
                callback(f"[错误] {e}")
            except Exception:
                logger.exception("回调错误输出失败")

    loaded = {"mahoshojo": MAHOSHOJO, "text_configs": TEXT_CONFIGS, "whitelist": PROCESS_WHITELIST, "backgrounds": sorted(BACKGROUND_INDEXES)}
    return loaded, report

