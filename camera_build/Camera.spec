# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['..\\Windows_VideoStreamApp.py'],
    pathex=[],
    binaries=[('C:\\Windows\\System32\\VERSION.dll', '.'), ('C:\\Windows\\System32\\MMDevAPI.DLL', '.'), ('C:\\Windows\\System32\\WINMM.dll', '.'), ('C:\\Windows\\System32\\MFPlat.DLL', '.'), ('C:\\Windows\\System32\\MF.dll', '.'), ('C:\\Windows\\System32\\d3d9.dll', '.'), ('C:\\Windows\\System32\\EVR.dll', '.'), ('C:\\Windows\\System32\\dxva2.dll', '.'), ('C:\\Windows\\System32\\bcrypt.dll', '.'), ('C:\\Windows\\System32\\IPHLPAPI.DLL', '.'), ('C:\\Windows\\System32\\imagehlp.dll', '.'), ('C:\\Windows\\System32\\dwmapi.dll', '.'), ('C:\\Windows\\System32\\WTSAPI32.dll', '.'), ('C:\\Windows\\System32\\IMM32.dll', '.'), ('C:\\Windows\\System32\\UxTheme.dll', '.'), ('C:\\Windows\\System32\\dxgi.dll', '.'), ('C:\\Windows\\System32\\d3d11.dll', '.'), ('C:\\Windows\\System32\\SHLWAPI.dll', '.'), ('C:\\Windows\\System32\\MFReadWrite.dll', '.'), ('C:\\Windows\\System32\\Secur32.dll', '.'), ('C:\\Windows\\System32\\COMDLG32.dll', '.'), ('C:\\Windows\\System32\\WSOCK32.dll', '.'), ('C:\\Windows\\System32\\MPR.dll', '.'), ('C:\\Windows\\System32\\NETAPI32.dll', '.'), ('C:\\Windows\\System32\\USERENV.dll', '.'), ('D:\\Python_pack\\lib\\site-packages\\pylibdmtx\\libdmtx-64.dll', '.')],
    datas=[],
    hiddenimports=['cv2'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('v', None, 'OPTION')],
    name='Camera',
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
    icon=['C:\\Users\\10417\\Desktop\\windows_camera\\camera_build\\camera.ico'],
)
