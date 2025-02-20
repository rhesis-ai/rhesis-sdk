from rhesis.config import api_key, base_url
import importlib.metadata

# Get version from pyproject.toml via package metadata
__version__ = importlib.metadata.version("rhesis-sdk")

# Make these variables available at the module level
__all__ = ["api_key", "base_url", "__version__"]
