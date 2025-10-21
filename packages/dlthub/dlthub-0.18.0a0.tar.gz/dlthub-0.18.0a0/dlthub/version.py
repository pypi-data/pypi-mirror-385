from importlib.metadata import version as pkg_version

IMPORT_NAME = "dlthub"
PKG_NAME = "dlthub"
__version__ = pkg_version(PKG_NAME)
PKG_REQUIREMENT = f"{PKG_NAME}=={__version__}"
