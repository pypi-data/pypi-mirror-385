"""Azure Text-to-Speech Terminal Client"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("azure-tts-client")
except importlib.metadata.PackageNotFoundError:
    # Package is not installed, try reading from pyproject.toml
    import tomllib
    from pathlib import Path
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, 'rb') as f:
            pyproject_data = tomllib.load(f)
            __version__ = pyproject_data.get('project', {}).get('version', '0.0.0')
    except Exception:
        __version__ = "0.0.0"
