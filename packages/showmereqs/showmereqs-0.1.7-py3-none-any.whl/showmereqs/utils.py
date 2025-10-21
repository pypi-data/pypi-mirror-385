"""
This module contains utility functions for ShowMeReqs.

Some package mapping and stdlib data are derived from pipreqs:
https://github.com/bndr/pipreqs/
Licensed under Apache License, Version 2.0
"""

import json
import sys
from pathlib import Path

config_dir = Path(__file__).parent / "config"
special_mapping_path = config_dir / "mapping"
stdlib_path = config_dir / "stdlib"
ignore_path = config_dir / "ignore.json"

_special_mapping: dict[str, str] = {}
_stdlib_modules: set[str] = set()
_ignore_dirs: set[str] = set()


def get_mapping():
    global _special_mapping
    if len(_special_mapping) == 0:
        with open(special_mapping_path, "r") as f:
            for line in f.read().splitlines():
                import_name, package_name = line.strip().split(":")
                _special_mapping[import_name] = package_name

    return _special_mapping


def get_builtin_modules() -> set[str]:
    """get python builtin modules"""
    global _stdlib_modules
    if len(_stdlib_modules) == 0:
        # method after Python 3.10+
        if hasattr(sys, "stdlib_module_names"):
            _stdlib_modules = set(sys.stdlib_module_names)

        # method before Python 3.10
        else:
            with open(stdlib_path, "r") as f:
                _stdlib_modules = set(f.read().splitlines())
    return _stdlib_modules


def get_ignore_dirs():
    global _ignore_dirs
    if len(_ignore_dirs) == 0:
        with open(ignore_path, "r") as f:
            _ignore_dirs = set(json.load(f)["ignore_dirs"])

    return _ignore_dirs
