# -*- mode: python ; coding: utf-8 -*-
import os

icon_file = 'icon.ico' if os.path.exists('icon.ico') else None
added_files = [('icon.ico', '.')] if os.path.exists('icon.ico') else []

# Odcinamy ciężkie biblioteki
excluded_modules = [
    'tkinter', 'unittest', 'pydoc', 'pdb', 'email', 'http', 'xml',
    'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'PySide6',
    'IPython', 'jupyter', 'notebook', 'PyQt5', 'wx', 'curses',
    'sqlite3', 'test', 'PyInstaller'
]

a = Analysis(
    ['EditCode.py'],
    pathex=[],
    binaries=[],
    datas=added_files, 
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

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
    icon=icon_file, 
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
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleName': 'EditCode',
        'LSMinimumSystemVersion': '10.13',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'All Files',
                'LSHandlerRank': 'Alternate',
                'LSItemContentTypes': ['public.data', 'public.content']
            }
        ]
    }
)
