from typing import List
from dataclasses import dataclass
import numpy as np

@dataclass
class TreeNode:
    label: int
    mean_encoding: np.ndarray = None
    total_tokens: int = 0
    total_samples: int = 0
    children: List['TreeNode'] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []

def _find_split_indices(similarities: List[float], threshold: float) -> List[int]:
    """Find indices where splits should occur based on similarity scores."""
    return [idx + 1 for idx, score in enumerate(similarities) if score < threshold]

class ABITClustering:
    """
    Adaptive Binary Iterative Threshold Clustering
    """
    def __init__(
            self,
            threshold_adjustment: float = 0.01,
            window_size: int = 3,
            min_split_tokens: int = 5,
            max_split_tokens: int = 10,
            split_tokens_tolerance: int = 5,
            min_cluster_size: int = 3,
            max_tokens: int = None,
            rebuild_frequency: int = 1
    ):
        self.threshold_adjustment = threshold_adjustment
        self.window_size = window_size
        self.min_split_tokens = min_split_tokens
        self.max_split_tokens = max_split_tokens
        self.split_tokens_tolerance = split_tokens_tolerance
        self.min_cluster_size = min_cluster_size
        self.max_tokens = max_tokens if max_tokens is not None else float('inf')
        self.rebuild_frequency = rebuild_frequency
        self.partial_fit_count = 0
        self.all_embeddings: List[np.ndarray] = []
        self.all_token_counts: List[int] = []
        self.labels_ = None
        self.tree_ = None
        self.n_samples_ = 0

    def fit(self, X: np.ndarray, T: np.ndarray):
        """Full batch fitting: reset state and build the tree."""
        self.all_embeddings = list(X)
        self.all_token_counts = T.tolist()
        self.partial_fit_count = 0
        self._build_tree()

    def partial_fit(self, X: np.ndarray, T: np.ndarray):
        """Incremental fitting: append new data and rebuild the tree."""
        if X.shape[0] == 0:
            if self.labels_ is None:
                self.labels_ = np.array([], dtype=int)
                self.tree_ = None
                self.n_samples_ = 0
            return
        self.all_embeddings.extend(list(X))
        self.all_token_counts.extend(T.tolist())
        self.partial_fit_count += 1
        if self.partial_fit_count % self.rebuild_frequency == 0:
            self._build_tree()
        else:
            # Quick append without full rebuild: add as new leaves (approximate)
            new_n = X.shape[0]
            new_labels = np.arange(self.n_samples_, self.n_samples_ + new_n)
            if self.labels_ is None:
                self.labels_ = new_labels
            else:
                self.labels_ = np.append(self.labels_, new_labels)
            new_tree_nodes = [
                TreeNode(
                    label=int(new_labels[i]),
                    mean_encoding=X[i],
                    total_tokens=T[i],
                    total_samples=1
                ) for i in range(new_n)
            ]
            if self.tree_ is None:
                if new_n == 1:
                    self.tree_ = new_tree_nodes[0]
                else:
                    # Create temporary root for new batch
                    total_samples = sum(n.total_samples for n in new_tree_nodes)
                    mean_encoding = np.sum([n.mean_encoding * n.total_samples for n in new_tree_nodes], axis=0) / total_samples
                    total_tokens = sum(n.total_tokens for n in new_tree_nodes)
                    self.tree_ = TreeNode(
                        label=int(new_labels[0]),
                        mean_encoding=mean_encoding,
                        total_tokens=total_tokens,
                        total_samples=total_samples,
                        children=new_tree_nodes
                    )
            else:
                # Append new nodes as siblings under root (approximate, consistency only after rebuild)
                self.tree_.children.extend(new_tree_nodes)
                self.tree_.total_samples += sum(n.total_samples for n in new_tree_nodes)
                self.tree_.total_tokens += sum(n.total_tokens for n in new_tree_nodes)
                self.tree_.mean_encoding = (self.tree_.mean_encoding * (self.tree_.total_samples - sum(n.total_samples for n in new_tree_nodes)) + np.sum([n.mean_encoding * n.total_samples for n in new_tree_nodes], axis=0)) / self.tree_.total_samples
            self.n_samples_ += new_n
            # Enforce max_tokens approximately
            while self.tree_ and self.tree_.total_tokens > self.max_tokens:
                self._remove_oldest_leaf()
                self.all_embeddings.pop(0)
                self.all_token_counts.pop(0)
                self.n_samples_ -= 1
                self.labels_ = np.delete(self.labels_, 0)

    def _build_tree(self):
        """Build the hierarchical tree from all accumulated data."""
        self.n_samples_ = len(self.all_embeddings)
        if self.n_samples_ == 0:
            self.tree_ = None
            self.labels_ = np.array([], dtype=int)
            return

        X = np.vstack(self.all_embeddings)
        T = np.array(self.all_token_counts)
        self.labels_ = np.arange(self.n_samples_)
        clusters = [[i] for i in range(self.n_samples_)]
        tree_nodes = [
            TreeNode(
                label=int(i),
                mean_encoding=X[i],
                total_tokens=T[i],
                total_samples=1
            ) for i in range(self.n_samples_)
        ]

        while len(clusters) > 1:
            cluster_encodings = [node.mean_encoding for node in tree_nodes]
            cluster_token_counts = [node.total_tokens for node in tree_nodes]
            similarities = self._rolling_similarity_scores(cluster_encodings)
            calculated_threshold = self._find_optimal_threshold(cluster_token_counts, similarities)
            split_indices = [0] + _find_split_indices(similarities, calculated_threshold) + [len(clusters)]
            cumulative_token_counts = np.cumsum([0] + cluster_token_counts)
            i = 1
            while i < len(split_indices) - 1:
                start = split_indices[i - 1]
                end = split_indices[i]
                size = cumulative_token_counts[end] - cumulative_token_counts[start]
                if size < self.min_cluster_size:
                    del split_indices[i]
                else:
                    i += 1
            if len(split_indices) > 1:
                last_start = split_indices[-2]
                last_end = split_indices[-1]
                last_size = cumulative_token_counts[last_end] - cumulative_token_counts[last_start]
                if last_size < self.min_cluster_size and len(split_indices) > 2:
                    del split_indices[-2]
            parent_cluster_ranges = list(zip(split_indices[:-1], split_indices[1:]))
            new_clusters = []
            new_tree_nodes = []
            merged = False
            for start_idx, end_idx in parent_cluster_ranges:
                if end_idx - start_idx > 1:
                    merged = True
                    parent_cluster = [item for sublist in clusters[start_idx:end_idx] for item in sublist]
                    parent_label = self.labels_[parent_cluster[0]]
                    self.labels_[parent_cluster] = parent_label
                    children = tree_nodes[start_idx:end_idx]
                    total_samples = sum(c.total_samples for c in children)
                    mean_encoding = np.sum([c.mean_encoding * c.total_samples for c in children], axis=0) / total_samples
                    total_tokens = sum(c.total_tokens for c in children)
                    parent_node = TreeNode(
                        label=int(parent_label),
                        mean_encoding=mean_encoding,
                        total_tokens=total_tokens,
                        total_samples=total_samples,
                        children=children
                    )
                    new_clusters.append(parent_cluster)
                    new_tree_nodes.append(parent_node)
                else:
                    new_clusters.append(clusters[start_idx])
                    new_tree_nodes.append(tree_nodes[start_idx])
            if not merged:
                # No new parent clusters identified, create final root cluster
                root_cluster = [item for sublist in new_clusters for item in sublist]
                root_label = self.labels_[root_cluster[0]]
                self.labels_[root_cluster] = root_label
                total_samples = sum(c.total_samples for c in new_tree_nodes)
                mean_encoding = np.sum([c.mean_encoding * c.total_samples for c in new_tree_nodes], axis=0) / total_samples if total_samples > 0 else np.zeros_like(X[0])
                total_tokens = sum(c.total_tokens for c in new_tree_nodes)
                self.tree_ = TreeNode(
                    label=int(root_label),
                    mean_encoding=mean_encoding,
                    total_tokens=total_tokens,
                    total_samples=total_samples,
                    children=new_tree_nodes
                )
                break
            else:
                clusters = new_clusters
                tree_nodes = new_tree_nodes

        if len(clusters) == 1:
            self.tree_ = tree_nodes[0]

        # Enforce max_tokens by removing oldest leaves if necessary
        while self.tree_ and self.tree_.total_tokens > self.max_tokens:
            self._remove_oldest_leaf()
            self.all_embeddings.pop(0)
            self.all_token_counts.pop(0)
            self.n_samples_ -= 1
            self.labels_ = np.delete(self.labels_, 0)

    def _remove_oldest_leaf(self):
        if not self.tree_:
            return
        if not self.tree_.children:
            self.tree_ = None
            return

        def remove_and_update(node: TreeNode) -> TreeNode:
            if not node.children:
                return None
            node.children[0] = remove_and_update(node.children[0])
            if node.children[0] is None:
                del node.children[0]
            if not node.children:
                return None
            # Update stats
            node.total_samples = sum(c.total_samples for c in node.children)
            node.total_tokens = sum(c.total_tokens for c in node.children)
            node.mean_encoding = np.sum([c.mean_encoding * c.total_samples for c in node.children], axis=0) / node.total_samples
            # Collapse if single child
            if len(node.children) == 1:
                return node.children[0]
            return node

        self.tree_ = remove_and_update(self.tree_)

        # Renumber labels in the tree (subtract 1 since removing the smallest index)
        def renumber(node: TreeNode):
            if not node:
                return
            if not node.children:
                node.label -= 1
            else:
                for child in node.children:
                    renumber(child)
                node.label = min(child.label for child in node.children)

        renumber(self.tree_)

    def _rolling_similarity_scores(self, encoded_docs: List[np.ndarray]) -> List[float]:
        """Calculate rolling similarity scores."""
        encoded_docs = np.asarray(encoded_docs, dtype=float)
        if len(encoded_docs) < 2:
            return []
        cumsum = np.cumsum(encoded_docs, axis=0)
        similarities = []
        for idx in range(1, len(encoded_docs)):
            window_start = max(0, idx - self.window_size)
            length = idx - window_start
            if window_start == 0:
                sum_context = cumsum[idx - 1]
            else:
                sum_context = cumsum[idx - 1] - cumsum[window_start - 1]
            cumulative_context = sum_context / length
            similarity = np.dot(cumulative_context, encoded_docs[idx]) / (
                np.linalg.norm(cumulative_context) * np.linalg.norm(encoded_docs[idx]) + 1e-10
            )
            similarities.append(similarity)
        return similarities

    def _find_optimal_threshold(self, token_counts: List[int], similarity_scores: List[float]) -> float:
        """Find the optimal threshold for splitting clusters."""
        if not similarity_scores:
            return 0.0
        cumulative_token_counts = np.cumsum([0] + token_counts)
        p25, p75 = np.percentile(similarity_scores, [25, 75])
        low = max(0.0, float(p25))
        high = min(1.0, float(p75))
        calculated_threshold = 0.0
        for _ in range(50):  # Reduced max iterations from 100 to 50
            calculated_threshold = (low + high) / 2
            split_indices = _find_split_indices(similarity_scores, calculated_threshold)
            split_token_counts = [
                cumulative_token_counts[end] - cumulative_token_counts[start]
                for start, end in zip([0] + split_indices, split_indices + [len(token_counts)])
            ]
            if not split_token_counts:
                high = calculated_threshold - self.threshold_adjustment
                continue
            min_tokens = np.min(split_token_counts)
            median_tokens = np.median(split_token_counts)
            if (min_tokens >= self.min_split_tokens - self.split_tokens_tolerance and
                median_tokens <= self.max_split_tokens + self.split_tokens_tolerance):
                break
            elif min_tokens < self.min_split_tokens:
                high = calculated_threshold - self.threshold_adjustment  # Lower threshold for larger clusters
            else:
                low = calculated_threshold + self.threshold_adjustment  # Higher threshold for smaller clusters
            if abs(high - low) < 1e-5:
                break
        return calculated_threshold