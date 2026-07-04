# -*- mode: python ; coding: utf-8 -*-
import os
import platform

# 1. AUTOMATYCZNE WYKRYWANIE SYSTEMU I IKONY
system = platform.system()

if system == 'Darwin':
    # macOS używa plików .icns
    icon_path = 'icon.icns' if os.path.exists('icon.icns') else None
elif system == 'Windows':
    # Windows używa plików .ico
    icon_path = 'icon.ico' if os.path.exists('icon.ico') else None
else:
    icon_path = None

# 2. KONFIGURACJA GŁÓWNA
a = Analysis(
    ['EditCode.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['webview'], # Wymuszamy dołączenie pywebview
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[], # Brak wykluczeń - nowa biblioteka jest naturalnie lekka!
    noarchive=False,
)

pyz = PYZ(a.pure)

# 3. BUDOWANIE PLIKU WYKONYWALNEGO
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
    console=False, # Ukrywa czarne okienko terminala systemowego w tle
    disable_windowed_traceback=False,
    argv_emulation=True, # Krytyczne dla macOS (pozwala otwierać pliki dwukrotnym kliknięciem)
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
    upx_exclude=[],
    name='EditCode',
)

# 4. BUDOWANIE PACZKI .APP (Tylko dla macOS)
if system == 'Darwin':
    app = BUNDLE(
        coll,
        name='EditCode.app',
        icon=icon_path,
        bundle_identifier='com.danielkaliski.editcode',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleName': 'EditCode',
            'LSMinimumSystemVersion': '10.13',
            'NSHumanReadableCopyright': 'Copyright © 2026 Daniel Kaliski. All rights reserved.',
            'NSHighResolutionCapable': True, # Wymusza ostry tekst na ekranach Retina
            # Rejestracja programu w macOS jako edytora tekstowego
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'All Files',
                    'LSHandlerRank': 'Alternate',
                    'LSItemContentTypes': ['public.data', 'public.content']
                }
            ]
        }
    )