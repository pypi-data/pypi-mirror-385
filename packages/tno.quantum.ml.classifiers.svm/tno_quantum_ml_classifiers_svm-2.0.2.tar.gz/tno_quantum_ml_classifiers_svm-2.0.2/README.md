# TNO Quantum: ML - Classifiers - Support Vector Machine

TNO Quantum provides generic software components aimed at facilitating the development
of quantum applications.

This package implements a scikit-learn compatible, (quantum) support vector machine.

During the fit, the (quantum) support vector machine solves a discretized version of
the continuous optimization problem posed by a standard kernel support vector machine.
This discrete optimization problem can be solved using quantum optimization algorithms
(DWAVE, QAOA, etc.). Predictions are done classically based on the solutions found
during fit.

An earlier version of the SVM was used in the following publication:
- [Three Quantum Machine Learning Approaches for Mobile User Indoor-Outdoor Detection - Phillipson et al. (2020)](https://publications.tno.nl/publication/34638453/4sWAlO/phillipson-2021-indoor.pdf)


*Limitations in (end-)use: the content of this software package may solely be used for applications 
that comply with international export control laws.*

## Documentation

Documentation of the `tno.quantum.ml.classifiers.svm` package can be found [here](https://tno-    
quantum.github.io/documentation/).


## Install

Easily install the `tno.quantum.ml.classifiers.svm` package using pip:

```console
$ python -m pip install tno.quantum.ml.classifiers.svm
```

## Example

The Support Vector Machine can be used as shown in the following example.

```python
from tno.quantum.ml.classifiers.svm import SupportVectorMachine
from tno.quantum.ml.datasets import get_iris_dataset

X_training, y_training, X_validation, y_validation = get_iris_dataset(n_classes=2)
svm = SupportVectorMachine()
svm = svm.fit(X_training, y_training)
predictions_validation = svm.predict(X_validation)
```
