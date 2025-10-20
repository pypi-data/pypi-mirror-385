"""This module contains tests for the ``QKMedoids`` class."""

import re

import numpy as np
import pytest
from sklearn.metrics import adjusted_rand_score
from sklearn.utils.estimator_checks import check_estimator
from tno.quantum.ml.components import check_estimator_serializable
from tno.quantum.ml.datasets import get_blobs_clustering_dataset
from tno.quantum.utils import BitVector

from tno.quantum.ml.clustering.kmedoids import QKMedoids


def test_sklearn_compliance() -> None:
    """Check compliance with the sklearn interface."""
    qkmedoids = QKMedoids(
        solver_config={
            "name": "simulated_annealing_solver",
            "options": {"random_state": 42},
        }
    )
    check_estimator(qkmedoids)


@pytest.mark.parametrize(
    ("n_samples", "n_features", "n_centers"),
    [(8, 2, 2), (80, 2, 2), (40, 2, 3), (40, 3, 2), (40, 3, 3)],
)
def test_check_clustering(n_samples: int, n_features: int, n_centers: int) -> None:
    """CHeck clustering of QKMedoids."""
    data, true_labels = get_blobs_clustering_dataset(n_samples, n_features, n_centers)

    qkmedoids = QKMedoids(
        n_clusters=n_centers,
        solver_config={
            "name": "simulated_annealing_solver",
            "options": {
                "number_of_reads": 10,
                "number_of_sweeps": 100,
                "random_state": 42,
            },
        },
    )
    pred_labels = qkmedoids.fit_predict(data)
    assert len(np.unique(pred_labels)) == n_centers
    assert adjusted_rand_score(true_labels, pred_labels) == 1


@pytest.mark.parametrize(
    ("bit_vector", "n_clusters"),
    [(BitVector([1, 0, 1, 0]), 2), (BitVector((1, 0, 0, 0, 1, 0, 0, 0, 1)), 3)],
)
def test_quantum_k_medoid_constrains_true(
    bit_vector: BitVector, n_clusters: int
) -> None:
    """Test if valid bit vectors don't break any constraints."""
    qkmedoids = QKMedoids(n_clusters=n_clusters)
    assert qkmedoids._check_constraints(bit_vector)


@pytest.mark.parametrize(
    ("bit_vector", "n_clusters", "expected_warning_message"),
    [
        (
            BitVector([1, 1, 0, 0]),
            1,
            "Number of desired clusters is 1, but 2 clusters were assigned. "
            "Consider changing increasing 'gamma' or changing the number of clusters.",
        ),
        (
            BitVector([0, 0, 0, 0]),
            2,
            "Number of desired clusters is 2, but 0 clusters were assigned. "
            "Consider changing increasing 'gamma' or changing the number of clusters.",
        ),
        (
            BitVector([1, 0, 0, 0]),
            2,
            "Number of desired clusters is 2, but 1 clusters were assigned. "
            "Consider changing increasing 'gamma' or changing the number of clusters.",
        ),
        (
            BitVector([1, 1, 1]),
            2,
            "Number of desired clusters is 2, but 3 clusters were assigned. "
            "Consider changing increasing 'gamma' or changing the number of clusters.",
        ),
        (
            BitVector([1]),
            0,
            "Number of desired clusters is 0, but 1 clusters were assigned. "
            "Consider changing increasing 'gamma' or changing the number of clusters.",
        ),
    ],
)
def test_qkmedoids_constraints_violated_warns_full_message(
    bit_vector: BitVector, n_clusters: int, expected_warning_message: str
) -> None:
    """Test if invalid bit vectors raise the full constraint violation warning."""
    qkmedoids = QKMedoids(n_clusters=n_clusters)
    with pytest.warns(UserWarning, match=re.escape(expected_warning_message)):
        result = qkmedoids._check_constraints(bit_vector)
    assert result is False


def test_equality() -> None:
    """Test equality of QKMedoids."""
    estimator_1 = QKMedoids()
    estimator_2 = QKMedoids()
    assert estimator_1 == estimator_2
    X = [[1, 1], [0, 1]]
    estimator_1.fit(X)
    assert estimator_1 != estimator_2
    estimator_2.fit(X)
    assert estimator_1 == estimator_2


def test_serialization() -> None:
    """Test correct serialization of estimator."""
    estimator1 = QKMedoids()
    check_estimator_serializable(estimator1)
    estimator2 = QKMedoids()
    X = [[1.0, 2.0], [3.0, 4.0]]
    estimator2.fit(X)
    check_estimator_serializable(estimator2)
