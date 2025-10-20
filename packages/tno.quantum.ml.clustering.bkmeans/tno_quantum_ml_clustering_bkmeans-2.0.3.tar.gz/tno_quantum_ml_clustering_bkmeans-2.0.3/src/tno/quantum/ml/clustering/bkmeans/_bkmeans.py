"""This module contains a scikit-learn compatible, balanced K-means clustering."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any, SupportsFloat, SupportsInt, cast

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.linalg import block_diag
from sklearn.base import ClusterMixin, Tags
from sklearn.metrics.pairwise import pairwise_distances
from tno.quantum.ml.components import QUBOEstimator, get_default_solver_config_if_none
from tno.quantum.optimization.qubo.components import QUBO, SolverConfig
from tno.quantum.utils.validation import check_arraylike, check_int, check_real

if TYPE_CHECKING:
    from typing import Self

    from tno.quantum.utils import BitVector


class QBKMeans(ClusterMixin, QUBOEstimator):  # type: ignore[misc]
    """Quantum Balanced K-means clustering."""

    def __init__(
        self,
        n_clusters: SupportsInt = 2,
        alpha: SupportsFloat = 0.4,
        beta: SupportsFloat = 0.4,
        metric: str | Callable[[ArrayLike, ArrayLike], float] = "euclidean",
        solver_config: SolverConfig | Mapping[str, Any] | None = None,
    ) -> None:
        r"""Init ``QBKMeans`` clustering algorithm.

        The QBKMeans algorithm is an unsupervised machine learning model that partitions
        training data into $k$ clusters such that each point belongs to the cluster with
        the nearest centroid while each cluster contains approximately $N/k$ points. The
        algorithm translates this task into a QUBO formulation as formulated in
        `[1] <https://www.nature.com/articles/s41598-021-89461-4#Sec13>`_. Its cost
        function is given by:

        .. _QUBO cost function:
        .. math::

            \hat{w}^T\left(
            I_k \otimes \left(D + \alpha F\right)
            +
            Q^T\left(I_N\otimes \beta G\right) Q
            \right)\hat{w}.

        where

        .. _F function:
        .. math::

            F &= 1_N - {2N}/{k} I_N, \\
            G &= 1_k - 2I_k, \\
            Q_{ij} &= \begin{cases}
                1  & j=N\cdot (i-1 \mod k) + \lfloor {i-1}/k \rfloor + 1, \\
                0 & \text{ otherwise.}
                \end{cases}

        **Details:**

        * $\hat{w}$ are $Nk$ binary decision variables.
        * $N$ is the number of datapoints.
        * $k$ is the number of clusters.
        * $D$ is the distance matrix.
        * $\alpha$ is the weight parameter of the first objective, i.e., each cluster has approximately $N/k$ entries.
        * $\beta$ is the weight parameter of the second objective, i.e., each cluster is assigned a unique cluster.

        Args:
            n_clusters: The number of clusters to form ($k$). Must be a strictly
                positive integer value.
            alpha: Weight parameter for the constraint that each cluster contains
                approximately $N/k$ entries. Penalty is scaled by the largest pairwise
                distance in the dataset. Must be non-negative and defaults to `0.4`.
            beta: The penalty parameter for the constraint that each datapoint
                is assigned a unique cluster. Penalty is scaled by the largest pairwise
                distance in the dataset multiplied with $N/k$, i.e. average number of
                datapoints per cluster.
            metric: The metric to use when calculating distance between instances in a
                feature array, see :py:func:`sklearn.metrics.pairwise_distances`. If
                metric is a string, it must be one of the options allowed by
                :py:func:`scipy.spatial.distance.pdist`. If metric is ``"precomputed"``,
                X is assumed to be a distance matrix. If metric is a callable function,
                it is called on each pair of instances and the resulting values. The
                callable should take two arrays from X as input and return a value
                indicating their distance.
            solver_config: A QUBO solver configuration or None. In the former case
                includes name and options. If ``None`` is given, the default solver
                configuration as defined in
                :py:func:`~tno.quantum.ml.components.get_default_solver_config_if_none`
                will be used. Default is ``None``.

        Attributes:
            X_: Training instances to cluster. Shape is assumed to be
                `(n_samples, n_features)`.
            N_: Number of samples in the dataset.
            distance_: Pairwise distance matrix of the dataset.
            labels_: 1-D array of length `n_samples` containing the assigned labels for
                each sample.
        """  # noqa: E501
        self.n_clusters = n_clusters
        self.alpha = alpha
        self.beta = beta
        self.metric = metric
        super().__init__(solver_config=solver_config)
        self.X_: NDArray[np.float64]
        self.N_: int
        self.distance_: NDArray[np.float64]
        self.labels_: NDArray[np.int_]

    def _make_qubo(
        self, X: NDArray[np.float64], y: NDArray[np.float64] | None = None
    ) -> QUBO:
        """Creates QUBO for balanced k-means clustering.

        See the docstring of :py:class:`~bkmeans.QBKMeans` for the definitions
        of the variables F,G and Q.

        Args:
            X: Training instances to cluster. Shape is assumed to be
                `(n_samples, n_features)`.
            y: Ignored.

        Returns:
            qubo: QUBO representation of Balanced K-means clustering.
        """
        self.N_ = self.X_.shape[0]
        # Check if the user has given valid input before doing any computations
        alpha = check_real(self.alpha, "alpha", l_bound=0)
        beta = check_real(self.beta, "beta", l_bound=0)
        n_clusters = check_int(self.n_clusters, "n_clusters", l_bound=1)
        self.distance_ = pairwise_distances(X, metric=self.metric)

        # For each cluster, ensure it contains approximately N/n_clusters points
        F = np.ones((self.N_, self.N_))
        np.fill_diagonal(F, 1 - 2 * self.N_ / n_clusters)

        # For each point, ensure that it belongs to exactly one cluster
        G = np.ones((n_clusters, n_clusters))
        np.fill_diagonal(G, -1)

        # To build the QUBO A, take the weighted sum of the constraints
        Q = np.zeros((self.N_ * n_clusters, self.N_ * n_clusters))
        row_indices = np.arange(self.N_ * n_clusters)
        col_indices = self.N_ * (row_indices % n_clusters) + row_indices // n_clusters
        Q[row_indices, col_indices] = 1

        scaled_alpha = alpha * np.max(self.distance_)
        scaled_beta = beta * np.max(self.distance_) * (self.N_ / n_clusters)

        qubo_matrix = (
            block_diag(*(self.distance_ + scaled_alpha * F for _ in range(n_clusters)))
            + Q.T @ block_diag(*(scaled_beta * G for _ in range(self.N_))) @ Q
        )

        return QUBO(np.asarray(qubo_matrix))

    def fit(self, X: ArrayLike, y: ArrayLike | None = None) -> Self:
        """Fit the model to data matrix X.

        Args:
            X: The input data.
            y: Ignored.

        Returns:
            Returns self, a trained ``QBKMeans`` class.
        """
        return cast("QBKMeans", super().fit(X, y=y))

    def _check_X_and_y(  # noqa: N802
        self, X: NDArray[np.float64], y: NDArray[np.float64] | None = None
    ) -> None:
        """Check if `X` and `y` are as expected.

        Args:
            X: training data with shape (`n_samples`, `n_features`).
            y: target values with shape (`n_samples`,) or ``None``. Defaults to
                ``None``.

        Raises:
            ValueError: if data is not suitable for estimator.
        """
        # Check at least 2 samples
        check_arraylike(X, "X", ndim=2)
        n_samples = X.shape[0]
        if n_samples < 2:
            error_msg = (
                f"{self.__class__.__name__} requires at least 2 samples, "
                f"but got n_samples = {n_samples}."
            )
            raise ValueError(error_msg)

    def _check_constraints(self, solution: ArrayLike) -> bool:
        """Check if the found solution string satisfies the imposed constraints.

        Constraints:
            1. Each cluster contains approximately $N/K$ entries,
            2. Each datapoint is assigned a unique cluster.

        Args:
            solution: 1-D ArrayLike with binary elements containing the solution to
            the QUBO.

        Returns:
            True if there are no violations, False otherwise.
        """
        violations = False
        n_clusters = int(self.n_clusters)
        solution = np.reshape(solution, (n_clusters, self.N_))

        l_bound = np.floor(self.N_ / n_clusters)
        u_bound = np.ceil(self.N_ / n_clusters)
        for cluster_idx, n_items in enumerate(np.count_nonzero(solution, axis=1)):
            if not (l_bound <= n_items <= u_bound):
                warnings.warn(
                    f"Cluster {cluster_idx} contains {n_items} items.  Which is not "
                    f"approximately N/K={self.N_ / n_clusters:.2f}. Consider "
                    "increasing the penalty parameter alpha.",
                    stacklevel=2,
                )
                violations = True

        assigned_number_of_clusters = np.count_nonzero(solution, axis=0)
        for data_idx, n_assigned_clusters in enumerate(assigned_number_of_clusters):
            if n_assigned_clusters != 1:
                warnings.warn(
                    f"Datapoint {data_idx} is assigned to {n_assigned_clusters} "
                    "clusters. Consider increasing the penalty parameter beta.",
                    stacklevel=2,
                )
                violations = True

        return not violations

    def _decode_bit_vector(self, bit_vector: BitVector) -> Self:
        """Decode `bit_vector` and set attributes.

        If the solution assigns zero clusters to the datapoint, it will be assigned to
        the current smallest cluster.

        If the solution assigns multiple clusters to the datapoint, it will be assigned
        to the smallest cluster among the assigned clusters.

        Args:
            bit_vector : ``BitVector`` with binary elements containing the solution to
                the QUBO.

        Attributes:
            - labels_: NDArray[np.int_], shape = (n_samples,)
        """
        n_clusters = int(self.n_clusters)
        self.labels_ = np.zeros(self.N_, dtype=np.int32)
        solution = np.reshape(bit_vector, (n_clusters, self.N_))

        for i, datapoint in enumerate(solution.T):
            non_zero_idxs = np.nonzero(datapoint)[0]
            if non_zero_idxs.size == 1:
                self.labels_[i] = non_zero_idxs[0]
            elif non_zero_idxs.size == 0:
                # Handle case by assigning datapoint to current smallest cluster
                cluster_sizes = {
                    cluster_idx: int(np.count_nonzero(self.labels_[:i] == cluster_idx))
                    for cluster_idx in range(n_clusters)
                }
                smallest_cluster = min(cluster_sizes, key=lambda k: cluster_sizes[k])
                self.labels_[i] = smallest_cluster
            elif non_zero_idxs.size > 1:
                # Handle case by assigning datapoint to smallest candidate clusters
                cluster_sizes = {
                    cluster_idx: int(np.count_nonzero(self.labels_[:i] == cluster_idx))
                    for cluster_idx in non_zero_idxs
                }
                smallest_cluster = min(cluster_sizes, key=lambda k: cluster_sizes[k])
                self.labels_[i] = smallest_cluster
        return self

    def __sklearn_tags__(self) -> Tags:
        """Return estimator tags."""
        tags = super().__sklearn_tags__()
        solver_config = get_default_solver_config_if_none(self.solver_config)
        solver = solver_config.get_instance()
        tags.non_deterministic = solver.non_deterministic
        return tags
