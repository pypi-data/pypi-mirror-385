"""This module contains tests for the kernels used in ``SupportVectorMachine``."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pytest
from numpy.typing import ArrayLike

from tno.quantum.ml.classifiers.svm.kernels import (
    get_kernel,
    linear_kernel,
    poly_kernel,
    rbf_kernel,
    sigmoid_kernel,
)


@pytest.mark.parametrize(
    ("kernel", "kwargs", "expected_fn"),
    [
        ("linear", {}, lambda x1, x2: linear_kernel(x1, x2)),
        ("rbf", {"gamma": 0.1}, lambda x1, x2: rbf_kernel(x1, x2, 0.1)),
        (
            "sigmoid",
            {"gamma": 1, "coef0": 0},
            lambda x1, x2: sigmoid_kernel(x1, x2, 1, 0),
        ),
        (
            "poly",
            {"gamma": 1, "degree": 2, "coef0": 1},
            lambda x1, x2: poly_kernel(x1, x2, 1, 2, 1),
        ),
    ],
)
def test_get_kernel_from_string(
    kernel: str,
    kwargs: dict[str, Any],
    expected_fn: Callable[[ArrayLike, ArrayLike], float],
) -> None:
    x1 = [1.0, 2.0]
    x2 = [3.0, 4.0]
    fn = get_kernel(kernel, **kwargs)
    assert callable(fn)
    np.testing.assert_allclose(fn(x1, x2), expected_fn(x1, x2))


def test_get_kernel_invalid_string() -> None:
    with pytest.raises(ValueError, match="Unknown kernel"):
        get_kernel("unknown_kernel")


def test_get_kernel_callable() -> None:
    def custom_linear_kernel(x1: ArrayLike, x2: ArrayLike) -> float:
        return float(np.dot(x1, x2))

    x1 = [1.0, 2.0]
    x2 = [3.0, 4.0]
    fn = get_kernel(custom_linear_kernel)
    assert callable(fn)
    np.testing.assert_allclose(fn(x1, x2), custom_linear_kernel(x1, x2))
