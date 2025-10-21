try:
    from .tng_python import *
except ImportError:
    pass
import tomllib
from pathlib import Path


def _get_version():
    """Get version from Rust extension or fallback"""
    try:
        from .tng_python import __version__ as rust_version
        return rust_version
    except ImportError:
        try:
            pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            return data["project"]["version"]
        except Exception:
            return "0.1.0"  # current version fallback


__version__ = _get_version()
