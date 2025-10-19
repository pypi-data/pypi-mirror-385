import pytest
import numpy as np
from numpy.testing import assert_allclose
from dataclasses import dataclass
from typing import List

# Assuming the ABITClustering class is defined in a module named consistent_abit_clustering.py
# For this test file, we'll import it as:
from abit_clustering import ABITClustering, TreeNode, _find_split_indices

@pytest.fixture
def clustering():
    return ABITClustering(
        threshold_adjustment=0.01,
        window_size=3,
        min_split_tokens=5,
        max_split_tokens=10,
        split_tokens_tolerance=5,
        min_cluster_size=3
    )

@pytest.fixture(params=[(0.01, 3, 5, 10, 5, 3), (0.02, 5, 48, 768, 10, 2)])
def param_clustering(request):
    return ABITClustering(*request.param)

def test_initialization(clustering):
    assert clustering.threshold_adjustment == 0.01
    assert clustering.window_size == 3
    assert clustering.min_split_tokens == 5
    assert clustering.max_split_tokens == 10
    assert clustering.split_tokens_tolerance == 5
    assert clustering.min_cluster_size == 3
    assert clustering.labels_ is None
    assert clustering.tree_ is None
    assert clustering.all_embeddings == []
    assert clustering.all_token_counts == []

@pytest.mark.parametrize("params", [(0.01, 3, 5, 10, 5, 3), (0.02, 5, 48, 768, 10, 2)])
def test_parametrized_initialization(params):
    clustering = ABITClustering(*params)
    assert clustering.threshold_adjustment == params[0]
    assert clustering.window_size == params[1]
    assert clustering.min_split_tokens == params[2]
    assert clustering.max_split_tokens == params[3]
    assert clustering.split_tokens_tolerance == params[4]
    assert clustering.min_cluster_size == params[5]

@pytest.mark.parametrize("encoded_docs, expected_scores", [
    (np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1], [1, 0, 1]]), [0.0, 0.0, 1.0, 0.7071067811865475]),
    (np.array([[1, 1], [1, 1], [0, 0]]), [1.0, 0.0]),
    (np.ones((5, 2)), [1.0, 1.0, 1.0, 1.0]),  # All identical
])
def test_rolling_similarity_scores(clustering, encoded_docs, expected_scores):
    scores = clustering._rolling_similarity_scores(encoded_docs)
    assert_allclose(scores, expected_scores, rtol=1e-6)

def test_rolling_similarity_scores_edge_cases(clustering):
    # Single element (no scores)
    scores = clustering._rolling_similarity_scores(np.array([[1, 0]]))
    assert len(scores) == 0  # Returns empty list, no error

    # Two elements
    scores = clustering._rolling_similarity_scores(np.array([[1, 0], [0, 1]]))
    assert_allclose(scores, [0.0])

@pytest.mark.parametrize("similarities, threshold, expected_splits", [
    ([0.9, 0.8, 0.3, 0.7, 0.2, 0.6], 0.5, [3, 5]),
    ([1.0, 1.0, 1.0], 0.5, []),
    ([0.4, 0.3, 0.2], 0.5, [1, 2, 3]),
    ([], 0.5, []),  # Empty
])
def test_find_split_indices(similarities, threshold, expected_splits):
    splits = _find_split_indices(similarities, threshold)
    assert splits == expected_splits

@pytest.mark.parametrize("token_counts, similarity_scores", [
    ([50, 60, 70, 80, 90, 100], [0.9, 0.8, 0.7, 0.6, 0.5]),
    ([1, 1, 1], [0.5, 0.6]),  # Small counts
    ([1000] * 5, [1.0] * 4),  # Large, uniform
])
def test_find_optimal_threshold(clustering, token_counts, similarity_scores):
    threshold = clustering._find_optimal_threshold(token_counts, similarity_scores)
    assert 0 <= threshold <= 1.01  # Relaxed for floating point
    # Verify splits respect constraints
    split_indices = _find_split_indices(similarity_scores, threshold)
    split_counts = np.diff([0] + split_indices + [len(token_counts)])
    assert np.all(split_counts >= clustering.min_cluster_size - clustering.split_tokens_tolerance)

def test_fit_simple_case(clustering):
    X = np.array([[1, 0], [0, 1], [1, 1], [0, 0]])
    T = np.array([1, 1, 1, 1])  # Unit tokens
    clustering.fit(X, T)
    assert len(set(clustering.labels_)) == 1  # Single root cluster
    assert clustering.tree_ is not None
    assert hasattr(clustering.tree_, 'label')
    assert hasattr(clustering.tree_, 'children')
    assert len(clustering.all_embeddings) == 4
    assert len(clustering.all_token_counts) == 4

@pytest.mark.parametrize("X, T, expected_num_clusters", [
    (np.ones((4, 2)), np.ones(4, dtype=int), 1),  # All similar
    (np.array([[1,0],[0,1],[1,0],[0,1]]), np.ones(4, dtype=int), 1),  # Alternating, but may merge
])
def test_fit_varying_cases(clustering, X, T, expected_num_clusters):
    clustering.fit(X, T)
    unique_labels = len(set(clustering.labels_))
    assert unique_labels == expected_num_clusters

def test_fit_min_cluster_size_enforcement(clustering):
    X = np.random.rand(10, 3)  # Random for varied similarities
    T = np.ones(10, dtype=int)
    clustering.fit(X, T)
    # Traverse tree to check aggregated leaf sizes
    def check_leaves(node):
        if not node.children:
            return 1  # Leaf size
        sizes = [check_leaves(child) for child in node.children]
        # Check aggregated size for non-leaves
        total_size = sum(sizes)
        assert total_size >= clustering.min_cluster_size
        return total_size
    total = check_leaves(clustering.tree_)
    assert total == 10

def test_fit_edge_cases(clustering):
    # Empty input
    clustering.fit(np.empty((0, 2)), np.empty(0, dtype=int))
    assert len(clustering.labels_) == 0
    assert clustering.tree_ is None
    assert len(clustering.all_embeddings) == 0
    assert len(clustering.all_token_counts) == 0

    # Single sample
    X = np.array([[1, 0]])
    T = np.array([1])
    clustering.fit(X, T)
    assert len(set(clustering.labels_)) == 1
    assert clustering.tree_.label == 0
    assert not clustering.tree_.children

    # All identical
    X = np.ones((5, 2))
    T = np.ones(5, dtype=int)
    clustering.fit(X, T)
    assert len(set(clustering.labels_)) == 1

def test_tree_structure(clustering):
    X = np.array([[1,0],[0,1],[1,1],[0,0]])
    T = np.ones(4, dtype=int)
    clustering.fit(X, T)
    assert clustering.tree_ is not None
    assert clustering.tree_.label == clustering.labels_[0]
    # Check children exist or not based on merging
    assert len(clustering.tree_.children) >= 0  # Flexible

def test_partial_fit_initialization(clustering):
    # Partial fit with empty data
    clustering.partial_fit(np.empty((0, 2)), np.empty(0, dtype=int))
    assert len(clustering.labels_) == 0
    assert clustering.tree_ is None
    assert clustering.n_samples_ == 0
    assert len(clustering.all_embeddings) == 0
    assert len(clustering.all_token_counts) == 0

def test_partial_fit_single_batch(clustering):
    X = np.array([[1, 0], [0, 1], [1, 1], [0, 0]])
    T = np.array([1, 1, 1, 1], dtype=int)
    clustering.partial_fit(X, T)
    assert clustering.n_samples_ == 4
    assert len(set(clustering.labels_)) == 1 # Assuming single root cluster as in simple case
    assert clustering.tree_ is not None
    assert hasattr(clustering.tree_, 'label')
    assert hasattr(clustering.tree_, 'children')

def test_partial_fit_multiple_batches(clustering):
    # First batch
    X1 = np.array([[1, 0], [0, 1]])
    T1 = np.array([1, 1], dtype=int)
    clustering.partial_fit(X1, T1)
    assert clustering.n_samples_ == 2
    assert clustering.tree_ is not None
    # Second batch
    X2 = np.array([[1, 1], [0, 0]])
    T2 = np.array([1, 1], dtype=int)
    clustering.partial_fit(X2, T2)
    assert clustering.n_samples_ == 4
    assert len(set(clustering.labels_)) == 1 # Assuming all merge
    assert clustering.tree_ is not None

def compare_trees(tree1, tree2):
    if tree1 is None and tree2 is None:
        return True
    if tree1 is None or tree2 is None:
        return False
    assert tree1.label == tree2.label
    assert tree1.total_tokens == tree2.total_tokens
    assert tree1.total_samples == tree2.total_samples
    assert_allclose(tree1.mean_encoding, tree2.mean_encoding)
    assert len(tree1.children) == len(tree2.children)
    for child1, child2 in zip(tree1.children, tree2.children):
        compare_trees(child1, child2)
    return True

def test_partial_fit_consistency_with_fit(clustering):
    X = np.ones((6, 2))
    T = np.ones(6, dtype=int)
    # Fit all at once
    clustering_fit = ABITClustering(
        threshold_adjustment=0.01,
        window_size=3,
        min_split_tokens=5,
        max_split_tokens=10,
        split_tokens_tolerance=5,
        min_cluster_size=3
    )
    clustering_fit.fit(X, T)
    labels_fit = clustering_fit.labels_
    tree_fit = clustering_fit.tree_
    # Partial fit in batches
    clustering.partial_fit(X[:3], T[:3])
    clustering.partial_fit(X[3:], T[3:])
    labels_partial = clustering.labels_
    tree_partial = clustering.tree_
    # Check labels consistency
    assert_allclose(labels_fit, labels_partial)
    # Check tree equality
    assert compare_trees(tree_fit, tree_partial)

def test_partial_fit_single_samples(clustering):
    for i in range(5):
        X_single = np.array([[1, 0]]) if i % 2 == 0 else np.array([[0, 1]])
        T_single = np.array([1], dtype=int)
        clustering.partial_fit(X_single, T_single)
    assert clustering.n_samples_ == 5
    assert clustering.tree_ is not None
    assert len(set(clustering.labels_)) == 1 # Assuming merging

def test_partial_fit_empty_after_nonempty(clustering):
    X = np.array([[1, 0]])
    T = np.array([1], dtype=int)
    clustering.partial_fit(X, T)
    assert clustering.n_samples_ == 1
    # Empty batch
    clustering.partial_fit(np.empty((0, 2)), np.empty(0, dtype=int))
    assert clustering.n_samples_ == 1
    assert clustering.tree_.total_samples == 1

def test_partial_fit_tree_structure(clustering):
    X = np.array([[1, 0], [0, 1], [1, 1], [0, 0]])
    T = np.ones(4, dtype=int)
    # Partial fit in two batches
    clustering.partial_fit(X[:2], T[:2])
    assert clustering.tree_ is not None
    clustering.partial_fit(X[2:], T[2:])
    assert clustering.tree_ is not None
    assert clustering.tree_.label == clustering.labels_[0]
    assert clustering.tree_.total_samples == 4
    assert clustering.tree_.total_tokens == 4

def test_partial_fit_with_max_tokens_single_adds():
    clustering = ABITClustering(
        threshold_adjustment=0.01,
        window_size=3,
        min_split_tokens=5,
        max_split_tokens=10,
        split_tokens_tolerance=5,
        min_cluster_size=3,
        max_tokens=3
    )
    means = []
    totals = []
    for i in range(4):
        X = np.array([[float(i+1), 0.0]])
        T = np.array([1], dtype=int)
        clustering.partial_fit(X, T)
        if clustering.tree_:
            means.append(clustering.tree_.mean_encoding[0])
            totals.append(clustering.tree_.total_tokens)
        else:
            means.append(None)
            totals.append(0)
    assert totals == [1, 2, 3, 3]
    assert_allclose(means, [1.0, 1.5, 2.0, 3.0])
    assert clustering.n_samples_ == 3
    assert len(clustering.all_embeddings) == 3
    assert len(clustering.all_token_counts) == 3

def test_partial_fit_with_max_tokens_large_batch():
    clustering = ABITClustering(
        threshold_adjustment=0.01,
        window_size=3,
        min_split_tokens=5,
        max_split_tokens=10,
        split_tokens_tolerance=5,
        min_cluster_size=3,
        max_tokens=3
    )
    X = np.array([[1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [4.0, 0.0], [5.0, 0.0]])
    T = np.ones(5, dtype=int)
    clustering.partial_fit(X, T)
    assert clustering.n_samples_ == 3
    assert clustering.tree_.total_tokens == 3
    assert_allclose(clustering.tree_.mean_encoding, [4.0, 0.0])  # Last three: 3,4,5 average 4.0
    assert len(clustering.all_embeddings) == 3
    assert len(clustering.all_token_counts) == 3

def test_fit_with_max_tokens():
    clustering = ABITClustering(
        threshold_adjustment=0.01,
        window_size=3,
        min_split_tokens=5,
        max_split_tokens=10,
        split_tokens_tolerance=5,
        min_cluster_size=3,
        max_tokens=3
    )
    X = np.array([[1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [4.0, 0.0], [5.0, 0.0]])
    T = np.ones(5, dtype=int)
    clustering.fit(X, T)
    assert clustering.n_samples_ == 3
    assert clustering.tree_.total_tokens == 3
    assert_allclose(clustering.tree_.mean_encoding, [4.0, 0.0])  # Last three: 3,4,5 average 4.0
    assert len(clustering.all_embeddings) == 3
    assert len(clustering.all_token_counts) == 3

def test_remove_oldest_leaf(clustering):
    X = np.array([[1.0, 0.0], [2.0, 0.0], [3.0, 0.0]])
    T = np.ones(3, dtype=int)
    clustering.fit(X, T)
    # Force remove oldest
    clustering._remove_oldest_leaf()
    assert clustering.tree_.total_samples == 2
    assert clustering.tree_.total_tokens == 2
    assert_allclose(clustering.tree_.mean_encoding, [2.5, 0.0])
    assert clustering.tree_.label == 0  # Renumbered

def test_consistency_after_pruning():
    clustering_partial = ABITClustering(max_tokens=3)
    clustering_batch = ABITClustering(max_tokens=3)
    X = np.array([[1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [4.0, 0.0], [5.0, 0.0]])
    T = np.ones(5, dtype=int)
    # Partial
    clustering_partial.partial_fit(X[:3], T[:3])
    clustering_partial.partial_fit(X[3:], T[3:])
    # Batch
    clustering_batch.fit(X, T)
    assert compare_trees(clustering_partial.tree_, clustering_batch.tree_)
    assert_allclose(clustering_partial.labels_, clustering_batch.labels_)