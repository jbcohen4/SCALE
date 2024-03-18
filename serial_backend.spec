# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['serial_backend.py'],
    pathex=[],
    binaries=[],
    datas=[
        ("excel-files/NPN_diode_parameters_V0.xlsx", "excel-files"),
        ("excel-files/PNP_diode_parameters_V0.xlsx", "excel-files"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='serial_backend',
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
    onefile=True,# makes it so pyinstaller knows you want a single dependency free .exe
)
