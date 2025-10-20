"""QBKMeans is part of TNO Quantum.

It provides a Python implementation of a QUBO based Balanced K-Means clustering
algorithm.

The implementation (see the :py:class:`~bkmeans.QBKMeans` class) has been
done in accordance with the `scikit-learn estimator API <https://scikit-learn.org/stable/developers/develop.html>`_,
which means that the clustering algorithm can be used as any other scikit-learn
clustering algorithm and combined with transforms through
`Pipelines <https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html>`_.

Example:
-----------
Here's an example of how the :py:class:`~bkmeans.QBKMeans` class can be used
for clustering a randomly generated dataset.

Note:
 The example requires the following additional dependencies:

 - :py:mod:`tno.quantum.ml.datasets`: Used for the generation of artificial dataset.
 - :py:mod:`tno.quantum.optimization.qubo.solvers`: Provides the specific QUBO solvers. In this example solvers from ``[dwave]`` are used.

  Both can be installed alongside with the package by providing the ``[example]`` flag::

    pip install tno.quantum.ml.clustering.bkmeans[example]

Generate sample data:

>>> from tno.quantum.ml.datasets import get_blobs_clustering_dataset
>>> n_centers = 4
>>> X, true_labels = get_blobs_clustering_dataset(
...     n_samples=20, n_features=2, n_centers=n_centers
... )

Create :py:class:`~bkmeans.QBKMeans` object and fit:

>>> from tno.quantum.ml.clustering.bkmeans import QBKMeans
>>> cluster_algo = QBKMeans(
...     n_clusters=n_centers,
...     solver_config={
...         "name":"simulated_annealing_solver",
...         "options": {"number_of_reads": 100}
...     },
... )
>>> pred_labels = cluster_algo.fit_predict(X)


Plot results:

>>> import matplotlib.pyplot as plt
>>> import numpy as np
>>> fig, ax = plt.subplots()  # doctest: +SKIP
>>> unique_labels = np.unique(pred_labels)
>>> colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
>>> for k, col in zip(unique_labels, colors):  # doctest: +SKIP
...     mask = cluster_algo.labels_ == k
...     x, y = X[mask].T
...     ax.plot(x, y, "o", mfc=col, mec="k", ms=6)  # doctest: +SKIP


>>> ax.set_title("Quantum BKMeans clustering")  # doctest: +SKIP
>>> plt.savefig("example.png")  # doctest: +SKIP
>>> plt.show()  # doctest: +SKIP

.. image:: assets/example.png
    :width: 600
    :align: center
    :alt: Clustering example.
"""  # noqa: E501

from tno.quantum.ml.clustering.bkmeans._bkmeans import QBKMeans

__all__ = ["QBKMeans"]

__version__ = "2.0.3"
