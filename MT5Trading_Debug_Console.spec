# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['debug_main.py'],
    pathex=[],
    binaries=[],
    datas=[('config', 'config'), ('resources', 'resources'), ('data', 'data'), ('app', 'app'), ('debug_place_batch_order.py', '.'), ('debug_batch_order.py', '.'), ('debug_trading_buttons_controller.py', '.'), ('debug_gui.py', '.')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='MT5Trading_Debug_Console',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
