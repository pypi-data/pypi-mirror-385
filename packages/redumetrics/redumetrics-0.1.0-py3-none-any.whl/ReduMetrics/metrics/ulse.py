import numpy as np

from ReduMetrics.metrics.utils.knn import KNNFinder
from sklearn.neighbors import NearestNeighbors

from ReduMetrics.exceptions import (
    InvalidShapeError,
    InconsistentDimensionsError,
    InvalidKError,
    NaNInputError,
)

def _check_inputs(X_high: np.ndarray, X_low: np.ndarray, k: int) -> int:
    if X_high.ndim != 2 or X_low.ndim != 2:
        raise InvalidShapeError("X_high y X_low deben ser matrices 2D (m, d)/(m, r).")

    m_high, _ = X_high.shape
    m_low, _ = X_low.shape
    if m_high != m_low:
        raise InconsistentDimensionsError(
            f"Número de muestras incompatible: X_high tiene {m_high} y X_low {m_low}."
        )
    m = m_high

    if not (1 <= k < m):
        raise InvalidKError(f"k debe cumplir 1 <= k < m (k={k}, m={m}).")

    if not (np.isfinite(X_high).all() and np.isfinite(X_low).all()):
        raise NaNInputError("Se han detectado valores no finitos (NaN/Inf) en la entrada.")

    return m

def _drop_self_indices(neighs: np.ndarray) -> np.ndarray:
    """
    Dado un array (m, k+1) de índices de vecinos (incluyendo autovecino),
    elimina i de la fila i y devuelve las primeras k posiciones restantes.
    Asume que 'i' aparece exactamente una vez por fila.
    """
    m, kp1 = neighs.shape
    k = kp1 - 1
    out = np.empty((m, k), dtype=neighs.dtype)
    for i in range(m):
        row = neighs[i]
        # Encontrar posición del autovecino i en la fila
        mask = row != i
        # Extrae los primeros k distintos de i preservando orden
        out[i] = row[mask][:k]
    return out

def ulse_score(X_high: np.ndarray, X_low: np.ndarray, k: int = 5) -> float:
    """
    Compute the Unsupervised Local Structure Evaluation (ULSE) score.

    Parameters
    ----------
    X_high : array-like, shape (m, n)
        High-dimensional data (m samples, n features).
    X_low : array-like, shape (m, r)
        Low-dimensional embedding (m samples, r features).
    k : int, default=5
        Number of nearest neighbors to consider.

    Returns
    -------
    ulse : float
        The average proportion of preserved local neighbors in [0, 1].
    """
    Xh = np.asarray(X_high)
    Xl = np.asarray(X_low)

    m = _check_inputs(Xh, Xl, k)

    # Índices para cada espacio
    knn_high = KNNFinder(Xh)   
    knn_low = KNNFinder(Xl)

    # Si consultamos sobre el mismo conjunto que indexa el KNNFinder,
    # pedimos k+1 vecinos y eliminamos el autovecino.
    neighs_high = knn_high.query(Xh, k=k + 1)
    neighs_high = _drop_self_indices(neighs_high)

    neighs_low = knn_low.query(Xl, k=k + 1)
    neighs_low = _drop_self_indices(neighs_low)

    # ULSE: promedio de intersección relativa
    preserved = 0.0
    for i in range(m):
        set_high = set(neighs_high[i])
        # Intersección en O(k)
        common = sum(1 for idx in neighs_low[i] if idx in set_high)
        preserved += common / k

    return float(preserved / m)

def ulse_score_sklearn(X_high: np.ndarray, X_low: np.ndarray, k: int = 5) -> float:
    """
    Compute the ULSE score using scikit-learn's NearestNeighbors.

    Parameters
    ----------
    X_high : array-like, shape (m, n)
        High-dimensional data (m samples, n features).
    X_low : array-like, shape (m, r)
        Low-dimensional embedding (m samples, r features).
    k : int, default=5
        Number of nearest neighbors to consider.

    Returns
    -------
    ulse : float
        The average proportion of preserved local neighbors.
    """
    m = X_high.shape[0]

    # Obtener los k vecinos más cercanos (sin contar el punto mismo)
    nn_high = NearestNeighbors(n_neighbors=k+1).fit(X_high)
    nn_low = NearestNeighbors(n_neighbors=k+1).fit(X_low)

    neighs_high = nn_high.kneighbors(X_high, return_distance=False)[:, 1:]
    neighs_low = nn_low.kneighbors(X_low, return_distance=False)[:, 1:]

    # Calcular la proporción de vecinos preservados
    preserved = 0.0
    for i in range(m):
        set_high = set(neighs_high[i])
        set_low = set(neighs_low[i])
        preserved += len(set_high.intersection(set_low)) / k

    return preserved / m