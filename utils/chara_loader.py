"""
chara_loader.py
从 assets/chara/*/meta.yml 加载角色配置

替代原来的 chara_meta.yml 单文件方案，每个角色在自己的文件夹内维护 meta.yml。
添加/移除角色只需添加/删除对应的文件夹即可，不需要手动编辑集中配置。
"""

from __future__ import annotations

import os
from typing import Dict, Any, Optional

from path_utils import get_resource_path


# 情感词列表（用于情感匹配）
EMOTION_LABELS = ["平静", "喜悦", "喜爱", "惊讶", "困惑", "无语", "悲伤", "愤怒", "恐惧"]


def load_all_characters() -> Dict[str, Dict[str, Any]]:
    """
    扫描 assets/chara/ 下所有子文件夹，
    加载每个文件夹中的 meta.yml 文件。

    Returns:
        { chara_id: { id, full_name, emotion_count, offset, scale, font, text, emo, ... }, ... }

    如果 meta.yml 缺少 id 字段，会自动用文件夹名填充。
    如果 meta.yml 不存在，该文件夹会被跳过（并打印警告）。
    """
    import yaml

    chara_dir = get_resource_path(os.path.join("assets", "chara"))
    if not chara_dir or not os.path.isdir(chara_dir):
        print(f"[WARN] 角色目录不存在: {chara_dir}")
        return {}

    characters: Dict[str, Dict[str, Any]] = {}

    for folder_name in sorted(os.listdir(chara_dir)):
        folder_path = os.path.join(chara_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue

        meta_path = os.path.join(folder_path, "meta.yml")
        if not os.path.isfile(meta_path):
            print(f"[WARN] 角色文件夹缺少 meta.yml，已跳过: {folder_name}")
            continue

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta: Dict[str, Any] = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[WARN] 读取 {meta_path} 失败: {e}，已跳过")
            continue

        if not isinstance(meta, dict):
            print(f"[WARN] {meta_path} 内容格式错误，已跳过")
            continue

        # 用文件夹名作为 id（如果 meta 中没有显式声明）
        chara_id = meta.get("id", folder_name)
        meta.setdefault("id", chara_id)

        # 确保必要字段有默认值
        meta.setdefault("full_name", chara_id)
        meta.setdefault("emotion_count", 0)
        meta.setdefault("offset", [0, 0])
        meta.setdefault("scale", 1.0)
        meta.setdefault("font", "font3")
        meta.setdefault("text", [])
        meta.setdefault("emo", {})

        characters[chara_id] = meta
        print(f"[INFO] 已加载角色: {chara_id} ({meta.get('full_name', '')})")

    return characters


def get_character_ids() -> list[str]:
    """返回所有已加载角色的 ID 列表"""
    # 避免循环导入
    from config import CONFIGS
    return list(CONFIGS.mahoshojo.keys())


def validate_character(chara_id: str) -> bool:
    """检查角色是否存在"""
    from config import CONFIGS
    return chara_id in CONFIGS.mahoshojo
