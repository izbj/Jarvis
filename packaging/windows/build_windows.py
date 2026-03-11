from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGING_ROOT = Path(__file__).resolve().parent
WORK_ROOT = PACKAGING_ROOT / "work"
STAGING_ROOT = WORK_ROOT / "source"
SPEC_ROOT = WORK_ROOT / "spec"
PYINSTALLER_WORK_ROOT = PACKAGING_ROOT / "build"
DIST_ROOT = PACKAGING_ROOT / "dist"

COPY_TARGETS = [
    "jarvis",
    "pyproject.toml",
    "README.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage, Cython-compile, and freeze jarvis for Windows."
    )
    parser.add_argument(
        "--mode",
        choices=("onedir", "onefile"),
        default="onedir",
        help="PyInstaller bundle mode. Start with onedir for easier debugging.",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python interpreter to use for the build environment.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete previous packaging/windows build outputs before building.",
    )
    parser.add_argument(
        "--annotate",
        action="store_true",
        help="Emit Cython HTML annotation files into packaging/windows/work/source.",
    )
    parser.add_argument(
        "--allow-non-windows",
        action="store_true",
        help="Skip the Windows platform guard. Useful only for script validation, not release builds.",
    )
    return parser.parse_args()


def ensure_windows(args: argparse.Namespace) -> None:
    if os.name != "nt" and not args.allow_non_windows:
        raise SystemExit(
            "This build must run on Windows. Re-run on Windows or pass --allow-non-windows for dry-run validation only."
        )


def reset_outputs(clean: bool) -> None:
    if clean:
        for path in (WORK_ROOT, PYINSTALLER_WORK_ROOT, DIST_ROOT):
            if path.exists():
                shutil.rmtree(path)

    for path in (WORK_ROOT, SPEC_ROOT, PYINSTALLER_WORK_ROOT, DIST_ROOT):
        path.mkdir(parents=True, exist_ok=True)


def stage_project() -> None:
    if STAGING_ROOT.exists():
        shutil.rmtree(STAGING_ROOT)
    STAGING_ROOT.mkdir(parents=True, exist_ok=True)

    for name in COPY_TARGETS:
        src = ROOT / name
        dst = STAGING_ROOT / name
        if src.is_dir():
            shutil.copytree(
                src,
                dst,
                ignore=shutil.ignore_patterns(
                    "__pycache__",
                    "*.pyc",
                    "*.pyo",
                    "*.pyd",
                    "*.so",
                ),
            )
        elif src.exists():
            shutil.copy2(src, dst)

    optional_bridge = ROOT / "bridge"
    if optional_bridge.exists():
        shutil.copytree(
            optional_bridge,
            STAGING_ROOT / "bridge",
            ignore=shutil.ignore_patterns("node_modules", "dist", "__pycache__"),
        )


def discover_hidden_imports(source_root: Path) -> list[str]:
    imports: list[str] = []
    package_root = source_root / "jarvis"
    for path in sorted(package_root.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        module_name = ".".join(path.relative_to(source_root).with_suffix("").parts)
        imports.append(module_name)
    return imports


def add_data_args(source_root: Path) -> list[str]:
    sep = ";" if os.name == "nt" else ":"
    args: list[str] = []

    templates = source_root / "jarvis" / "templates"
    if templates.exists():
        args += ["--add-data", f"{templates}{sep}jarvis/templates"]

    builtin_skills = source_root / "jarvis" / "skills"
    if builtin_skills.exists():
        args += ["--add-data", f"{builtin_skills}{sep}jarvis/skills"]

    bridge = source_root / "bridge"
    if bridge.exists():
        args += ["--add-data", f"{bridge}{sep}bridge"]

    return args


def run(cmd: list[str], cwd: Path) -> None:
    print(f"\n>>> {' '.join(str(part) for part in cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def compile_with_cython(args: argparse.Namespace) -> None:
    cmd = [
        args.python,
        str(PACKAGING_ROOT / "setup_cython.py"),
        "--source-root",
        str(STAGING_ROOT),
        "--strip-sources",
    ]
    if args.annotate:
        cmd.append("--annotate")
    run(cmd, cwd=STAGING_ROOT)


def freeze_with_pyinstaller(args: argparse.Namespace, hidden_imports: list[str]) -> None:
    entrypoint = STAGING_ROOT / "jarvis" / "__main__.py"

    cmd = [
        args.python,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        "jarvis",
        "--console",
        f"--{args.mode}",
        "--distpath",
        str(DIST_ROOT),
        "--workpath",
        str(PYINSTALLER_WORK_ROOT),
        "--specpath",
        str(SPEC_ROOT),
        "--paths",
        str(STAGING_ROOT),
    ]

    for hidden_import in hidden_imports:
        cmd += ["--hidden-import", hidden_import]

    cmd += add_data_args(STAGING_ROOT)
    cmd.append(str(entrypoint))

    run(cmd, cwd=STAGING_ROOT)


def main() -> None:
    args = parse_args()
    ensure_windows(args)
    reset_outputs(clean=args.clean)
    stage_project()
    hidden_imports = discover_hidden_imports(STAGING_ROOT)
    compile_with_cython(args)
    freeze_with_pyinstaller(args, hidden_imports)
    print("\nBuild complete.")
    print(f"Staging tree: {STAGING_ROOT}")
    print(f"PyInstaller work dir: {PYINSTALLER_WORK_ROOT}")
    print(f"Artifacts: {DIST_ROOT}")


if __name__ == "__main__":
    main()
