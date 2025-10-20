"""This module contains tests for the ``SupportVectorMachine``."""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

import numpy as np
import pytest
from numpy.testing import assert_array_equal
from numpy.typing import NDArray
from sklearn.utils.estimator_checks import check_estimator
from tno.quantum.ml.components import check_estimator_serializable
from tno.quantum.ml.datasets import (
    get_circles_dataset,
    get_iris_dataset,
    get_linearly_separable_dataset,
    get_moons_dataset,
)
from tno.quantum.optimization.qubo.components import QUBO
from tno.quantum.utils.serialization import Serializable

from tno.quantum.ml.classifiers.svm import SupportVectorMachine
from tno.quantum.ml.classifiers.svm._support_vector_machine import (
    ComparableLabelEncoder,
)

# --- Sklearn compliance tests ------------------------------------------------


def test_sklearn_compliance() -> None:
    svm = SupportVectorMachine(
        solver_config={
            "name": "simulated_annealing_solver",
            "options": {"random_state": 42},
        }
    )
    check_estimator(svm)


# --- Basic functionality tests -----------------------------------------------


def test_initialization() -> None:
    """Test the initialization of the SupportVectorMachine."""
    svm1 = SupportVectorMachine()

    assert svm1.K == 2
    assert svm1.C == 1.0
    assert svm1.xi == "auto"
    assert svm1.kernel == "rbf"
    assert svm1.gamma == "scale"
    assert svm1.degree == 3
    assert svm1.coef0 == 0
    assert svm1.solver_config is None

    svm2 = SupportVectorMachine(
        K=3,
        C=0.5,
        xi=0.1,
        kernel="linear",
        gamma=0.01,
        degree=2,
        coef0=1.0,
        solver_config={"name": "simulated_annealing_solver", "random_state": 42},
    )
    assert svm2.K == 3
    assert svm2.C == 0.5  # noqa: PLR2004
    assert svm2.xi == 0.1  # noqa: PLR2004
    assert svm2.kernel == "linear"
    assert svm2.gamma == 0.01  # noqa: PLR2004
    assert svm2.degree == 2
    assert svm2.coef0 == 1.0
    assert svm2.solver_config == {
        "name": "simulated_annealing_solver",
        "random_state": 42,
    }


def test_svm_basic_fit_predict() -> None:
    svm = SupportVectorMachine()
    X_train, y_train, X_val, _ = get_iris_dataset(n_classes=2)
    svm.fit(X_train[:50], y_train[:50])
    y_pred = svm.predict(X_val)

    # Check that the predictions are of the correct shape and type
    assert y_pred.shape[0] == X_val.shape[0]
    assert set(np.unique(y_pred)).issubset(set(np.unique(y_train)))


def test_many_classes_exception() -> None:
    svm = SupportVectorMachine()
    X_train, y_train, _, _ = get_iris_dataset(n_classes=3)

    expected_message = (
        "Only binary classification is supported. The type of the target is multiclass."
    )
    with pytest.raises(ValueError, match=expected_message):
        svm.fit(X_train, y_train)


def test_make_qubo_y_is_none() -> None:
    svm = SupportVectorMachine()
    X = np.array([[1.0, 1.0], [1.0, 1.0]])

    with pytest.raises(ValueError, match="y must be provided for making the QUBO"):
        svm._make_qubo(X)


def test_qubo_size() -> None:
    """Test size of the QUBO matrix."""
    svm = SupportVectorMachine()
    X = [[1.0, 1.0], [1.0, 1.0]]
    y = [1, 0]
    svm.fit(X, y)
    qubo = svm.qubo_
    assert isinstance(qubo, QUBO)
    expected_size = svm.K * len(X)
    assert qubo.size == expected_size


@pytest.mark.parametrize(
    ("y", "expected_spin_labels"),
    [
        ([1, 0, 0], [1, -1, -1]),
        ([0, 1, 0], [-1, 1, -1]),
        ([0, 0, 1], [-1, -1, 1]),
        ([5, 2, 2], [1, -1, -1]),
        ([0, 3, 3], [-1, 1, 1]),
        ([-2, -1, -1], [-1, 1, 1]),
        ([0, 0, 0], [-1, -1, -1]),
    ],
)
def test_spin_labels(y: list[int], expected_spin_labels: list[int]) -> None:
    """Test that the spin labels are correctly set in the QUBO."""
    svm = SupportVectorMachine()
    X = [[1.0, 1.0], [-1.0, 1.0], [1.0, 2.0]]
    svm.fit(X, y)
    np.testing.assert_array_equal(svm.y_spin_, expected_spin_labels)
    np.testing.assert_array_equal(svm.y_, y)


def test_predictions() -> None:
    """Test that the predictions are correct."""
    svm = SupportVectorMachine()
    X = [[1.0, 1.0], [-1.0, 1.0], [1.0, 2.0]]
    y = [1, -1, 1]
    svm.fit(X, y)
    predictions = svm.predict(X)
    np.testing.assert_array_equal(predictions, y)


def test_predict_proba() -> None:
    """Test that the predict_proba method returns probabilities."""
    svm = SupportVectorMachine()
    X = [[1.0, 1.0], [-1.0, 1.0], [1.0, 2.0]]
    y = [1, -1, 1]
    svm.fit(X, y)
    probabilities = svm.predict_proba(X)

    # Check shape: (n_samples, n_classes)
    assert probabilities.shape == (len(X), 2)


# --- Gamma logic and xi tests -----------------------------------------------


@pytest.mark.parametrize(
    ("svm", "expected_gamma"),
    [
        (SupportVectorMachine(gamma="scale"), 1 / 12),
        (SupportVectorMachine(gamma="auto"), 1 / 3),
        (SupportVectorMachine(gamma=10.0), 10.0),
        (SupportVectorMachine(kernel="linear"), None),
        (SupportVectorMachine(kernel=lambda x1, x2: x1.sum() + x2.sum()), None),  # type: ignore
    ],
)
def test_gamma_logic(svm: SupportVectorMachine, expected_gamma: str | float) -> None:
    X = np.array([[2, -2, 2], [-2, 2, -2]])
    y = np.array([1, -1])
    svm.fit(X, y)
    assert svm._check_and_calc_gamma() == expected_gamma


@pytest.mark.parametrize(
    ("xi", "expected"),
    [
        (1.5, 1.5),
        ("auto", 2.5 * 3),  # Assuming K=3
    ],
)
def test_check_and_calc_xi_valid(xi: str | float, expected: float) -> None:
    svm = SupportVectorMachine(xi=xi, K=3)
    assert svm._check_and_calc_xi() == expected


@pytest.mark.parametrize(
    ("xi", "expected_message"),
    [
        (-1.0, "'xi' has an inclusive lower bound of 0.0, but was -1.0."),
        ("invalid", "xi should be a positive real number or 'auto'"),
    ],
)
def test_check_and_calc_xi_invalid(xi: str | float, expected_message: str) -> None:
    svm = SupportVectorMachine(xi=xi, K=3)
    with pytest.raises(ValueError, match=expected_message):
        svm._check_and_calc_xi()


# --- Estimator equality tests -----------------------------------------------


def test_equality() -> None:
    """Test equality of SVMs."""
    estimator_1 = SupportVectorMachine()
    estimator_2 = SupportVectorMachine()
    X = np.array([[2, -2, 2], [-2, 2, -2]])
    y = np.array([1, -1])
    assert estimator_1 == estimator_2
    estimator_1.fit(X, y)
    assert estimator_1 != estimator_2
    estimator_2.fit(X, y)
    assert estimator_1 == estimator_2


# --- Serialization tests -----------------------------------------------------


def test_serialization() -> None:
    """Test correct serialization of estimator."""
    estimator1 = SupportVectorMachine()
    check_estimator_serializable(estimator1)
    estimator2 = SupportVectorMachine()
    X = np.array([[2, -2, 2], [-2, 2, -2]])
    y = np.array([1, -1])
    estimator2.fit(X, y)
    check_estimator_serializable(estimator2)


def test_serialization_comparable_label_encoder() -> None:
    """Test (de)serialization of comparable label encoder."""
    le = ComparableLabelEncoder()
    le.fit([1, 3, 2, 3, "cat"])

    serialized_value = Serializable.serialize(le)
    deserialized_value = Serializable.deserialize(serialized_value)
    assert_array_equal(le.classes_, deserialized_value.classes_)

    transform_value = [3, 3, "cat", 1, 1, "cat", 2]

    assert_array_equal(
        deserialized_value.transform(transform_value), le.transform(transform_value)
    )


# --- Accuracy tests -----------------------------------------------------


def _calc_accuracy(prediction: NDArray[Any], actual: NDArray[Any]) -> float:
    """Calculate the accuracy of predictions against actual values."""
    if len(prediction) != len(actual):
        error_message = "len(prediction) != len(actual)"
        raise ValueError(error_message)
    return float(sum(prediction == actual) / len(actual))


@pytest.mark.parametrize(
    ("kernel", "dataset_maker", "min_accuracy"),
    [
        (
            "linear",
            functools.partial(
                get_linearly_separable_dataset, n_samples=13, test_size=0, random_seed=0
            ),
            1.0,
        ),
        (
            "poly",
            functools.partial(
                get_circles_dataset, n_samples=13, test_size=0, random_seed=3
            ),
            0.8,
        ),
        (
            "sigmoid",
            functools.partial(
                get_moons_dataset, n_samples=13, test_size=0, random_seed=1
            ),
            0.75,
        ),
        (
            "rbf",
            functools.partial(
                get_moons_dataset, n_samples=13, test_size=0, random_seed=3
            ),
            0.8,
        ),
        (
            "linear",
            functools.partial(
                get_iris_dataset, n_classes=2, test_size=0.87, random_seed=0
            ),
            0.9,
        ),
    ],
)
def test_svm_accuracy(
    kernel: str,
    dataset_maker: Callable[
        [],
        tuple[
            NDArray[np.float64], NDArray[np.int_], NDArray[np.float64], NDArray[np.int_]
        ],
    ],
    min_accuracy: float,
) -> None:
    X_train, y_train, _, _ = dataset_maker()

    # Max number tree decomposition solver can handle.
    assert len(X_train) == 13

    kernel_params: dict[str, Any] = {}
    if kernel == "poly":
        kernel_params = {"degree": 2, "gamma": 5.0}
    if kernel == "sigmoid":
        kernel_params = {"gamma": 0.5, "coef0": -1.0}
    if kernel == "rbf":
        kernel_params = {"gamma": 3.0}
    svm = SupportVectorMachine(
        kernel=kernel,
        solver_config={"name": "tree_decomposition_solver"},
        **kernel_params,
    )

    svm.fit(X_train, y_train)
    # Predict on the training set to check whether the SVM learned.
    y_pred = svm.predict(X_train)
    accuracy = _calc_accuracy(y_pred, y_train)
    assert accuracy >= min_accuracy
