from pathlib import Path
import importlib.util
import sys

from setuptools import setup


def _load_get_extensions():
    try:
        from build_tools.prepare_native import get_extensions  # type: ignore
        return get_extensions
    except ModuleNotFoundError:
        root = Path(__file__).resolve().parent
        tools_dir = root / "build_tools"
        if tools_dir.exists():
            sys.path.insert(0, str(tools_dir))
            spec = importlib.util.spec_from_file_location(
                "build_tools.prepare_native", tools_dir / "prepare_native.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module.get_extensions
        return lambda: []


def _load_cmdclass():
    try:
        from build_tools.commands import install_lib  # type: ignore
        return {"install_lib": install_lib}
    except ModuleNotFoundError:
        root = Path(__file__).resolve().parent
        tools_dir = root / "build_tools"
        if not tools_dir.exists():
            return {}
        sys.path.insert(0, str(tools_dir))
        spec = importlib.util.spec_from_file_location(
            "build_tools.commands", tools_dir / "commands.py"
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return {"install_lib": module.install_lib}
        return {}


setup(
    ext_modules=_load_get_extensions()(),
    include_package_data=True,
    cmdclass=_load_cmdclass(),
)
