import enum

try:
    import importlib.metadata as importlib_metadata  # Python >= 3.8
except ImportError:
    import importlib_metadata  # type: ignore


def _get_version() -> str:
    try:
        return importlib_metadata.version(__package__)
    except importlib_metadata.PackageNotFoundError:
        return "dev"


__version__ = _get_version()


class TimeSeriesType(enum.Enum):
    FORECAST = 1
    """Forecast point predictions"""

    HISTORICAL = 2
    """Historical predictions"""
