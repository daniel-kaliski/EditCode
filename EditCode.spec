# -*- mode: python ; coding: utf-8 -*-
import os
import platform

system = platform.system()

if system == 'Darwin':
    icon_path = 'icon.icns' if os.path.exists('icon.icns') else None
elif system == 'Windows':
    icon_path = 'icon.ico' if os.path.exists('icon.ico') else None
else:
    icon_path = None

a = Analysis(
    ['EditCode.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['webview'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

if system == 'Darwin':

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
        disable_windowed_traceback=False,
        argv_emulation=True,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_path,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        name='EditCode',
    )
    app = BUNDLE(
        coll,
        name='EditCode.app',
        icon=icon_path,
        bundle_identifier='com.danielkaliski.editcode',
        info_plist={
            'CFBundleShortVersionString': '1.1.0',
            'CFBundleName': 'EditCode',
            'LSMinimumSystemVersion': '10.13',
            'NSHighResolutionCapable': True,
            'NSHumanReadableCopyright': 'Copyright © 2026 Daniel Kaliski. All rights reserved.', 
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'All Files',
                    'LSHandlerRank': 'Alternate',
                    'LSItemContentTypes': ['public.data', 'public.content']
                }
            ]
        }
    )
else:

    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name='EditCode',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_path,
    )
