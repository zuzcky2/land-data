# _builtins_stubs.py
import builtins
from typing import Any

def dd(*args: Any, inspect: bool = False) -> None:
    """Dump and Die function for debugging"""
    ...

builtins.dd = dd