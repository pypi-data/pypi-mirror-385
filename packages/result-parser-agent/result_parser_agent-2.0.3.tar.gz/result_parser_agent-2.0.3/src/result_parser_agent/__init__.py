from .config.settings import settings


# Read version from pyproject.toml dynamically
def _get_version() -> str:
    """Get version from pyproject.toml."""
    import re
    from pathlib import Path

    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)

    # Fallback version
    return "2.0.1"


__version__ = _get_version()
__author__ = "Akhilreddy"
__email__ = "akhil@Infobellit.com"

__all__ = [
    "settings",
]
