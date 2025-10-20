# src/metrics/utils/knn.py

import numpy as np
from sklearn.neighbors import KDTree, BallTree

from ...exceptions import UnsupportedMetricError


class KNNFinder:
    """
    Lightweight wrapper to perform exact k-NN queries over a static reference set.
    Backends: 'kd_tree', 'ball_tree', 'brute' (euclidean).
    """

    def __init__(self, data: np.ndarray, leaf_size: int = 40, tree_type: str = 'kd_tree'):
        """
        Parameters
        ----------
        data : np.ndarray of shape (m, d)
            Reference data (not modified in-place).
        leaf_size : int, default=40
            Leaf size for tree-based backends.
        tree_type : {'kd_tree', 'ball_tree', 'brute'}, default='kd_tree'
            Backend to use. 'brute' computes pairwise euclidean distances on the fly.
        """
        self.data = np.asarray(data)
        self.tree_type = str(tree_type).lower()

        if self.tree_type == 'kd_tree':
            self.tree = KDTree(self.data, leaf_size=leaf_size)
        elif self.tree_type == 'ball_tree':
            self.tree = BallTree(self.data, leaf_size=leaf_size)
        elif self.tree_type == 'brute':
            # No pre-built tree needed; keep None and compute on query.
            self.tree = None
        else:
            raise UnsupportedMetricError(
                "tree_type debe ser 'kd_tree', 'ball_tree' o 'brute'"
            )

    def query(self, points: np.ndarray, k: int = 5) -> np.ndarray:
        """
        Parameters
        ----------
        points : np.ndarray of shape (q, d)
            Query points (not modified in-place).
        k : int, default=5
            Number of nearest neighbors to retrieve.

        Returns
        -------
        indices : np.ndarray of shape (q, k), dtype=int64
            For each query row, indices of its k nearest neighbors in 'data'.
        """
        Q = np.asarray(points)

        if self.tree_type in ('kd_tree', 'ball_tree'):
            # scikit-learn guarantees neighbors ordered by increasing distance
            _, indices = self.tree.query(Q, k=k)
            return indices

        # 'brute' backend (euclidean only)
        # Compute squared distances to avoid unnecessary sqrt
        # dist^2 = ||a||^2 + ||b||^2 - 2 a·b
        # Shapes: Q (q,d), D (m,d)
        D = self.data
        # Norms
        q_norm2 = np.einsum('ij,ij->i', Q, Q)  # (q,)
        d_norm2 = np.einsum('ij,ij->i', D, D)  # (m,)
        # Gram matrix
        G = Q @ D.T  # (q, m)
        d2 = q_norm2[:, None] + d_norm2[None, :] - 2.0 * G  # (q, m)
        # Argpartition for top-k (ascending distances)
        idx = np.argpartition(d2, kth=k-1, axis=1)[:, :k]  # (q, k) unordered slice
        # Order the k candidates by actual distance
        row_idx = np.arange(idx.shape[0])[:, None]
        idx_sorted = idx[row_idx, np.argsort(d2[row_idx, idx], axis=1)]
        return idx_sorted
