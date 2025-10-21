#!/usr/bin/env python
# -*- coding: utf-8 -*-
# type: ignore
# ruff: noqa
# mypy: ignore-errors
# pylint: skip-file
"""
This is a test file that demonstrates various Python import patterns.
It is used for testing the import analysis functionality of showmereqs.
This file intentionally includes all kinds of import statements and should not be analyzed for actual dependencies.

DO NOT EDIT - This file is part of the test suite.
"""

# 1. built-in module
import datetime

# 2. multiple imports
import json
import os

# 3. alias imports
import numpy as np
import pandas as pd

# 4. dot imports
import os.path
import sys
import xml.dom.minidom

# 5. from imports
from math import pi

# 6. from multiple imports
from os import makedirs, path, remove

# 7. from dot imports
from os.path import exists, join
from time import sleep
from xml.dom.minidom import parse


# 8. from alias imports
from tensorflow import keras as k
from torch.nn import functional as F

# 9. relative imports
from ... import module_0
from ...module_1 import functionB
from .. import module_01
from ..package_01 import module_010
from .module_020 import functionA

# 10. conditional imports
try:
    import scipy
except ImportError:
    import numpy


# 11. within function imports
def some_function():
    import requests
    from PIL import Image

    return requests, Image


# 12. within class imports
class SomeClass:
    import threading

    def __init__(self):
        import queue

        self.queue = queue.Queue()

    def method(self):
        from collections import defaultdict

        return defaultdict(list)


# 13. if conditional imports
if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

# 14. star imports
from math import *

# 15. complex from imports
from torch.nn.functional import dropout, gelu, relu
from torch.nn.functional import softmax as soft


# 16. dynamic imports     unable to analyze
def dynamic_import():
    module_name = "yaml"
    # 使用 __import__
    yaml1 = __import__(module_name)

    # 使用 importlib
    import importlib

    yaml2 = importlib.import_module(module_name)

    return yaml1, yaml2


# 17. nested conditional imports
try:
    import torch

    try:
        import torch.cuda
    except ImportError:
        import torch.cpu
except ImportError:
    try:
        import tensorflow as tf
    except ImportError:
        import theano


# 18. with statement imports
def with_import():
    with open("test.txt") as f:
        import csv

        return csv


# 19. imports in list/dict comprehensions   unable to analyze
def comprehension_import():
    return [__import__(x) for x in ["os", "sys", "time"]]


# 20. imports in async context
async def async_function():
    import asyncio

    import aiohttp

    return aiohttp, asyncio


# 21. unknown import
import guidoooo

if __name__ == "__main__":
    # use some imports to prevent them from being optimized away
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Pi value: {pi}")
    print(f"NumPy random: {np.random.rand()}")
