from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import Incomplete


def toml_loads(toml_string: str) -> Incomplete:
    """Load TOML string into a Python object.

    Uses the built-in tomllib module for Python 3.11 and above,
    and the tomli package for earlier versions.
    """
    import sys

    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import tomli as tomllib

    return tomllib.loads(toml_string)
