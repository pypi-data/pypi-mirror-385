from importlib.metadata import version

try:
    __version__ = version('claude-cache-savings')
except Exception:
    __version__ = 'unknown'

del version

__all__ = [
    '__version__',
]
