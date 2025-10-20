"""This module implements a scikit-learn compatible, quantum support vector machine."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

import numpy as np
from numpy.typing import ArrayLike, NDArray
from sklearn.base import ClassifierMixin, ClassifierTags, Tags
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.multiclass import type_of_target, unique_labels
from sklearn.utils.validation import check_is_fitted, check_X_y, validate_data
from tno.quantum.ml.components import QUBOEstimator, get_default_solver_config_if_none
from tno.quantum.optimization.qubo.components import QUBO, SolverConfig
from tno.quantum.utils.serialization import Serializable
from tno.quantum.utils.validation import check_int, check_real, check_string

from tno.quantum.ml.classifiers.svm.kernels import get_kernel

if TYPE_CHECKING:
    from typing import Self

    from tno.quantum.utils import BitVector


class ComparableLabelEncoder(LabelEncoder):  # type: ignore[misc]
    """LabelEncoder that can be compared to another LabelEncoder."""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LabelEncoder):
            return False
        return np.array_equal(self.classes_, other.classes_)

    def __hash__(self) -> int:
        error_msg = "unhashable type: 'ComparableLabelEncoder'"
        raise NotImplementedError(error_msg)


class SupportVectorMachine(ClassifierMixin, QUBOEstimator):  # type: ignore[misc]
    """Support vector machine."""

    def __init__(  # noqa: PLR0913
        self,
        *,
        K: int = 2,  # noqa: N803
        C: float = 1.0,  # noqa: N803
        xi: str | float = "auto",
        kernel: str | Callable[[ArrayLike, ArrayLike], float] = "rbf",
        gamma: str | float = "scale",
        degree: int = 3,
        coef0: float = 0,
        solver_config: SolverConfig | Mapping[str, Any] | None = None,
    ) -> None:
        r"""Init of the SupportVectorMachine.

        The SupportVectorMachine minimizes the following objective function:

        .. _QUBO cost function:
        .. math::

            \frac{C}{2^K-1}\sum_{n,m,k,j}a_{n,k}a_{m,j}2^{k+j-1}y_ny_mk(x_n,x_m)
            -\sum_{n,k}a_{n,k}2^k
            + \xi \frac{C}{2^K-1}\left(\sum_{n,k}2^ka_{n,k}y_n\right)^2.

        **Details:**

        * $a_{n,k}$ are the binary decision variables.
        * $x_{n}$ is the $n^{th}$ feature vector, i.e., the $n^{th}$ row of the feature matrix $X$.
        * $y_n$ is the $n^{th}$ target value. The classes of the input vector `y` are converted such that $y_n\in\{-1,1\}$.
        * $k(\cdot,\cdot)$ is the kernel function.

        Args:
            K: Number of variables used in the variable encoding. The total number of
                variables the objective function of the SVM is ``n_samples * K``. K must
                be a strictly positive integer. Defaults to 2.
            C: Upper limit of the variables. C must be a strictly positive real number.
                Default is 1.
            xi: Penalty parameter to enforce the constraint $\sum_i y_i\alpha_i = 0$.
                `xi` is relative to the largest absolute term of the unconstrained
                problem. `xi` must be a positive real number or ``'auto'``. If
                ``'auto'`` is used, `xi` is set to 2.5K. Default is ``'auto'``.
            kernel: Kernel to use, choose from ``{'rbf', 'linear', 'poly', 'sigmoid'}``
                or custom callable.  Default is ``'rbf'``. For more information on the
                kernels see the documentation of
                :py:mod:`~tno.quantum.ml.classifiers.svm.kernels`.
            gamma: Kernel parameter of the ``'rbf'``, ``'poly'`` and ``'sigmoid'``
                kernels. If ``'scaled'`` is given, then
                ``gamma=1 / n_features_in * X_train.var()``. If ``'auto'`` is given,
                then ``gamma=1 / n_features_in``. If a real number is given then this
                float will be used for gamma. Default is ``'scaled'``. For more
                information see the documentation of
                :py:mod:`~tno.quantum.ml.classifiers.svm.kernels`.
            degree: Degree of the ``'poly'`` kernel. Default is 3. For more information,
                see the documentation of :py:func:`~tno.quantum.ml.classifiers.svm.kernels.poly_kernel`.
            coef0: Offset in the 'sigmoid' or ``'poly'`` kernel. Default is 0. For more
                information see the documentation of
                :py:func:`~tno.quantum.ml.classifiers.svm.kernels.sigmoid_kernel` or
                :py:func:`~tno.quantum.ml.classifiers.svm.kernels.poly_kernel`.
            solver_config: A QUBO solver configuration or None. In the former case
                includes name and options. If ``None`` is given, the default solver
                configuration as defined in
                :py:func:`~tno.quantum.ml.components.get_default_solver_config_if_none`
                will be used. Default is ``None``.

        Attributes:
            gamma_: kernel parameter of the ``'rbf'``, ``'poly'`` and ``'sigmoid'``
                kernels.
            y_spin_: Spin-encoded labels.
            alphas_: Coefficients of the SVM.
            bias_: Bias of the SVM.
            label_encoder_: Label encoder for the classes.
            classes_: Classes of the SVM.
        """  # noqa: E501
        self.K = K
        self.C = C
        self.xi = xi
        self.kernel = kernel
        self.gamma = gamma
        self.degree = degree
        self.coef0 = coef0
        super().__init__(solver_config=solver_config)
        self.gamma_: None | float
        self.y_spin_: NDArray[np.int8]
        self.alphas_: NDArray[np.float64]
        self.bias_: float
        self.label_encoder_: ComparableLabelEncoder
        self.classes_: NDArray[np.int_]

    def _validate_params(self) -> None:
        """Validate the parameters of the SVM.

        Raises:
            ValueError: If the SVM parameters are not valid.
        """
        check_int(self.K, "K", l_bound=1)
        check_real(self.C, "C", l_bound=0, l_inclusive=False)
        check_int(self.degree, "degree")
        check_real(self.coef0, "coef0")

    def _make_qubo(
        self, X: NDArray[np.float64], y: NDArray[np.float64] | None = None
    ) -> QUBO:
        """Make a SVM QUBO in the QUBO format of the optimization pipeline.

        Args:
            X: The input data.
            y: The target values. The array must contain values of (-1,1).

        Returns:
            qubo: QUBO of the SVM
        """
        if y is None:
            error_msg = "y must be provided for making the QUBO."
            raise ValueError(error_msg)
        # Calculate gamma
        self.gamma_ = self._check_and_calc_gamma()

        kernel = get_kernel(
            self.kernel, gamma=self.gamma_, degree=self.degree, coef0=self.coef0
        )
        n_variables = X.shape[0] * self.K
        scalar = self.C / (2**self.K - 1)

        qubo_base = np.zeros((n_variables, n_variables))

        for a_nk in range(n_variables):
            n, k = divmod(a_nk, self.K)
            qubo_base[a_nk, a_nk] -= 2**k
            qubo_base[a_nk, a_nk] += scalar * 2 ** (2 * k - 1) * kernel(X[n], X[n])

            for a_mj in range(a_nk + 1, n_variables):
                m, j = divmod(a_mj, self.K)
                qubo_base[a_nk, a_mj] += (
                    scalar * 2 ** (k + j) * y[n] * y[m] * kernel(X[n], X[m])
                )

        qubo_constraint = np.zeros((n_variables, n_variables))
        for a_nk in range(n_variables):
            n, k = divmod(a_nk, self.K)
            qubo_constraint[(a_nk, a_nk)] += (2 ** (2 * k - 1)) * scalar

            for a_mj in range(a_nk + 1, n_variables):
                m, j = divmod(a_mj, self.K)
                qubo_constraint[(a_nk, a_mj)] += scalar * ((2 ** (k + j)) * y[n] * y[m])

        penalty = max(-qubo_base.min(), qubo_base.max()) * self._check_and_calc_xi()

        return QUBO(qubo_base + penalty * qubo_constraint)

    def fit(self, X: ArrayLike, y: ArrayLike | None = None) -> Self:
        """Fit the model to data matrix X and targets y.

        The model is fitted by minimizing the `QUBO cost function`_ shown in the
        ``__init__``.

        Args:
            X: The input data. Should be a 2 dimensional real valued ArrayLike
                containing the features. Must be the same length as `y`.
            y: The target values. There must be exactly 2 classes (unique values). Must
                be the same length as `X`.

        Returns:
            Self, a trained classifier.
        """
        if y is None:
            error_msg = "requires y to be passed, but the target y is None"
            raise ValueError(error_msg)
        self._validate_params()
        # Fitting is done on spin labels.
        self.y_spin_ = self._compute_spin_labels(y)
        svm = cast("SupportVectorMachine", super().fit(X, y=self.y_spin_))
        # Overwrite y_ with the original y.
        self.y_ = np.asarray(y)
        return svm

    def predict(self, X: ArrayLike) -> NDArray[Any]:
        """Predict the class labels for the provided data.

        Predictions are theoretically based on
        :py:func:`~svm.SupportVectorMachine.predict_proba`, but this method uses a more
        efficient implementation based on the sign of the decision function.

        Args:
            X: Test samples.

        Returns:
            Array containing the predicted class labels.
        """
        # Check is fit has been called
        check_is_fitted(self)

        # Input validation
        X = np.asarray(validate_data(self, X=X, reset=False))
        y_pred_spin = np.sign(np.array([self._predict_svm(x) for x in X]))
        y_pred_binary = ((y_pred_spin + 1) / 2).astype(np.int8)
        y_pred = self.label_encoder_.inverse_transform(y_pred_binary)

        return np.asarray(y_pred)

    def predict_proba(self, X: ArrayLike) -> NDArray[np.float64]:
        r"""Return probability-like estimates for the test data X.

        .. warning::
            The values returned by this method are **not true calibrated probability**.
            If true probabilistic interpretation is needed, consider applying a post-hoc
            calibration method such as Platt scaling.

        The predictions are based on the following formula:

        .. _prediction probability function:
        .. math::

            \begin{align}
            p(x) &= \frac{1-b}{2}
            - \frac{1}{2}\sum_n \sum_k a_{nk}y_n^\text{train}k(x_n^\text{train}, x)\\
            \text{, where}\\
            b &= \frac{
            \sum_n\left(\sum_k2^ka_{nk}\right)
            \left(1-\frac{\sum_k2^ka_{nk}}{2^K-1}\right)
            \left(y^\text{train}_n-\frac{C}{2^K-1}\sum_m\sum_ka_{m,k}y^\text{train}_mk
            (x^\text{train}_n,x^\text{train}_m)\right)
            }{
            \sum_n\left(\sum_k2^ka_{nk}\right)
            \left(1-\frac{\sum_k2^ka_{nk}}{2^K-1}\right)
            }
            \end{align}

        **Details:**

        * $a_{n,k}$ are the binary solutions of the fitted QUBO.
        * $x_{n}^\text{train}$ is the $n^{th}$ feature vector of the training data.
        * $y_n^\text{train}$ is the $n^{th}$ target value of the training data. The classes of the input vector `y` are converted such that $y_n^\text{train}\in\{-1,1\}$.
        * $k(\cdot,\cdot)$ is the kernel function.

        Args:
            X: Test samples.

        Returns:
            The class probabilities of the input samples. Classes are ordered by
            lexicographic order.
        """  # noqa: E501
        # Check is fit had been called
        check_is_fitted(self)

        # Input validation
        X = np.asarray(validate_data(self, X=X, reset=False))

        proba_array = np.zeros([X.shape[0], 2])
        for i, x in enumerate(X):
            proba_array[i, 0] = 0.5 - 0.5 * self._predict_svm(x)
        proba_array[:, 1] = 1 - proba_array[:, 0]

        return proba_array

    def _check_X_and_y(
        self, X: NDArray[np.float64], y: NDArray[np.float64] | None = None
    ) -> None:
        """Check if `X` and `y` are valid and compatible with binary classification.

        Args:
            X: Feature matrix.
            y: The target values

        Raises:
            ValueError: If `X` and `y` are not compatible.
            ValueError: If `y` has more than 2 classes.
        """
        # Check that X and y have correct shape
        check_X_y(X, y)

        # Check that we have exactly 2 classes
        y_type = type_of_target(y, input_name="y", raise_unknown=True)
        if y_type != "binary":
            error_msg = (
                "Only binary classification is supported. The type of the target "
                f"is {y_type}."
            )
            raise ValueError(error_msg)

    def _compute_spin_labels(self, y: ArrayLike) -> NDArray[np.int8]:
        """Compute spin labels {-1, +1} from class labels.

        Args:
            y: Original target labels.

        Returns:
            Spin-encoded labels.
        """
        label_encoder = ComparableLabelEncoder()
        self.classes_ = unique_labels(y)
        label_encoder.fit(self.classes_)
        y_binary = label_encoder.transform(y)

        # Store encoder
        self.label_encoder_ = label_encoder
        return np.asarray(y_binary * 2 - 1, dtype=np.int8)

    def _check_and_calc_gamma(self) -> None | float:
        """Compute gamma if needed.

        Returns:
            gamma: kernel parameter of the 'rbf', 'sigmoid' and 'poly' kernels.
        """
        if callable(self.kernel):
            return None
        kernel_id = check_string(self.kernel, "kernel", lower=True)
        if kernel_id not in ["rbf", "sigmoid", "poly"]:
            return None

        try:
            return float(check_real(self.gamma, "gamma"))
        except TypeError:
            gamma_id = check_string(self.gamma, "gamma", lower=True)
        num_features = int(self.n_features_in_)
        if gamma_id == "scale":
            return float(1 / (num_features * self.X_.var()))
        if gamma_id == "auto":
            return 1 / num_features
        error_msg = (
            f"gamma should be a real number, 'scale' or 'auto', but was  {self.gamma}"
        )
        raise ValueError(error_msg)

    def _check_and_calc_xi(self) -> float:
        """Compute xi.

        Returns:
            xi: penalty parameter for enforcing the constraint.
        """
        try:
            return float(check_real(self.xi, "xi", l_bound=0))
        except TypeError:
            xi_id = check_string(self.xi, "xi", lower=True)

        if xi_id == "auto":
            return 2.5 * self.K
        error_msg = f"xi should be a positive real number or 'auto', but was {self.xi}"
        raise ValueError(error_msg)

    def _predict_svm(self, x: ArrayLike) -> float:
        """Return the prediction of the test data x.

        Args:
            x: a single test sample.

        Returns:
            decision value: real-valued SVM decision function output.
        """
        kernel = get_kernel(
            self.kernel, gamma=self.gamma_, degree=self.degree, coef0=self.coef0
        )
        f = self.bias_
        for n, alpha in enumerate(self.alphas_):
            f += alpha * self.y_spin_[n] * kernel(self.X_[n], x)
        return f

    def _check_constraints(self, bit_vector: BitVector) -> bool:
        """Check if the found bit vector satisfies the imposed constraints.

        Args:
            bit_vector: Bitvector containing the solution to the QUBO.

        Returns:
            True if there are no violations, False otherwise.
        """
        constraint_value = 0
        for i, indicator in enumerate(bit_vector.bits):
            if indicator:
                n, k = divmod(i, self.K)
                constraint_value += 2**k * self.y_spin_[n]

        if not constraint_value:
            return True

        warnings.warn("Constraints were violated.", stacklevel=2)

        return False

    def _decode_bit_vector(self, bit_vector: BitVector) -> Self:
        """Decode bit vector and set attributes.

        More specifically, decode the bit vector to the decoded alpha
        (real valued) coefficients of the SVM.

        Args:
            bit_vector : A bit vector containing the solution to the QUBO.

        Attributes:
            alphas: decoded alpha coefficients of the SVM.
            bias_: decoded bias coefficient of the SVM.
        """
        int_alphas = np.zeros(self.X_.shape[0])

        for n in range(self.X_.shape[0]):
            for k in range(self.K):
                int_alphas[n] += (2**k) * bit_vector.bits[self.K * n + k]

        scaling = float(self.C / (2**self.K - 1))
        self.alphas_ = scaling * int_alphas
        self.bias_ = self._calc_bias()

        return self

    def _calc_bias(self) -> float:
        """Calculate the bias of the SVM.

        Returns:
            bias: bias of the SVM.
        """
        X = self.X_
        y = self.y_spin_
        alphas = self.alphas_
        kernel = get_kernel(
            self.kernel, gamma=self.gamma_, degree=self.degree, coef0=self.coef0
        )
        bias = 0
        for n, alpha_n in enumerate(alphas):
            sample_bias = y[n]
            for m, alpha_m in enumerate(alphas):
                sample_bias -= alpha_m * y[m] * kernel(X[m], X[n])
            sample_bias *= alpha_n * (self.C - alpha_n)
            bias += sample_bias

        if bias == 0:
            return float(bias)

        normalising_constant = sum(alpha * (self.C - alpha) for alpha in self.alphas_)

        return float(bias / normalising_constant)

    def __sklearn_tags__(self) -> Tags:
        """Return estimator tags."""
        tags = super().__sklearn_tags__()

        # Dynamic tag based on solver
        solver_config = get_default_solver_config_if_none(self.solver_config)
        solver = solver_config.get_instance()
        tags.non_deterministic = solver.non_deterministic

        # Static tag
        tags.estimator_type = "classifier"
        tags.classifier_tags = ClassifierTags(multi_class=False)

        return tags


# Register `ComparableLabelEncoder` as serializable
def _serialize_comparable_label_encoder(
    value: ComparableLabelEncoder,
) -> dict[str, list[Any]]:
    return {"classes_": value.classes_.tolist()}


def _deserialize_comparable_label_encoder(
    data: dict[str, list[Any]],
) -> ComparableLabelEncoder:
    label_encoder = ComparableLabelEncoder()
    label_encoder.classes_ = np.array(data["classes_"])
    return label_encoder


Serializable.register(
    ComparableLabelEncoder,
    _serialize_comparable_label_encoder,
    _deserialize_comparable_label_encoder,
)
