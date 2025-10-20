"""This package provides quantum classification algorithms.

The :py:mod:`~tno.quantum.ml.classifiers` package can be installed using pip::

    pip install tno.quantum.ml.classifiers

For usage examples see the documentation of different submodules.
"""

from __future__ import annotations

from tno.quantum.ml.classifiers.svm import SupportVectorMachine
from tno.quantum.ml.classifiers.vc import VariationalClassifier

__all__: list[str] = ["SupportVectorMachine", "VariationalClassifier"]

__version__ = "1.0.0"
