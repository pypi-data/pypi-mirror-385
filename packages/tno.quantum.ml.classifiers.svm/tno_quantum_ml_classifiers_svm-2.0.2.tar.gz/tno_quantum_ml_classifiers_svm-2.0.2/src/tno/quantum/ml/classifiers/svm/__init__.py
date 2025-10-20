"""This package implements a scikit-learn compatible, (quantum) support vector machine.

During the fit, the (quantum) support vector machine solves a discretized version of
the continuous optimization problem posed by a standard kernel support vector machine.
This discrete optimization problem can be solved using quantum optimization algorithms
(DWAVE, QAOA, etc.). Predictions are done classically based on the solutions found
during fit.

Example:
-----------
The following example shows how to use the
:py:class:`~tno.quantum.ml.classifiers.svm.SupportVectorMachine` class for
classification on the iris dataset.

Note:
 The example requires the following additional dependencies:

 - :py:mod:`tno.quantum.ml.datasets`: Used for the generation of artificial dataset.
 - :py:mod:`tno.quantum.optimization.qubo.solvers`: Provides the specific QUBO solvers. In this example solvers from ``[dwave]`` are used.

  Both can be installed alongside with the package by providing the ``[example]`` flag::

    pip install tno.quantum.ml.classifiers.svm[example]


Generate sample data:

>>> from tno.quantum.ml.datasets import get_iris_dataset
>>> data = get_iris_dataset(n_classes=2)
>>> X_training, y_training, X_validation, y_validation = data


Create :py:class:`~tno.quantum.ml.classifiers.svm.SupportVectorMachine` object and fit plus predict:

>>> from tno.quantum.ml.classifiers.svm import SupportVectorMachine
>>> svm = SupportVectorMachine()
>>> svm = svm.fit(X_training, y_training)
>>> predictions_validation = svm.predict(X_validation)

Plot results:

>>> import matplotlib.pyplot as plt
>>> import numpy as np
>>> fig, ax = plt.subplots()  # doctest: +SKIP
>>> unique_labels = np.unique(y_training)
>>> colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
>>> for k, col in zip(unique_labels, colors):  # doctest: +SKIP
...     mask = y_training == k
...     x, y = X_training[mask, :2].T
...     ax.plot(x, y, "o", mfc=col, mec="k", ms=6, label=f"Train class {k}")  # doctest: +SKIP
>>> ax.scatter(X_validation[:, 0], X_validation[:, 1],
...            c=predictions_validation, cmap="Spectral", marker="x", s=50, label="Predicted")  # doctest: +SKIP
>>> ax.set_title("Quantum SVM predictions")  # doctest: +SKIP
>>> ax.legend()  # doctest: +SKIP
>>> plt.savefig("example.png")  # doctest: +SKIP

.. image:: assets/example.png
    :width: 600
    :align: center
    :alt: Classification example.

"""  # noqa: E501

from tno.quantum.ml.classifiers.svm._support_vector_machine import SupportVectorMachine

__all__ = ["SupportVectorMachine"]

__version__ = "2.0.2"
