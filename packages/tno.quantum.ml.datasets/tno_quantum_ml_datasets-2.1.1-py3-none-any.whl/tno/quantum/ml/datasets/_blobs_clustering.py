"""Module for blobs clustering dataset."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from sklearn import datasets
from tno.quantum.utils.validation import check_int


def get_blobs_clustering_dataset(
    n_samples: int, n_features: int, n_centers: int, random_seed: int = 42
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    r"""Load a blobs clustering dataset.

    This function wraps :func:`~sklearn.datasets.make_blobs` of :mod:`sklearn.datasets`
    with a fixed cluster standard deviation of 0.1.

    Example usage:

        >>> from tno.quantum.ml.datasets import get_blobs_clustering_dataset
        >>> X, true_labels = get_blobs_clustering_dataset(100, 3, 2)
        >>> print(f"{X.shape=}\n{true_labels.shape=}")
        X.shape=(100, 3)
        true_labels.shape=(100,)

    Args:
        n_samples: Number of samples.
        n_features: Number of features.
        n_centers: Number of centers.
        random_seed: Seed to give to the random number generator. Defaults to `42`.

    Returns:
        A tuple containing ``X`` and ``true_labels`` of a blobs clustering dataset.
    """
    # Validate input
    n_samples = check_int(n_samples, name="n_classes", l_bound=1)
    n_features = check_int(n_features, name="n_features", l_bound=1)
    n_centers = check_int(n_centers, name="n_centers", l_bound=1)
    random_seed = check_int(random_seed, name="random_seed", l_bound=0)

    centers = np.array(
        [[i] + [(f + i) % 2 for f in range(n_features - 1)] for i in range(n_centers)]
    )

    X, true_labels = datasets.make_blobs(
        n_samples=n_samples, centers=centers, cluster_std=0.1, random_state=random_seed
    )
    return X, true_labels
