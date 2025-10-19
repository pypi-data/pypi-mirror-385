"""
Absfuyu: Core
-------------
Bases for other features

Version: 5.12.0
Date updated: 17/10/2025 (dd/mm/yyyy)
"""

# Module Package
# ---------------------------------------------------------------------------
__all__ = [
    # color
    "CLITextColor",
    # path
    # "CORE_PATH",
    # class
    "GetClassMembersMixin",
    "BaseClass",
    # wrapper
    "tqdm",
    "unidecode",
    # decorator
    "deprecated",
    "versionadded",
    "versionchanged",
]

__package_feature__ = [
    "beautiful",  # BeautifulOutput
    "docs",  # For (package) hatch's env use only
    "extra",  # DataFrame
    "full",  # All package
    "dev",
]


# Library
# ---------------------------------------------------------------------------
# from importlib.resources import files

# Most used features are imported to core
from absfuyu.core.baseclass import BaseClass, CLITextColor, GetClassMembersMixin
from absfuyu.core.docstring import deprecated, versionadded, versionchanged
from absfuyu.core.dummy_func import tqdm, unidecode

# Path
# ---------------------------------------------------------------------------
# CORE_PATH = files("absfuyu")
