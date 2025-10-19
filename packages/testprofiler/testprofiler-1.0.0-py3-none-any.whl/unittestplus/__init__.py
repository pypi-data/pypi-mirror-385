from .core import unittestplus
from .manipulate import run_regression
from .testsuite import TestSuite

__version__ = "1.0.0"  # Match with pyproject.toml

__all__ = [
    "unittestplus",
    "run_regression",
    "TestSuite",
]
