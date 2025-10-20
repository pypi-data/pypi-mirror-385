"""This package provides quantum clustering algorithms.

The :py:mod:`~tno.quantum.ml.clustering` package can be installed using pip::

    pip install tno.quantum.ml.clustering

To additionally install all external QUBO solvers, you can use the [all] flag::

    pip install tno.quantum.ml.clustering'[all]'

For usage examples see the documentation of different submodules.
"""

from __future__ import annotations

from tno.quantum.ml.clustering.bkmeans import QBKMeans
from tno.quantum.ml.clustering.kmedoids import QKMedoids

__all__: list[str] = ["QBKMeans", "QKMedoids"]

__version__ = "1.0.0"
