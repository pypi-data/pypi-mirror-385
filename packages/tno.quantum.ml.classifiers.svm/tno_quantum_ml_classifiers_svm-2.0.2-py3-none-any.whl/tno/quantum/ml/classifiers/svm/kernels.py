"""Module containing kernel function used by the :py:class:`~tno.quantum.ml.classifiers.svm.SupportVectorMachine`."""  # noqa:E501

from __future__ import annotations

from collections.abc import Callable
from typing import SupportsFloat

import numpy as np
from numpy.typing import ArrayLike
from tno.quantum.utils.validation import check_real, check_string


def get_kernel(
    kernel: str | Callable[[ArrayLike, ArrayLike], float],
    gamma: SupportsFloat | None = None,
    degree: SupportsFloat | None = None,
    coef0: SupportsFloat | None = None,
) -> Callable[[ArrayLike, ArrayLike], float]:
    """Given a kernel, which can be a string or callable, returns a kernel function.

    Args:
        kernel: Name of the kernel or a callable. If a string is given, choose from
            'rbf', 'sigmoid', 'poly' or 'linear'.
        gamma: gamma parameter of the 'rbf', 'sigmoid' or 'poly' kernel.
        degree: degree of the 'poly' kernel.
        coef0: Offset in the 'sigmoid' or 'poly' kernel.

    Return:
        kernel function corresponding to the name, or the given callable.
    """
    if callable(kernel):
        return kernel

    kernel_id = check_string(kernel, "kernel", lower=True)

    if kernel_id == "rbf":
        gamma_checked = float(check_real(gamma, "gamma", l_bound=0))

        def rbf(x1: ArrayLike, x2: ArrayLike) -> float:
            return rbf_kernel(x1, x2, gamma_checked)

        return rbf

    if kernel_id == "sigmoid":
        gamma_checked = float(check_real(gamma, "gamma"))
        coef0_checked = float(check_real(coef0, "coef0"))

        def sigmoid(x1: ArrayLike, x2: ArrayLike) -> float:
            return sigmoid_kernel(x1, x2, gamma_checked, coef0_checked)

        return sigmoid

    if kernel_id == "poly":
        gamma_checked = float(check_real(gamma, "gamma"))
        degree = float(check_real(degree, "degree"))
        coef0 = float(check_real(coef0, "coef0"))

        def poly(x1: ArrayLike, x2: ArrayLike) -> float:
            return poly_kernel(x1, x2, gamma_checked, degree, coef0)

        return poly

    if kernel_id == "linear":
        return linear_kernel
    error_msg = "Unknown kernel."
    raise ValueError(error_msg)


def rbf_kernel(x1: ArrayLike, x2: ArrayLike, gamma: float) -> float:
    r"""RBF kernel for the SVM.

    Args:
        x1: The input data of one sample.
        x2: The input data of one sample.
        gamma: non-negative parameter of the rbf kernel

    Returns:
        $\exp(-\gamma\|x_1-x_2\|)$.
    """
    x1, x2 = np.asarray(x1), np.asarray(x2)
    return float(np.exp(-gamma * np.linalg.norm(x1 - x2, ord=2) ** 2))


def poly_kernel(
    x1: ArrayLike, x2: ArrayLike, gamma: float, degree: float, coef0: float
) -> float:
    r"""Polynomial kernel for the SVM.

    Args:
        x1: The input data of one sample.
        x2: The input data of one sample.
        gamma: Scaling of the of the interacting terms in the kernel.
        degree: Degree of the kernel.
        coef0: Offset of the kernel.

    Returns:
        $(\gamma\langle x_1, x_2\rangle> + c_0)^d$.
    """
    return float((gamma * np.dot(x1, x2) + coef0) ** degree)


def sigmoid_kernel(x1: ArrayLike, x2: ArrayLike, gamma: float, coef0: float) -> float:
    r"""Sigmoid kernel for the SVM.

    Args:
        x1: The input data of one sample.
        x2: The input data of one sample.
        gamma: Scaling of the of the interacting terms in the kernel
        coef0: Offset of the kernel

    Returns:
        $\tanh(\gamma\langle x_1, x_2\rangle + c_0)$.
    """
    return float(np.tanh(gamma * np.dot(x1, x2) + coef0))


def linear_kernel(x1: ArrayLike, x2: ArrayLike) -> float:
    r"""Linear kernel for the SVM.

    Args:
        x1: The input data of one sample.
        x2: The input data of one sample.

    Returns:
        $\langle x_1, x_2\rangle$.
    """
    return float(np.dot(x1, x2))
