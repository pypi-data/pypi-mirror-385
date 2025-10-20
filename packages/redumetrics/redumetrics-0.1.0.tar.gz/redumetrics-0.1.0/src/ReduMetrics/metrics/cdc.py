import numpy as np
from scipy.stats import rankdata
from sklearn.metrics import pairwise_distances

from ReduMetrics.exceptions import (
    InvalidShapeError,
    InconsistentDimensionsError,
    InvalidKError,
    NaNInputError,
)

def _check_inputs_cdc(X_high: np.ndarray, X_low: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, int]:
    # Formas 2D y mismo m
    if X_high.ndim != 2 or X_low.ndim != 2:
        raise InvalidShapeError("X_high y X_low deben ser matrices 2D (m, d)/(m, r).")
    m_high, _ = X_high.shape
    m_low,  _ = X_low.shape
    if m_high != m_low:
        raise InconsistentDimensionsError(
            f"Número de muestras incompatible: X_high tiene {m_high} y X_low {m_low}."
        )
    # labels 1D y longitud m
    lab = np.asarray(labels)
    if lab.ndim != 1 or lab.shape[0] != m_high:
        raise InvalidShapeError(f"labels debe ser un vector de longitud m={m_high}.")
    # Datos finitos
    if not (np.isfinite(X_high).all() and np.isfinite(X_low).all()):
        raise NaNInputError("Se han detectado valores no finitos (NaN/Inf) en la entrada de datos.")
    # Al menos 2 clases
    classes = np.unique(lab)
    C = classes.size
    if C < 2:
        raise InvalidKError("Se requieren al menos 2 clases para CDC.")
    return classes, C

def cdc_score(X_high: np.ndarray, X_low: np.ndarray, labels: np.ndarray) -> float:
    """
    Centroid Distance Correlation (CDC): Spearman entre distancias entre centroides
    de clase en alto y bajo.
    """
    Xh = np.asarray(X_high)
    Xl = np.asarray(X_low)
    classes, C = _check_inputs_cdc(Xh, Xl, labels)

    # Centroides por clase (mismo orden en ambos espacios)
    cent_high = np.vstack([Xh[labels == c].mean(axis=0) for c in classes])
    cent_low  = np.vstack([Xl[labels == c].mean(axis=0) for c in classes])

    # Distancias entre centroides (euclídeas por defecto)
    Dn = pairwise_distances(cent_high)  # (C, C)
    Dr = pairwise_distances(cent_low)   # (C, C)

    # Vectorizo el triángulo superior k=1 (pares c1<c2)
    iu = np.triu_indices(C, k=1)
    dn = Dn[iu]
    dr = Dr[iu]

    # Rangos con manejo de empates (promedio)
    rn = rankdata(dn, method='average')
    rr = rankdata(dr, method='average')

    # Spearman = Pearson(rn, rr)
    rn_c = rn - rn.mean()
    rr_c = rr - rr.mean()
    num = float(np.dot(rn_c, rr_c))
    den = float(np.sqrt(np.dot(rn_c, rn_c) * np.dot(rr_c, rr_c)))

    # Casos degenerados: un solo par (C=2) o todas las distancias iguales ⇒ den=0
    if den == 0.0:
        return 0.0

    return num / den

# Alias opcional si quieres mantener el nombre anterior:
# centroid_distance_correlation = cdc_score
