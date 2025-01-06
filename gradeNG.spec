# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['平时成绩查询重构版.py'],
    pathex=[],
    binaries=[],
   datas=[('./onnx/common.onnx','ddddocr'),('./onnx/common_old.onnx','ddddocr'),('./onnx/common_det.onnx','ddddocr'),('./onnx/onnxruntime_providers_shared.dll','onnxruntime\\capi'),
    ('./onnx/onnxruntime_providers_shared.dll','ddddocr'),('./onnx/common.onnx','onnxruntime\\capi'),('./onnx/common_old.onnx','onnxruntime\\capi')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='平时成绩查询',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon='E:\dailyTool\pythonProject\cache\gdufs.ico',
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='平时成绩查询',
)
