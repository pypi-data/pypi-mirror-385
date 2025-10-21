from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("wt_templatetags")
except PackageNotFoundError:
    # package is not installed
    __version__ = "dev"
