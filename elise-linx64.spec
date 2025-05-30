# -*- mode: python ; coding: utf-8 -*-

import os
conda_path = str(os.environ["CONDA_PREFIX"])
print(conda_path)

entry_a = Analysis(
    ['framework/elise.py'],
    pathex=['.', 'framework/realsim'],
    binaries=[],
    datas=[
        (f"{conda_path}/lib/python3.13/site-packages/dash_extensions/package-info.json", 'dash_extensions'),
        (f"{conda_path}/lib/python3.13/site-packages/dash_extensions/dash_extensions.js", 'dash_extensions'),
        ('api/loader/*.py', 'api/loader'),
        ('framework/batch/*.py', 'batch'),
        ('framework/common/*.py', 'common'),
        ('framework/webui/ws_server.py', 'webui'),
        ('framework/webui/assets', 'webui/assets'),
        ('framework/realsim/*.py', 'realsim'),
        ('framework/realsim/cluster/*.py', 'realsim/cluster'),
        ('framework/realsim/jobs/*.py', 'realsim/jobs'),
        ('framework/realsim/generators/*.py', 'realsim/generators'),
        ('framework/realsim/generators/distribution/*.py', 'realsim/generators/distribution'),
        ('framework/realsim/scheduler/*.py', 'realsim/scheduler'),
        ('framework/realsim/scheduler/schedulers/*.py', 'realsim/scheduler/schedulers'),
        ('framework/realsim/scheduler/coschedulers/ranks/*.py', 'realsim/scheduler/coschedulers/ranks'),
        ('framework/realsim/scheduler/coschedulers/rulebased/*.py', 'realsim/scheduler/coschedulers/rulebased'),
        ('framework/realsim/logger/*.py', 'realsim/logger')
    ],
    hiddenimports=[
        'mpi4py', 
        'procset', 
        'websockets',
        'websocket',
        'kaleido'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

run_mpi_a = Analysis(
    ['framework/batch/run_mpi.py'],
    pathex=['.', 'framework/realsim'],
    binaries=[],
    datas=[
        ('framework/common/*.py', 'common'),
        ('framework/realsim/*.py', 'realsim'),
        ('framework/realsim/cluster/*.py', 'realsim/cluster'),
        ('framework/realsim/jobs/*.py', 'realsim/jobs'),
        ('framework/realsim/generators/*.py', 'realsim/generators'),
        ('framework/realsim/generators/distribution/*.py', 'realsim/generators/distribution'),
        ('framework/realsim/scheduler/*.py', 'realsim/scheduler'),
        ('framework/realsim/scheduler/schedulers/*.py', 'realsim/scheduler/schedulers'),
        ('framework/realsim/scheduler/coschedulers/ranks/*.py', 'realsim/scheduler/coschedulers/ranks'),
        ('framework/realsim/scheduler/coschedulers/rulebased/*.py', 'realsim/scheduler/coschedulers/rulebased'),
        ('framework/realsim/logger/*.py', 'realsim/logger')
    ],
    hiddenimports=[
        'mpi4py'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

run_mp_a = Analysis(
    ['framework/batch/run_mp.py'],
    pathex=['.', 'framework/realsim'],
    binaries=[],
    datas=[
        ('framework/common/*.py', 'common'),
        ('framework/realsim/*.py', 'realsim'),
        ('framework/realsim/cluster/*.py', 'realsim/cluster'),
        ('framework/realsim/jobs/*.py', 'realsim/jobs'),
        ('framework/realsim/generators/*.py', 'realsim/generators'),
        ('framework/realsim/generators/distribution/*.py', 'realsim/generators/distribution'),
        ('framework/realsim/scheduler/*.py', 'realsim/scheduler'),
        ('framework/realsim/scheduler/schedulers/*.py', 'realsim/scheduler/schedulers'),
        ('framework/realsim/scheduler/coschedulers/ranks/*.py', 'realsim/scheduler/coschedulers/ranks'),
        ('framework/realsim/scheduler/coschedulers/rulebased/*.py', 'realsim/scheduler/coschedulers/rulebased'),
        ('framework/realsim/logger/*.py', 'realsim/logger')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

progress_server_a = Analysis(
    ['framework/batch/progress_server.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('framework/common/*.py', 'common'),
    ],
    hiddenimports=[
        'cProfile',
        'platform',
        'psutil'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

ws_server_a = Analysis(
    ['framework/webui/ws_server.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
  
entry_pyz = PYZ(entry_a.pure)
entry_exe = EXE(
    entry_pyz,
    entry_a.scripts,
    [],
    exclude_binaries=True,
    name='elise',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/promo/elise-marker.ico",
)

run_mpi_pyz = PYZ(run_mpi_a.pure)
run_mpi_exe = EXE(
    run_mpi_pyz,
    run_mpi_a.scripts,
    [],
    exclude_binaries=True,
    name='run_mpi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

run_mp_pyz = PYZ(run_mp_a.pure)
run_mp_exe = EXE(
    run_mp_pyz,
    run_mp_a.scripts,
    [],
    exclude_binaries=True,
    name='run_mp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

progress_server_pyz = PYZ(progress_server_a.pure)
progress_server_exe = EXE(
    progress_server_pyz,
    progress_server_a.scripts,
    [],
    exclude_binaries=True,
    name='progress_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=False
)

ws_server_pyz = PYZ(ws_server_a.pure)
ws_server_exe = EXE(
    ws_server_pyz,
    ws_server_a.scripts,
    [],
    exclude_binaries=True,
    name='ws_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=False
)

coll = COLLECT(
    entry_exe, 
    entry_a.binaries, 
    entry_a.zipfiles, 
    entry_a.datas, 
    run_mpi_exe,
    run_mpi_a.binaries, 
    run_mpi_a.zipfiles, 
    run_mpi_a.datas, 
    run_mp_exe,
    run_mp_a.binaries, 
    run_mp_a.zipfiles, 
    run_mp_a.datas, 
    progress_server_exe,
    progress_server_a.binaries, 
    progress_server_a.zipfiles, 
    progress_server_a.datas, 
    ws_server_exe,
    ws_server_a.binaries, 
    ws_server_a.zipfiles, 
    ws_server_a.datas, 
    strip=False, 
    upx=True, 
    upx_exclude=[],
    name='elise',
)