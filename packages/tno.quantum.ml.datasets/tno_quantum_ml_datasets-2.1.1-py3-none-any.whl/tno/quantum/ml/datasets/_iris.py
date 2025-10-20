"""Module for iris dataset."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from sklearn import datasets
from tno.quantum.utils.validation import check_int

from tno.quantum.ml.datasets._utils import _pre_process_data, _safe_train_test_split


def get_iris_dataset(
    n_features: int = 4,
    n_classes: int = 3,
    random_seed: int = 0,
    test_size: float | int | None = None,
) -> tuple[
    NDArray[np.float64], NDArray[np.int_], NDArray[np.float64], NDArray[np.int_]
]:
    r"""Generate the iris dataset.

    This function wraps :func:`~sklearn.datasets.load_iris` of :mod:`sklearn.datasets`.
    The dataset is loaded and split into training and validation data.

    Example usage:

        >>> from tno.quantum.ml.datasets import get_iris_dataset
        >>> X_train, y_train, X_val, y_val = get_iris_dataset()
        >>> print(f"{X_train.shape=}\n{y_train.shape=}\n{X_val.shape=}\n{y_val.shape=}")
        X_train.shape=(112, 4)
        y_train.shape=(112,)
        X_val.shape=(38, 4)
        y_val.shape=(38,)

    Args:
        n_features: Number of features. Defaults to 4.
        n_classes: Number of classes, must be 1, 2 or 3. Defaults to 3.
        random_seed: Seed to give to the random number generator. Defaults to 0.
        test_size: The proportion of the dataset that is included in the test-split.
            Either represented by a percentage in the range [0.0, 1.0) or as absolute
            number of test samples in the range [1, inf). Defaults to 0.25.

    Returns:
        A tuple containing ``X_training``, ``y_training``, ``X_validation`` and
        ``y_validation`` of the iris dataset.
    """
    # Validate input
    n_features = check_int(n_features, name="n_features", l_bound=1)
    n_classes = check_int(n_classes, name="n_classes", l_bound=1)
    random_seed = check_int(random_seed, name="random_seed", l_bound=0)

    # Load data and take subset
    X, y = datasets.load_iris(return_X_y=True)
    X, y = _pre_process_data(X, y, n_features, n_classes)

    # Split into training and validation data sets
    return _safe_train_test_split(X, y, test_size=test_size, random_state=random_seed)
