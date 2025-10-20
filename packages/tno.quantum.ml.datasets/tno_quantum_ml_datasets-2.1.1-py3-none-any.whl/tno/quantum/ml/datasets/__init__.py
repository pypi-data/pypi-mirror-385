"""This package contains mainly wrapper functions around :mod:`sklearn.datasets`.

The :mod:`~tno.quantum.ml.datasets` package only wraps some of the functionality of the
:mod:`sklearn.datasets`. This package is used for testing the :mod:`tno.quantum.ml`
classifiers and clustering algorithms in an easy, reproducible and consistent way.
"""

from tno.quantum.ml.datasets._anomalous_spiky_time_series import (
    get_anomalous_spiky_time_series_dataset,
)
from tno.quantum.ml.datasets._bars_and_stripes import (
    get_bars_and_stripes_dataset,
)
from tno.quantum.ml.datasets._blobs_clustering import (
    get_blobs_clustering_dataset,
)
from tno.quantum.ml.datasets._circles import get_circles_dataset
from tno.quantum.ml.datasets._iris import get_iris_dataset
from tno.quantum.ml.datasets._linearly_separable import (
    get_linearly_separable_dataset,
)
from tno.quantum.ml.datasets._moons import get_moons_dataset
from tno.quantum.ml.datasets._utils import show_images_dataset
from tno.quantum.ml.datasets._wine import get_wine_dataset

__all__ = [
    "get_anomalous_spiky_time_series_dataset",
    "get_bars_and_stripes_dataset",
    "get_blobs_clustering_dataset",
    "get_circles_dataset",
    "get_iris_dataset",
    "get_linearly_separable_dataset",
    "get_moons_dataset",
    "get_wine_dataset",
    "show_images_dataset",
]

__version__ = "2.1.1"
