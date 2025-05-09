# -*- mode: python ; coding: utf-8 -*-
# BackEnd
import os
import shutil

def collectSubdirs(base):
    excluded = {'build', 'dist', '__pycache__'}
    datas = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in excluded]
        for file in files:
            filePath = os.path.join(root, file)
            relativePath = os.path.relpath(filePath, base)
            datas.append((filePath, os.path.join(base, os.path.dirname(relativePath))))
    return datas

datas = collectSubdirs('.')

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tensorflow',
        'tensorflow.keras.models',
        'tensorflow.python.keras.engine.training',
        'engineio.async_drivers.threading',
        'joblib',
        'sklearn',
        'scipy',
        'h5py',
        'pandas',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SecurAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity='',
    entitlements_file=None,
    onefile=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='run'
)