"""This module contains a scikit-learn compatible, quantum K-medoid clustering."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any, SupportsFloat, SupportsInt, TypeVar, cast

import numpy as np
from numpy.typing import ArrayLike, NDArray
from sklearn.base import ClusterMixin, Tags
from sklearn.metrics.pairwise import pairwise_distances
from tno.quantum.ml.components import QUBOEstimator, get_default_solver_config_if_none
from tno.quantum.optimization.qubo.components import QUBO, SolverConfig
from tno.quantum.utils.validation import check_int, check_real

if TYPE_CHECKING:
    from tno.quantum.utils import BitVector

QKMedoidsT = TypeVar("QKMedoidsT", bound="QKMedoids")


class QKMedoids(ClusterMixin, QUBOEstimator):  # type: ignore[misc]
    """Quantum K-medoid clustering."""

    def __init__(  # noqa: PLR0913
        self,
        n_clusters: SupportsInt = 2,
        alpha: SupportsFloat = 1,
        beta: SupportsFloat = 1,
        gamma: SupportsFloat = 2,
        metric: str | Callable[[ArrayLike, ArrayLike], float] = "euclidean",
        solver_config: SolverConfig | Mapping[str, Any] | None = None,
    ) -> None:
        r"""Init ``QKMedoid`` clustering algorithm.

        The QKMedoid algorithm minimizes a double objective function with a constraint
        translated to a QUBO formulation. The first objective maximizes the distance
        between the medoids, while the second objective tries to make the medoid as
        centrally positioned as possible. The constraint restricts the number of medoids
        to be exactly equal to $k$. The QUBO is an implementation of the work shown in
        `[1] <https://ceur-ws.org/Vol-2454/paper_39.pdf>`_ and
        `[2] <https://link.springer.com/chapter/10.1007/978-3-031-40852-6_12>`_.
        Its cost function is given by:


        .. _QUBO cost function:
        .. math::

            \sum_{i=1}^N\sum_{j=1}^Nz_iz_j\left(\gamma-\frac{1}{2}\alpha\Delta_{ij}\right)
            +
            \sum_{i=1}^Nz_i\left(\beta\sum_{j=1}^N\Delta_{ij}-2\gamma k\right).

        **Details:**

        * $z_{i}$ are the binary decision variables.
        * $N$ is the number of datapoints.
        * $k$ is the number of clusters.
        * $\Delta_{ij}=1-\exp(-\frac{1}{2}d_{ij})$, where $d_{ij}$ is the distance between data point $i$ and $j$.
        * $\alpha$ is the weight parameter of the first objective, i.e., maximizing the distance between the medoids.
        * $\beta$ is the weight parameter of the second objective, i.e., centralizing the medoids.
        * $\gamma$ is the penalty parameter for the constraint that there must be exactly $k$ medoids.

        Args:
            n_clusters: The number of clusters to form ($k$). Must be a strictly
                positive integer value.
            alpha: Weight parameter for identifying far apart points. The weight is
                scaled by `1 / (number of clusters)`. Must be non-negative and defaults
                to 1.
            beta: Weight parameter for identifying central points. The weight is scaled
                by `1 / (number of samples)`. Must be non-negative and defaults to 1.
            gamma: Penalty parameter for the constraint that the solution contains
                exactly the specified number of clusters ($k$).The penalty is scaled
                by $\max_{i,j}\left(1-\exp(-\frac{1}{2}d_{ij})\right)$, where $d_{ij}$
                is the distance between data point $i$ and $j$. Must be non-negative and
                defaults to 2.
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
            distance_: 2-D array of shape `(n_features, n_features)` containing the
                pairwise distances between each feature vector.
            medoid_indices_: 1-D array of length `n_clusters` containing the indices of
                the medoid row in the feature matrix $X$.
            cluster_centers_: 2-D array of shape `(n_cluster, n_features)` containing
                the cluster centers (elements from original dataset $X$).
            labels_: 1-D array of length `n_samples` containing the assigned labels for
                each sample.
            inertia_: The sum of distances of samples to their closest cluster center.
        """  # noqa: E501
        self.n_clusters = n_clusters
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.metric = metric
        super().__init__(solver_config=solver_config)
        self.distance_: NDArray[np.float64]
        self.medoid_indices_: NDArray[np.int64]
        self.cluster_centers_: NDArray[np.float64]
        self.labels_: NDArray[np.int_]
        self.inertia_: float

    def _make_qubo(
        self, X: NDArray[np.float64], y: NDArray[np.float64] | None = None
    ) -> QUBO:
        """Create QUBO for k-medoid clustering.

        Args:
            X: Training instances to cluster. Shape is assumed to be
                `(n_samples, n_features)`.
            y: Ignored.

        Attributes:
            distance_: 2-D array of shape `(n_features, n_features)` containing the
                pairwise distances between each feature vector.

        Returns:
            A QUBO representation of K-medoid clustering.
        """
        # Check if the user has given valid input before doing any computations
        alpha = check_real(self.alpha, "alpha", l_bound=0)
        beta = check_real(self.beta, "beta", l_bound=0)
        gamma = check_real(self.gamma, "gamma", l_bound=0)
        n_clusters = check_int(self.n_clusters, "n_clusters", l_bound=1)

        # For each cluster, minimise the distance to the clusterhead
        self.distance_ = pairwise_distances(X, metric=self.metric)
        delta = 1 - np.exp(-0.5 * self.distance_)

        # Scale the hyper-parameters to the appropriate size
        n_features = len(X)
        scaled_alpha = alpha / n_clusters
        scaled_beta = beta / n_features
        scaled_gamma = gamma * np.max(delta)

        cost1 = scaled_gamma - 0.5 * scaled_alpha * delta
        cost2 = delta.sum(axis=0) * scaled_beta - 2 * scaled_gamma * self.n_clusters

        return QUBO(cost1 + np.diag(cost2))

    def fit(self: QKMedoidsT, X: ArrayLike, y: ArrayLike | None = None) -> QKMedoidsT:
        """Fit the model to data matrix X.

        Args:
            X: The input data.
            y: Ignored.

        Returns:
            Returns self, a trained ``QKMedoids`` class.
        """
        return cast("QKMedoids", super().fit(X, y))

    def _check_X_and_y(  # noqa: N802
        self, X: NDArray[np.float64], y: NDArray[np.float64] | None = None
    ) -> None:
        """Check if `X` is a valid feature matrix.

        Args:
            X: The input data.
            y: Ignored.

        Raises:
            ValueError: If X does not contain at least 2 samples.
        """
        # Check at least 2 samples
        n_samples = len(X)
        if n_samples < 2:
            error_msg = (
                f"{self.__class__.__name__} requires at least 2 samples, "
                f"but got n_samples = {n_samples}."
            )
            raise ValueError(error_msg)

    def _check_constraints(self, bit_vector: BitVector) -> bool:
        """Check if the found bit vector satisfies the imposed constraints.

        In this model, the only constraint is that there are exactly `n_cluster` cluster
        heads assigned.

        Args:
            bit_vector: BitVector containing the solution to the QUBO.

        Returns:
            True if there are no violations, False otherwise
        """
        num_clusterheads = np.count_nonzero(bit_vector)
        if num_clusterheads != self.n_clusters:
            warnings.warn(
                stacklevel=2,
                message=f"Number of desired clusters is {self.n_clusters}, but "
                f"{num_clusterheads} clusters were assigned. Consider changing "
                "increasing 'gamma' or changing the number of clusters.",
            )
            return False
        return True

    def _decode_bit_vector(self: QKMedoidsT, bit_vector: BitVector) -> QKMedoidsT:
        """Decode bit vector and set attributes.

        Args:
            bit_vector : A bit vector containing the solution to the QUBO.

        Attributes:
            medoid_indices_: 1-D array of length `n_clusters` containing the indices of
                the medoid row in the feature matrix $X$.
            cluster_centers_: 2-D array of shape `(n_cluster, n_features)` containing
                the cluster centers (elements from original dataset $X$).
            labels_: 1-D array of length `n_samples` containing the assigned labels for
                each sample.
            inertia_: The sum of distances of samples to their closest cluster center.

        Returns:
            ``Self``
        """
        self.medoid_indices_ = np.flatnonzero(bit_vector)
        self.cluster_centers_ = self.X_[self.medoid_indices_]

        # Distance from each point to the medoids
        self.labels_ = self.distance_[:, self.medoid_indices_].argmin(axis=1)
        self.inertia_ = self._compute_inertia()

        return self

    def _compute_inertia(self) -> float:
        """Compute inertia of clustering.

        Inertia is defined as the sum of the sample distances to closest cluster
        centers.

        Returns:
            inertia: Sum of sample distances to closest cluster centers.
        """
        n_features = len(self.X_)
        data_indices = np.arange(n_features)
        cluster_indices = self.medoid_indices_[self.labels_]
        return float(self.distance_[data_indices, cluster_indices].sum())

    def __sklearn_tags__(self) -> Tags:
        """Return estimator tags."""
        tags = super().__sklearn_tags__()
        solver_config = get_default_solver_config_if_none(self.solver_config)
        solver = solver_config.get_instance()
        tags.non_deterministic = solver.non_deterministic
        return tags
