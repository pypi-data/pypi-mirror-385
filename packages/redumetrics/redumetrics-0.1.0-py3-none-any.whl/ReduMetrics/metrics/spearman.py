import numpy as np
from scipy.stats import rankdata

from ReduMetrics.exceptions import (
    InvalidShapeError,
    InconsistentDimensionsError,
    InvalidKError,
    NaNInputError,
)

def _check_inputs_spearman(X_high: np.ndarray, X_low: np.ndarray, P: int) -> int:
    if X_high.ndim != 2 or X_low.ndim != 2:
        raise InvalidShapeError("X_high y X_low deben ser matrices 2D (m, d)/(m, r).")
    m_high, _ = X_high.shape
    m_low,  _ = X_low.shape
    if m_high != m_low:
        raise InconsistentDimensionsError(
            f"Número de muestras incompatible: X_high tiene {m_high} y X_low {m_low}."
        )
    if m_high < 2:
        raise InvalidKError("Se requieren al menos 2 muestras para formar pares distintos.")
    if P is None or P <= 0:
        raise InvalidKError(f"P debe ser un entero positivo (P={P}).")
    if not (np.isfinite(X_high).all() and np.isfinite(X_low).all()):
        raise NaNInputError("Se han detectado valores no finitos (NaN/Inf) en la entrada.")
    return m_high

def _sample_distinct_pairs(m: int, P: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """
    Devuelve dos arrays (P,) con índices i, j tales que i != j, sin rechazos.
    i ~ U{0..m-1}; j ~ U{0..m-2} remapeado para saltar i.
    """
    i = rng.integers(m, size=P)
    j = rng.integers(m - 1, size=P)
    j = j + (j >= i)  # desplaza los >= i
    return i, j

def spearman_correlation(
    X_high: np.ndarray,
    X_low: np.ndarray,
    P: int = 10000,
    random_state: int | None = None
) -> float:
    """
    Spearman rank-order correlation entre distancias muestreadas en alto y bajo.
    """
    Xh = np.asarray(X_high)
    Xl = np.asarray(X_low)
    m = _check_inputs_spearman(Xh, Xl, P)

    rng = np.random.default_rng(random_state)
    i, j = _sample_distinct_pairs(m, P, rng)

    # Distancias euclídeas cuadradas (mantienen el orden → mismos rangos)
    d_high_sq = np.sum((Xh[i] - Xh[j]) ** 2, axis=1)
    d_low_sq  = np.sum((Xl[i] - Xl[j]) ** 2, axis=1)

    # Rangos con manejo de empates (promedio)
    r_high = rankdata(d_high_sq, method='average')
    r_low  = rankdata(d_low_sq,  method='average')

    # Correlación de Spearman = Pearson(r_high, r_low)
    r_high_centered = r_high - r_high.mean()
    r_low_centered  = r_low  - r_low.mean()
    num = np.dot(r_high_centered, r_low_centered)
    den = np.sqrt(np.dot(r_high_centered, r_high_centered) * np.dot(r_low_centered, r_low_centered))

    if den == 0.0:
        # Degenerado (varianza cero en uno o ambos rangos): devolvemos 0.0
        return 0.0

    return float(num / den)
