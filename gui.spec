# -*- mode: python -*-
# PyInstaller spec for building the GUI application (one-folder / onedir).
# This spec collects resource files (background, character folders, font) and packages gui.py.

block_cipher = None

import sys
import os

# Add current directory to sys.path so we can import core during spec parsing
sys.path.insert(0, os.path.abspath('.'))

import core

# collect data files (tuples of (src, destdir))
datas = []

# include font if present
if os.path.exists('font3.ttf'):
    datas.append(('font3.ttf', '.'))

# include background folder
if os.path.isdir('background'):
    for root, _, files in os.walk('background'):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, 'background')
            dest = os.path.join('background', rel)
            datas.append((src, dest))

# include character folders defined in core.mahoshojo
for ch in core.mahoshojo.keys():
    if os.path.isdir(ch):
        for root, _, files in os.walk(ch):
            for f in files:
                src = os.path.join(root, f)
                rel = os.path.relpath(src, ch)
                dest = os.path.join(ch, rel)
                datas.append((src, dest))

# Analysis
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

a = Analysis(
    ['gui.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=['keyboard', 'pyperclip', 'win32clipboard'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # show console window
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='gui',
)
