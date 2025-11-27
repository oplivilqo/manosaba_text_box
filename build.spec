# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for onefolder build (no console window)

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/fonts', 'assets/fonts'),
        ('assets/background', 'assets/background'),
        ('assets/chara', 'assets/chara'),
    ],
    hiddenimports=['keyboard', 'pyperclip', 'win32clipboard'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='gui',
)
