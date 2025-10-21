from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("polyserde")
except PackageNotFoundError:
    # Package is not installed, so version is not available
    __version__ = "unknown"

from .polyserde import PolymorphicSerde

__all__ = ["PolymorphicSerde", "__version__"]
