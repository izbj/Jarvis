# Windows Build

This directory contains the Windows-only build chain for compiling `jarvis` with Cython and freezing it with PyInstaller.

All intermediate and final artifacts stay under this directory:

- `packaging/windows/work/`
- `packaging/windows/build/`
- `packaging/windows/dist/`

Nothing is written into `jarvis/`.

## What The Build Does

1. Copies the repository sources into `packaging/windows/work/source/`
2. Compiles most `jarvis/*.py` modules into extension modules with Cython
3. Strips compiled `.py` sources from the staged copy
4. Freezes the staged app with PyInstaller

Excluded from Cython compilation:

- `jarvis/__main__.py`
- `jarvis/cli/commands.py`
- all `__init__.py` files

Those files stay as Python entry/runtime glue.

## Requirements

- Windows
- Python 3.11 or newer
- A working C/C++ compiler for the Python version you use
  - For CPython on Windows, the practical choice is Visual Studio Build Tools / MSVC

## Quick Start

From PowerShell:

```powershell
cd <repo>
.\packaging\windows\build_windows.ps1 -Mode onedir -Clean
```

For a single-file bundle:

```powershell
.\packaging\windows\build_windows.ps1 -Mode onefile -Clean
```

Generated artifacts land in:

- `packaging/windows/dist/jarvis/` for `onedir`
- `packaging/windows/dist/jarvis.exe` for `onefile`

## Manual Build

```powershell
py -m pip install --upgrade pip
py -m pip install cython pyinstaller
py -m pip install .
py .\packaging\windows\build_windows.py --mode onedir --clean
```

## Notes

- Build on Windows for Windows. This flow is not a cross-compile setup.
- If `bridge/` exists, it is included as data. If you have removed WhatsApp support entirely, nothing special is required.
- Start with `onedir`. It is easier to debug missing imports or missing data files than `onefile`.
