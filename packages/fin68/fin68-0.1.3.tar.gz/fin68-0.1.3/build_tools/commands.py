from __future__ import annotations

import shutil
from pathlib import Path

from setuptools.command.install_lib import install_lib as _install_lib

_PRIVATE_PACKAGE = "private_core"
_KEEP_FILES = {"__init__.py"}


class install_lib(_install_lib):
    """Remove private_core source modules after copying build artifacts."""

    def run(self) -> None:
        super().run()
        self._strip_private_sources()

    def _strip_private_sources(self) -> None:
        install_dir = Path(self.install_dir)
        target = install_dir / _PRIVATE_PACKAGE
        if not target.exists():
            return

        for py_file in target.glob("*.py"):
            if py_file.name in _KEEP_FILES:
                continue
            py_file.unlink(missing_ok=True)

        init_py = target / "__init__.py"
        if not init_py.exists():
            init_py.write_text("__all__ = ()\n", encoding="utf-8")

        for cache_dir in target.glob("__pycache__"):
            shutil.rmtree(cache_dir, ignore_errors=True)
