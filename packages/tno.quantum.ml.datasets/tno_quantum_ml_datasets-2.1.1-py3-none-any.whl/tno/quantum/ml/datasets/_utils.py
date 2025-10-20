"""Some basic utility functions for datasets."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from matplotlib import pyplot as plt
from numpy.typing import ArrayLike, NDArray
from sklearn.model_selection import train_test_split
from tno.quantum.utils.validation import check_arraylike, check_int, check_path

if TYPE_CHECKING:
    from pathlib import Path


def _pre_process_data(
    X: NDArray[Any], y: NDArray[Any], n_features: int, n_classes: int
) -> tuple[NDArray[Any], NDArray[Any]]:
    """Slice `X` and `y` and cast the dtype of `y` to the dtype of `X`.

    Args:
        X: Feature matrix to slice.
        y: Target samples to slice and cast.
        n_features: Number of features.
        n_classes: Number of classes

    Returns:
        ``Tuple`` of `X` and `y`, where `X`, and `y` are sliced to have the correct
        number of classes and number of features. Furthermore, the datatype of `y` is
        set to the datatype of `X`.
    """
    # Validate input
    n_features = check_int(n_features, name="n_features", l_bound=1)
    n_classes = check_int(n_classes, name="n_classes", l_bound=1)

    y = y.astype(X.dtype)
    ind = y < n_classes
    X = X[ind, :n_features]
    y = y[ind]
    return X, y


def _safe_train_test_split(
    X: ArrayLike,
    y: ArrayLike,
    test_size: int | float | None = 0.25,
    random_state: int | np.random.RandomState | None = None,
) -> tuple[NDArray[Any], NDArray[Any], NDArray[Any], NDArray[Any]]:
    """Wrapper around sklearn's `train_test_split` that allows `test_size=0`.

    If test_size == 0, returns all of (X, y) as training data and empty arrays for
    the validation data.

    Args:
        X: Dataset samples.
        y: Dataset labels.
        test_size: Size of the test dataset.
        random_state: random state for reproducibility.

    Returns:
        A tuple containing ``X_training``, ``y_training``, ``X_validation`` and
        ``y_validation`` of the dataset.
    """
    X = np.asarray(X)
    y = np.asarray(y)

    if test_size == 0:
        return (
            X,
            y,
            np.empty((0, *X.shape[1:]), dtype=X.dtype),
            np.empty((0, *y.shape[1:]), dtype=y.dtype),
        )

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    return X_train, y_train, X_val, y_val


def show_images_dataset(
    images: ArrayLike,
    labels: ArrayLike | None = None,
    save_path: None | Path = None,
    max_per_row: int = 4,
    *,
    show: bool = True,
) -> None:
    r"""Displays a grayscale image with a grid and pixel values.

    Example usage:

    >>> from tno.quantum.ml.datasets import get_bars_and_stripes_dataset, show_images_dataset
    >>> X, y, _, _ = get_bars_and_stripes_dataset(6, (8, 8), noise_size=30, test_size=0)
    >>> show_images_dataset(X, y, max_per_row=3)  # doctest: +SKIP

    Args:
        images: Greyscale images to plot
        labels: Corresponding labels of each image.
        save_path: if provided, the path where figure is saved to.
        max_per_row: Maximum number of images in a single row.
        show: whether to call plt.show() at the end.

    Raises:
        ValueError: If labels is provided but has not same length as images.
    """  # noqa: E501
    images = check_arraylike(images, "images", ndim=3)
    labels = check_arraylike(labels, "labels", ndim=1)
    max_per_row = check_int(max_per_row, "max_per_row", l_bound=1)
    number_of_images = len(images)

    if labels is not None and len(labels) != number_of_images:
        error_msg = (
            f"labels length {len(labels)} does not match "
            f"number of images {number_of_images}."
        )
        raise ValueError(error_msg)

    # Compute rows and columns
    ncols = min(number_of_images, max_per_row)
    nrows = number_of_images // max_per_row
    if number_of_images % max_per_row:
        nrows += 1

    _, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 5 * nrows), squeeze=False)
    axes = axes.ravel()
    for idx, (ax, img) in enumerate(zip(axes, images, strict=False)):
        rows, cols = img.shape
        ax.imshow(img, cmap="gray", vmin=0, vmax=255)

        # Draw grid
        ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
        ax.grid(which="minor", color="red", linestyle="-", linewidth=0.5)

        # Remove ticks
        ax.tick_params(
            which="both", bottom=False, left=False, labelbottom=False, labelleft=False
        )

        # Add label as title
        if labels is not None:
            ax.set_title(f"label={labels[idx]}")

    for ax in axes[number_of_images:]:
        ax.axis("off")

    if save_path is not None:
        save_path = check_path(save_path, "save_path")
        plt.savefig(save_path, bbox_inches="tight")

    if show:
        plt.show()
