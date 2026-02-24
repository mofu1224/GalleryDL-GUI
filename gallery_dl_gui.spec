# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Gallery-DL GUI  v1.0.0
# Folder-type distribution (onedir)

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# --- Collect gallery_dl package data ---
gallery_dl_datas = collect_data_files("gallery_dl")
gallery_dl_hiddenimports = collect_submodules("gallery_dl")

a = Analysis(
    ["gallery_dl_gui.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("assets/icon.ico", "assets"),
        ("gallery-dl.conf", "."),
        *gallery_dl_datas,
    ],
    hiddenimports=gallery_dl_hiddenimports + [
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "tkinter.scrolledtext",
        "tkinter.simpledialog",
        "json",
        "glob",
        "certifi",
        "charset_normalizer",
        "requests",
        "urllib3",
        "idna",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib", "numpy", "scipy", "pandas",
        "PIL", "cv2", "PyQt5", "wx",
        "IPython", "notebook", "jupyter",
        "test", "unittest", "doctest",
        "pdb", "turtle", "turtledemo",
        "idlelib",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,   # Folder mode: binaries stay separate
    name="GalleryDL-GUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.ico",
    version_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="GalleryDL-GUI",
)
