from __future__ import annotations

import os
from pathlib import Path
from typing import List

from setuptools import Extension

try:
    from Cython.Build import cythonize
except Exception:
    cythonize = None

EXCLUDE = {"__init__.py", "__main__.py"}


def _discover(core_dir: Path) -> List[Path]:
    return sorted(p for p in core_dir.glob("*.py") if p.name not in EXCLUDE)


def get_extensions():
    root = Path(__file__).resolve().parents[1]
    core_dir = root / "private_core"
    if not core_dir.exists():
        return []
    srcs = _discover(core_dir)
    if not srcs:
        return []

    exts = []
    for src in srcs:
        mod = src.with_suffix("").name
        fullname = f"private_core.{mod}"
        rel_src = os.path.relpath(src, root).replace(os.sep, "/")
        exts.append(Extension(fullname, sources=[rel_src]))

    if cythonize is None:
        return exts  # cho phép đọc metadata mà không có Cython
    cythonized = cythonize(
        exts, compiler_directives={"language_level": "3", "embedsignature": True}
    )
    for ext in cythonized:
        rel_sources = []
        for src in ext.sources:
            src_path = Path(src)
            if not src_path.is_absolute():
                src_path = (root / src_path).resolve(strict=False)
            rel_sources.append(
                os.path.relpath(str(src_path), str(root)).replace(os.sep, "/")
            )
        ext.sources = rel_sources
    return cythonized
