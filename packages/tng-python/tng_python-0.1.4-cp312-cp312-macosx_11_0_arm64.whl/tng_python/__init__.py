try:
    from .tng_python import *
except ImportError:
    # Rust extension not available (e.g., during testing)
    pass
import tomllib
from pathlib import Path

def _get_version():
    """Get version from Rust extension or fallback"""
    try:
        # First try to get from Rust extension (works when installed)
        from .tng_python import __version__ as rust_version
        return rust_version
    except ImportError:
        # Fallback: try reading from pyproject.toml (works in development)
        try:
            pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            return data["project"]["version"]
        except Exception:
            return "0.1.1"  # current version fallback

__version__ = _get_version()
