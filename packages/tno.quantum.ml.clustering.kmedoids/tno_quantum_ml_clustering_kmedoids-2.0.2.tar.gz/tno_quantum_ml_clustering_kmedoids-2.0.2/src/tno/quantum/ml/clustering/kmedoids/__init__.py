"""This package provides a Quantum K-Medoids clustering algorithm.

It provides a Python implementation of a QUBO based K-Medoids clustering algorithm.

The implementation (see the :py:class:`~kmedoids.QKMedoids` class) has been
done in accordance with the `scikit-learn estimator API <https://scikit-learn.org/stable/developers/develop.html>`_,
which means that the clustering algorithm can be used as any other scikit-learn
clustering algorithm and combined with transforms through
`Pipelines <https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html>`_.


Example:
-----------
The following example shows how to use the
:py:class:`~tno.quantum.ml.clustering.kmedoids.QKMedoids` class for clustering
a synthetic dataset.

Note:
 The example requires the following additional dependencies:

 - :py:mod:`tno.quantum.ml.datasets`: Used for the generation of artificial dataset.
 - :py:mod:`tno.quantum.optimization.qubo.solvers`: Provides the specific QUBO solvers. In this example solvers from ``[dwave]`` are used.

  Both can be installed alongside with the package by providing the ``[example]`` flag::
  Both can be installed alongside with the package by providing the ``[example]`` flag::

    pip install tno.quantum.ml.clustering.kmedoids[example]

Generate sample data:

>>> from tno.quantum.ml.datasets import get_blobs_clustering_dataset
>>> n_centers = 3
>>> X, true_labels = get_blobs_clustering_dataset(
...     n_samples=60, n_features=2, n_centers=n_centers
... )

Create :py:class:`~kmedoids.QKMedoids` object and fit:

>>> from tno.quantum.ml.clustering.kmedoids import QKMedoids
>>> cobj = QKMedoids(
...     n_clusters=n_centers,
...     solver_config={
...         "name": "simulated_annealing_solver",
...         "options": {"random_state": 42, "num_read": 1000, "num_sweeps": 2000},
...     },
... )
>>> pred_labels = cobj.fit_predict(X)

Plot results:

>>> import matplotlib.pyplot as plt
>>> import numpy as np
>>> fig, ax = plt.subplots()  # doctest: +SKIP
>>> unique_labels = np.unique(pred_labels)
>>> colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
>>> for k, col in zip(unique_labels, colors):  # doctest: +SKIP
...     mask = cobj.labels_ == k
...     x, y = X[mask].T
...     ax.plot(x, y, "o", mfc=col, mec="k", ms=6)  # doctest: +SKIP
>>> x_centers, y_centers = cobj.cluster_centers_.T
>>> ax.plot(x_centers, y_centers, "o", mfc="cyan", mec="k", ms=6)  # doctest: +SKIP
>>> ax.set_title("Quantum KMedoids clustering")  # doctest: +SKIP
>>> plt.savefig("/tmp/qkmedoids.png")  # doctest: +SKIP

.. image:: assets/example.png
    :width: 600
    :align: center
    :alt: Clustering example.
"""  # noqa: E501

from tno.quantum.ml.clustering.kmedoids._kmedoids import QKMedoids

__all__ = ["QKMedoids"]

__version__ = "2.0.2"
