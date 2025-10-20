"""Module for moons dataset."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from sklearn import datasets
from tno.quantum.utils.validation import check_int

from tno.quantum.ml.datasets._utils import _safe_train_test_split


def get_moons_dataset(
    n_samples: int = 100,
    random_seed: int = 0,
    test_size: int | float | None = None,
) -> tuple[
    NDArray[np.float64], NDArray[np.int_], NDArray[np.float64], NDArray[np.int_]
]:
    r"""Generate a random dataset with a moon shape.

    This function wraps :func:`~sklearn.datasets.make_moons` of :mod:`sklearn.datasets`
    with a fixed noise factor of 0.3. Furthermore, the data is split into training and
    validation data, where 60% of the data is training and 40% is validation.

    Example usage:

        >>> from tno.quantum.ml.datasets import get_moons_dataset
        >>> X_train, y_train, X_val, y_val = get_moons_dataset()
        >>> print(f"{X_train.shape=}\n{y_train.shape=}\n{X_val.shape=}\n{y_val.shape=}")
        X_train.shape=(75, 2)
        y_train.shape=(75,)
        X_val.shape=(25, 2)
        y_val.shape=(25,)

    Args:
        n_samples: Number of samples
        random_seed: Seed to give to the random number generator. Defaults to 0.
        test_size: The proportion of the dataset that is included in the test-split.
            Either represented by a percentage in the range [0.0, 1.0) or as absolute
            number of test samples in the range [1, inf). Defaults to 0.25.

    Returns:
        A tuple containing ``X_training``, ``y_training``, ``X_validation`` and
        ``y_validation`` of a moon shaped dataset.
    """
    # Validate input
    n_samples = check_int(n_samples, name="n_samples", l_bound=1)
    random_seed = check_int(random_seed, name="random_seed", l_bound=0)

    X, y = datasets.make_moons(n_samples=n_samples, noise=0.3, random_state=random_seed)

    # Split into training and validation data sets
    return _safe_train_test_split(X, y, test_size=test_size, random_state=random_seed)
