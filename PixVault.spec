# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build script for PixVault.

Produces a single-file, windowed executable named ``PixVault.exe``.

Non-trivial details handled here:

- ``processing/profiles/*.icc`` profiles are bundled as data so the color
  space engine can load them from inside the frozen bundle.
- ``pillow-heif`` installs its native ``_pillow_heif.pyd`` plus the libheif /
  libde265 / libx265 shared libraries directly in ``site-packages`` rather
  than inside the ``pillow_heif`` package folder.  The delvewheel shim in
  ``pillow_heif/__init__.py`` calls ``os.add_dll_directory`` on the bundle
  root at import time, so those DLLs are collected into the bundle root.
- ``pillow-avif-plugin`` registers its Pillow plugin on import; it is listed
  as a hidden import so AVIF conversion works from the frozen executable.
"""

import glob
import os
import sysconfig

import pillow_avif
import pillow_heif


site_packages = os.path.abspath(sysconfig.get_paths()["purelib"])

# ---------------------------------------------------------------------------
# Native binaries for pillow-heif / pillow-avif
# ---------------------------------------------------------------------------

heif_binaries = []
for pattern in (
    "_pillow_heif*.pyd",
    "libheif-*.dll",
    "libde265-*.dll",
    "libx265-*.dll",
    "libstdc++-*.dll",
    "libgcc_s_seh-*.dll",
    "libwinpthread-*.dll",
):
    heif_binaries.extend(
        (path, ".") for path in glob.glob(os.path.join(site_packages, pattern))
    )

avif_binaries = []
avif_pkg_dir = os.path.dirname(pillow_avif.__file__)
avif_binaries.extend(
    (path, "pillow_avif") for path in glob.glob(os.path.join(avif_pkg_dir, "*.pyd"))
)

binaries = heif_binaries + avif_binaries

# ---------------------------------------------------------------------------
# Data files (ICC profiles)
# ---------------------------------------------------------------------------

datas = [
    (os.path.join("processing", "profiles"), "processing/profiles"),
]

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

a = Analysis(
    ["main.py"],
    pathex=[os.path.dirname(os.path.abspath(SPECPATH))],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "pillow_heif",
        "pillow_heif._lib_info",
        "pillow_avif",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

# ---------------------------------------------------------------------------
# Single-file executable
# ---------------------------------------------------------------------------

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="PixVault",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=os.path.join("packaging", "version_info.txt"),
    icon=os.path.join("icons", "pixvault.ico"),
)