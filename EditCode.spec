# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['EditCode.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.ico', '.')], 
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EditCode',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, 
    icon='icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EditCode',
)

app = BUNDLE(
    coll,
    name='EditCode.app',
    icon='icon.icns', 
    bundle_identifier='com.danielkaliski.editcode',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'NSRequiresAquaSystemAppearance': False, 
        'CFBundleName': 'EditCode',
        'CFBundleDisplayName': 'EditCode',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'LSMinimumSystemVersion': '10.13.0',
        'NSHumanReadableCopyright': 'Copyright © 2026 Daniel Kaliski. All rights reserved.',
    },
)