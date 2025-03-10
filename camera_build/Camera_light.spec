# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../Camera V1.2.py'],
    pathex=[],
    binaries=[('/usr/local/bin/uvc-util', '.')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('v', None, 'OPTION')],
    name='Camera_light',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['camera.icns'],
)
app = BUNDLE(
    exe,
    name='Camera_light.app',
    icon='./camera.icns',
    bundle_identifier=None,
)
