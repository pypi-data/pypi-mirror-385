from importlib import metadata as _md

from .utils import PublishConfig, default_run_id  # re-export key types

try:  # runtime version (works inside installed env)
    __version__ = _md.version("pytest-allure-host")
except Exception:  # pragma: no cover
    __version__ = "0.0.0+unknown"

__all__ = [
    "PublishConfig",
    "default_run_id",
    "__version__",
]
