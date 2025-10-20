"""Module for circles dataset."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from sklearn import datasets
from tno.quantum.utils.validation import check_int

from tno.quantum.ml.datasets._utils import _safe_train_test_split


def get_circles_dataset(
    n_samples: int = 100,
    random_seed: int = 0,
    test_size: int | float | None = None,
) -> tuple[
    NDArray[np.float64], NDArray[np.int_], NDArray[np.float64], NDArray[np.int_]
]:
    r"""Generate a random dataset with the shape of two circles.

    This function wraps :func:`~sklearn.datasets.make_circles` of
    :mod:`sklearn.datasets` with a fixed noise factor of `0.2` and factor of `0.5`.

    Example usage:

        >>> from tno.quantum.ml.datasets import get_circles_dataset
        >>> X_train, y_train, X_val, y_val = get_circles_dataset(n_samples=100, test_size=0.4)
        >>> print(f"{X_train.shape=}\n{y_train.shape=}\n{X_val.shape=}\n{y_val.shape=}")
        X_train.shape=(60, 2)
        y_train.shape=(60,)
        X_val.shape=(40, 2)
        y_val.shape=(40,)

    Args:
        n_samples: Total number of generated data samples.
        random_seed: Seed to give to the random number generator. Defaults to 0.
        test_size: The proportion of the dataset that is included in the test-split.
            Either represented by a percentage in the range [0.0, 1.0) or as absolute
            number of test samples in the range [1, inf). Defaults to 0.25.

    Returns:
        A tuple containing ``X_training``, ``y_training``, ``X_validation`` and
        ``y_validation`` of a dataset with two circles.
    """  # noqa: E501
    # Validate input
    n_samples = check_int(n_samples, name="n_samples", l_bound=1)
    random_seed = check_int(random_seed, name="random_seed", l_bound=0)

    X, y = datasets.make_circles(
        n_samples=n_samples, noise=0.2, factor=0.5, random_state=random_seed
    )

    # Split into training and validation data sets
    return _safe_train_test_split(X, y, test_size=test_size, random_state=random_seed)
