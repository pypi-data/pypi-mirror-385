"""Module for time series dataset."""

from __future__ import annotations

from math import ceil

import numpy as np
from numpy.typing import NDArray
from tno.quantum.utils.validation import check_int, check_real

from tno.quantum.ml.datasets._utils import _safe_train_test_split


def get_anomalous_spiky_time_series_dataset(  # noqa: PLR0913
    n_samples: int = 100,
    n_features: int = 4,
    n_times: int = 200,
    anomaly_proportion: float = 0.5,
    random_seed: int = 42,
    test_size: float | int | None = None,
) -> tuple[
    NDArray[np.float64], NDArray[np.int_], NDArray[np.float64], NDArray[np.int_]
]:
    r"""Create a time series dataset.

    This uses normally distributed spikes centered around zero.

    This function generates non-anomalous time series' with spikes for each feature
    which come from distributions with random standard deviations between `0` and `0.5`.

    Anomalous time series' have alternating intervals of small spikes and large spikes.
    These intervals are of length `10` time units. The small spikes for each feature
    come from distributions with random standard deviations between `0` and `0.3` and
    the large spikes for each features come from distributions with random standard
    deviations between `0.8` and `1.6`. There is an `80%` chance of a small spike and a
    `20%` chance of a large spike at each time for each feature.

    Example usage:

        >>> from tno.quantum.ml.datasets import get_anomalous_spiky_time_series_dataset
        >>> X_train, y_train, X_val, y_val = get_anomalous_spiky_time_series_dataset(
        ...     n_samples=100, n_features=2, n_times=100, anomaly_proportion=0.5
        ... )
        >>> print(f"{X_train.shape=}\n{y_train.shape=}\n{X_val.shape=}\n{y_val.shape=}")
        X_train.shape=(75, 2, 100)
        y_train.shape=(75,)
        X_val.shape=(25, 2, 100)
        y_val.shape=(25,)

    Args:
        n_samples: Number of samples
        n_features: Number of features
        n_times: Number of evenly spaced times.
        anomaly_proportion: Percentage of the dataset that contains anomalies.
        random_seed: Seed to give to the random number generator. Defaults to `42`.
        test_size: The proportion of the dataset that is included in the test-split.
            Either represented by a percentage in the range [0.0, 1.0) or as absolute
            number of test samples in the range [1, inf). Defaults to 0.25.

    Returns:
        A tuple containing ``X_training``, ``y_training``, `X_validation`` and
        ``y_validation``.
    """
    rng = np.random.default_rng(random_seed)

    # Validate input
    n_samples = check_int(n_samples, "n_samples", l_bound=1)
    n_features = check_int(n_features, "n_features", l_bound=1)
    n_times = check_int(n_times, "n_times", l_bound=1)
    anomaly_proportion = check_real(
        anomaly_proportion, "anomaly_proportion", l_bound=0, u_bound=1
    )

    # Generate non-anomalous time series.

    n_samples_anomalous = int(anomaly_proportion * n_samples)
    n_samples_non_anomalous = n_samples - n_samples_anomalous

    # Define noise levels
    noise_levels_non_anomalous = rng.uniform(low=0, high=0.5, size=n_features)
    low_noise_levels = rng.uniform(low=0, high=0.3, size=n_features)
    high_noise_levels = rng.uniform(low=0.8, high=1.6, size=n_features)

    # Generate non-anomalous time series
    X_non_anomalous = np.zeros(shape=(n_samples_non_anomalous, n_features, n_times))
    y_non_anomalous = np.zeros(shape=(n_samples_non_anomalous), dtype=np.int_)

    for feature, noise_level in enumerate(noise_levels_non_anomalous):
        X_non_anomalous[:, feature, :] = rng.normal(
            0, noise_level, (n_samples_non_anomalous, n_times)
        )

    # Generate anomalous time series.
    X_anomalous = np.zeros(shape=(n_samples_anomalous, n_features, n_times))
    y_anomalous = np.ones(shape=(n_samples_anomalous), dtype=np.int_)
    probability_large_spike = 0.2

    spike_types = rng.binomial(n=1, p=probability_large_spike, size=ceil(n_times / 10))
    for sample in range(n_samples_anomalous):
        for feature in range(n_features):
            low_noise_level = low_noise_levels[feature]
            high_noise_level = high_noise_levels[feature]

            X_anomalous[sample, feature, :] = np.array(
                [
                    rng.normal(
                        0,
                        high_noise_level if spike_type else low_noise_level,
                        size=10,
                    )
                    for spike_type in spike_types
                ]
            ).flatten()[:n_times]

    X = np.concatenate((X_non_anomalous, X_anomalous), axis=0)
    y = np.concatenate((y_non_anomalous, y_anomalous), axis=0)

    # Split into training and validation data sets
    return _safe_train_test_split(X, y, test_size=test_size, random_state=random_seed)
