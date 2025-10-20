
import numpy as np

from ReduMetrics.exceptions import (
    InvalidShapeError,
    InconsistentDimensionsError,
    InvalidKError,      # reutilizamos para validar T (si prefieres, creamos InvalidTError)
    NaNInputError,
)

def _check_inputs_rta(X_high: np.ndarray, X_low: np.ndarray, T: int) -> int:
    if X_high.ndim != 2 or X_low.ndim != 2:
        raise InvalidShapeError("X_high y X_low deben ser matrices 2D (m, d)/(m, r).")
    m_high, _ = X_high.shape
    m_low,  _ = X_low.shape
    if m_high != m_low:
        raise InconsistentDimensionsError(
            f"Número de muestras incompatible: X_high tiene {m_high} y X_low {m_low}."
        )
    if m_high < 3:
        raise InvalidKError("Se requieren al menos 3 muestras para formar tríos distintos.")
    if T is None or T <= 0:
        raise InvalidKError(f"T debe ser un entero positivo (T={T}).")
    if not (np.isfinite(X_high).all() and np.isfinite(X_low).all()):
        raise NaNInputError("Se han detectado valores no finitos (NaN/Inf) en la entrada.")
    return m_high

def _sample_distinct_triplets(m: int, T: int, rng: np.random.Generator) -> np.ndarray:
    """
    Devuelve un array (T, 3) con tríos (i,j,l) distintos, sin reintentos ni bucles.
    Estrategia:
      - i ~ U{0..m-1}
      - j ~ U{0..m-2} y se mapea para evitar i
      - l ~ U{0..m-3} y se mapea para evitar i y j
    """
    i = rng.integers(m, size=T)

    j = rng.integers(m - 1, size=T)
    j = j + (j >= i)  # desplaza los >= i

    # Para l, evitamos dos índices (i y j). Mapeamos desde {0..m-3} a {0..m-1}\{i,j}
    a = np.minimum(i, j)
    b = np.maximum(i, j)
    t = rng.integers(m - 2, size=T)

    l = t
    l = l + (l >= a)
    l = l + (l >= b)
    return np.stack([i, j, l], axis=1)

def rta_score(
    X_high: np.ndarray,
    X_low: np.ndarray,
    T: int = 10000,
    random_state: int | None = None
) -> float:
    """
    Random Triplet Accuracy (RTA): fracción de tríos (i, j, l) cuya relación de distancias
    respecto de i se preserva tras la reducción.

    - Empates: un trío con d_ij == d_il en alto se considera preservado solo si
      d'_ij == d'_il en bajo; en otro caso, no se cuenta como preservado.
    """
    Xh = np.asarray(X_high)
    Xl = np.asarray(X_low)
    m = _check_inputs_rta(Xh, Xl, T)

    rng = np.random.default_rng(random_state)
    trip = _sample_distinct_triplets(m, T, rng)
    i = trip[:, 0]
    j = trip[:, 1]
    l = trip[:, 2]

    # Distancias cuadradas (mantienen el orden; evitamos sqrt)
    dh_ij = np.sum((Xh[i] - Xh[j]) ** 2, axis=1)
    dh_il = np.sum((Xh[i] - Xh[l]) ** 2, axis=1)

    dl_ij = np.sum((Xl[i] - Xl[j]) ** 2, axis=1)
    dl_il = np.sum((Xl[i] - Xl[l]) ** 2, axis=1)

    # Preservación si el orden relativo coincide, o si hay empate en ambos espacios
    high_lt = dh_ij < dh_il
    high_gt = dh_ij > dh_il
    high_eq = ~(high_lt | high_gt)  # empate

    low_lt = dl_ij < dl_il
    low_gt = dl_ij > dl_il
    low_eq = ~(low_lt | low_gt)

    preserved = (high_lt & low_lt) | (high_gt & low_gt) | (high_eq & low_eq)
    return float(preserved.mean())
