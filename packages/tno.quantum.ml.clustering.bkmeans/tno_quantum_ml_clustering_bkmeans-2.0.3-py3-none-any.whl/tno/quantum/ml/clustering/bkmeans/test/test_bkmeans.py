"""This module contains tests for the ``QBKMeans`` class."""

import warnings

import numpy as np
import pytest
from numpy.typing import ArrayLike
from sklearn.metrics import adjusted_rand_score
from sklearn.utils.estimator_checks import check_estimator
from tno.quantum.ml.components import check_estimator_serializable
from tno.quantum.ml.datasets import get_blobs_clustering_dataset

from tno.quantum.ml.clustering.bkmeans import QBKMeans


def test_sklearn_compliance() -> None:
    """Check compliance with the sklearn interface."""
    qbkmeans = QBKMeans()
    for estimator, check in check_estimator(qbkmeans, generate_only=True):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            check(estimator)


@pytest.mark.parametrize(
    ("n_samples", "n_features", "n_clusters"),
    [(8, 2, 2), (80, 2, 2), (30, 2, 3), (40, 3, 2), (60, 3, 3)],
)
def test_check_clustering(n_samples: int, n_features: int, n_clusters: int) -> None:
    """Check clustering of QBKMeans."""
    data, true_labels = get_blobs_clustering_dataset(n_samples, n_features, n_clusters)
    solver_config = {
        "name": "simulated_annealing_solver",
        "options": {"number_of_reads": 100, "random_state": 42},
    }
    qbkmeans = QBKMeans(solver_config=solver_config, n_clusters=n_clusters)
    pred_labels = qbkmeans.fit_predict(data)
    assert len(np.unique(pred_labels)) == n_clusters
    assert adjusted_rand_score(true_labels, pred_labels) == 1


@pytest.mark.parametrize(
    ("solution", "num_points", "n_clusters"),
    [
        # Clusters balanced; each point assigned to one cluster
        ([[1, 0, 1, 0], [0, 1, 0, 1]], 4, 2),
        # Clusters balanced (as possible); each point assigned to one cluster
        ([[1, 1, 1, 0, 0], [0, 0, 0, 1, 1]], 5, 2),
        # Clusters balanced; each point assigned to one cluster
        (
            [
                [1, 1, 1, 0, 0, 0, 0, 0, 0],  # cluster 0
                [0, 0, 0, 1, 1, 1, 0, 0, 0],  # cluster 1
                [0, 0, 0, 0, 0, 0, 1, 1, 1],  # cluster 3
            ],
            9,
            3,
        ),
    ],
)
def test_quantum_b_k_means_constraints_true(
    solution: ArrayLike, num_points: int, n_clusters: int
) -> None:
    """Check valid solution constrains."""
    solution = np.array(solution).flatten()
    qbkmeans = QBKMeans(n_clusters=n_clusters)
    qbkmeans.N_ = num_points
    assert qbkmeans._check_constraints(solution)


@pytest.mark.parametrize(
    ("solution", "num_points", "n_clusters", "penalty_parameter"),
    [
        # Unbalanced clusters
        ([[1, 1, 1, 1, 0], [0, 0, 0, 0, 1]], 5, 2, "alpha"),
        # Unbalanced clusters
        (
            [
                [1, 1, 1, 1, 0, 0, 0, 0, 0],  # cluster 0
                [0, 0, 0, 0, 1, 1, 1, 1, 0],  # cluster 1
                [0, 0, 0, 0, 0, 0, 0, 0, 1],  # cluster 2
            ],
            9,
            3,
            "alpha",
        ),
        # First point assigned to two clusters
        ([[1, 1, 1, 1, 0, 0, 0, 0], [1, 0, 0, 0, 1, 1, 1, 1]], 8, 2, "beta"),
        # First point assigned to no cluster
        (
            [
                [0, 1, 1, 0, 0, 0, 0],  # cluster 0
                [0, 0, 0, 1, 1, 0, 0],  # cluster 1
                [0, 0, 0, 0, 0, 1, 1],  # cluster 2
            ],
            7,
            3,
            "beta",
        ),
    ],
)
def test_quantum_b_k_means_constraints_false(
    solution: ArrayLike, num_points: int, n_clusters: int, penalty_parameter: float
) -> None:
    """Check invalid solution constrains."""
    solution = np.array(solution).flatten()
    qbkmeans = QBKMeans(n_clusters=n_clusters)
    qbkmeans.N_ = num_points
    with pytest.warns(
        UserWarning,
        match=f"Consider increasing the penalty parameter {penalty_parameter}",
    ):
        assert not qbkmeans._check_constraints(solution)


def test_equality() -> None:
    estimator_1 = QBKMeans()
    estimator_2 = QBKMeans()
    assert estimator_1 == estimator_2
    X = [[1, 1], [0, 1]]
    estimator_1.fit(X)
    assert estimator_1 != estimator_2
    estimator_2.fit(X)
    assert estimator_1 == estimator_2


def test_serialization() -> None:
    estimator1 = QBKMeans()
    check_estimator_serializable(estimator1)
    estimator2 = QBKMeans()
    X = [[1.0, 2.0], [3.0, 4.0]]
    estimator2.fit(X)
    check_estimator_serializable(estimator2)
