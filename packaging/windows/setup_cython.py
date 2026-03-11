from __future__ import annotations

import argparse
from pathlib import Path

from Cython.Build import cythonize
from setuptools import Extension, setup


EXCLUDED_RELATIVE_PATHS = {
    "jarvis/__main__.py",
    "jarvis/cli/commands.py",
}


def discover_extensions(source_root: Path) -> tuple[list[Extension], list[Path]]:
    package_root = source_root / "jarvis"
    if not package_root.exists():
        raise FileNotFoundError(f"Missing package root: {package_root}")

    extensions: list[Extension] = []
    compiled_sources: list[Path] = []

    for path in sorted(package_root.rglob("*.py")):
        rel = path.relative_to(source_root).as_posix()
        if path.name == "__init__.py" or rel in EXCLUDED_RELATIVE_PATHS:
            continue
        module_name = ".".join(path.relative_to(source_root).with_suffix("").parts)
        extensions.append(Extension(module_name, [str(path)]))
        compiled_sources.append(path)

    return extensions, compiled_sources


def strip_sources(source_root: Path, compiled_sources: list[Path]) -> None:
    for source in compiled_sources:
        if source.exists():
            source.unlink()
        c_file = source.with_suffix(".c")
        cpp_file = source.with_suffix(".cpp")
        if c_file.exists():
            c_file.unlink()
        if cpp_file.exists():
            cpp_file.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile jarvis package modules with Cython.")
    parser.add_argument(
        "--source-root",
        type=Path,
        required=True,
        help="Path to the staging source tree that contains the jarvis package.",
    )
    parser.add_argument(
        "--strip-sources",
        action="store_true",
        help="Delete compiled .py source files after .pyd/.so modules are created.",
    )
    parser.add_argument(
        "--annotate",
        action="store_true",
        help="Emit Cython HTML annotation files into the staging tree.",
    )
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    extensions, compiled_sources = discover_extensions(source_root)
    if not extensions:
        raise SystemExit("No modules found to compile.")

    ext_modules = cythonize(
        extensions,
        compiler_directives={"language_level": "3"},
        annotate=args.annotate,
    )

    setup(
        name="jarvis-cython-build",
        script_args=["build_ext", "--inplace"],
        ext_modules=ext_modules,
    )

    if args.strip_sources:
        strip_sources(source_root, compiled_sources)


if __name__ == "__main__":
    main()
