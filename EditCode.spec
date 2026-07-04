# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

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
    datas=[('icon.ico', '.')], 
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
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
    strip=True,          
    upx=True,            
    console=False,       
    disable_windowed_traceback=False,
    argv_emulation=True, 
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,          
    upx=True,
    upx_exclude=[],
    name='EditCode',
)

app = BUNDLE(
    coll,
    name='EditCode.app',
    icon='icon.ico', 
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
