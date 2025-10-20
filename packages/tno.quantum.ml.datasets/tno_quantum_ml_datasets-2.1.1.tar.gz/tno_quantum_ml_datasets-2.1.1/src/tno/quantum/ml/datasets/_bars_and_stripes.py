"""Module for bars and stripes dataset."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray
from tno.quantum.utils.validation import check_arraylike, check_int

from tno.quantum.ml.datasets._utils import _safe_train_test_split


def _add_noise(
    img: ArrayLike, noise_size: int, rng: np.random.Generator
) -> NDArray[np.uint8]:
    """Helper function to apply noise to pattern image(s).

    - Black pixels (0) get values in [0, noise_size]
    - White pixels (1) get values in [255 - noise_size, 255].

    Args:
        img: input pattern image(s).
        noise_size: magnitude of noise in range (0, 255)
        rng: random number generator instance for reproducibility.

    Returns:
        Noisy image(s).
    """
    arr = np.asarray(img, dtype=np.uint8)

    if noise_size == 0:
        return (arr * 255).astype(np.uint8)

    white_mask = arr == 1
    black_mask = arr == 0
    arr[white_mask] = rng.integers(255 - noise_size, 256, size=white_mask.sum())
    arr[black_mask] = rng.integers(0, noise_size + 1, size=black_mask.sum())
    return arr.astype(np.uint8)


def get_bars_and_stripes_dataset(
    n_samples: int | None = 100,
    shape: ArrayLike | None = None,
    noise_size: int = 0,
    random_seed: int = 42,
    test_size: float | int | None = None,
) -> tuple[NDArray[np.uint8], NDArray[np.int_], NDArray[np.uint8], NDArray[np.int_]]:
    r"""Create bars and stripes images dataset.

    Example usage:

        >>> from tno.quantum.ml.datasets import get_bars_and_stripes_dataset
        >>> X_train, y_train, X_val, y_val = get_bars_and_stripes_dataset(
        ...     n_samples=100, shape=(4, 4), noise_size=10,
        ... )
        >>> print(f"{X_train.shape=}\n{y_train.shape=}\n{X_val.shape=}\n{y_val.shape=}")
        X_train.shape=(75, 4, 4)
        y_train.shape=(75,)
        X_val.shape=(25, 4, 4)
        y_val.shape=(25,)

    Args:
        n_samples: Number of samples. If ``None``, generate the full Bars and Stripes
            dataset of size ``2^rows + 2^cols - 4``.
        shape: Shape of the generated images (rows, cols), defaults to (4, 4).
        noise_size: Amount of pixel noise intensity to add. By default (`noise_size=0`)
            the pixels are strictly binary with value `0` for black and value `255` for
            white pixels. For `noise_size>0`, pixel values are sampled uniformly within
            an interval around these extremes.
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
    if n_samples is not None:
        n_samples = check_int(n_samples, "n_samples", l_bound=1)
    shape = check_arraylike(shape or (4, 4), "shape", ndim=1, shape=(2,))
    n_rows, n_cols = shape
    noise_size = check_int(noise_size, "noise_size", l_bound=0, u_bound=255)

    if n_samples is None:  # Generate full dataset
        X, y = _generate_full_bars_and_stripes_patterns(n_rows, n_cols)

    else:  # Random subset sampling
        X = np.empty((n_samples, n_rows, n_cols), dtype=np.uint8)
        y = rng.integers(2, size=n_samples, dtype=np.int_)

        for i, y_i in enumerate(y):
            if y_i:  # Stripes
                size = (1, n_cols)
                reps = (n_rows, 1)
            else:  # Bars
                size = (n_rows, 1)
                reps = (1, n_cols)

            pattern = rng.integers(0, 2, size=size, dtype=np.uint8)
            while np.all(pattern == 0) or np.all(pattern == 1):  # avoid trivial
                pattern = rng.integers(0, 2, size=size, dtype=np.uint8)
            img = np.tile(pattern, reps)
            X[i] = img

    # Apply noise
    X = _add_noise(X, noise_size, rng)

    # Split into training and validation data sets
    return _safe_train_test_split(X, y, test_size=test_size, random_state=random_seed)


def _generate_full_bars_and_stripes_patterns(
    n_rows: int, n_cols: int
) -> tuple[NDArray[np.uint8], NDArray[np.int_]]:
    """Generate all patterns for the full bars and stripes dataset.

    Dataset has size ``2^rows + 2^cols - 4``.

    Args:
        n_rows: number of rows
        n_cols: number of columns

    Returns:
        Image patterns (no noise applied yet) and labels (bar/stripe)
    """
    bars = []
    for row_pattern in range(1, 2**n_rows - 1):  # exclude all 0 and all 1
        pattern = np.fromiter(np.binary_repr(row_pattern, n_rows), int, n_rows).reshape(
            n_rows, 1
        )
        bars.append(np.tile(pattern, (1, n_cols)))
    y_bars = np.zeros(len(bars), dtype=np.int_)

    stripes = []
    for col_pattern in range(1, 2**n_cols - 1):  # exclude all 0 and all 1
        pattern = np.fromiter(np.binary_repr(col_pattern, n_cols), int, n_cols).reshape(
            1, n_cols
        )
        stripes.append(np.tile(pattern, (n_rows, 1)))
    y_stripes = np.ones(len(stripes), dtype=np.int_)

    X = np.concatenate([bars, stripes], axis=0)
    y = np.concatenate([y_bars, y_stripes], axis=0)

    return X, y
