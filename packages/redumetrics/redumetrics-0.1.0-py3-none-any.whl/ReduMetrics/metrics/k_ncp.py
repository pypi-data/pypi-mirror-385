import numpy as np
from sklearn.metrics import pairwise_distances

from ReduMetrics.exceptions import (
    InvalidShapeError,
    InconsistentDimensionsError,
    InvalidKError,
    NaNInputError,
)

def _check_inputs_kncp(X_high: np.ndarray, X_low: np.ndarray, labels: np.ndarray) -> tuple[int, np.ndarray]:
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
    C = classes.shape[0]
    if C < 2:
        raise InvalidKError("Se requieren al menos 2 clases para k-NCP.")
    return C, classes

def kncp_score(X_high: np.ndarray, X_low: np.ndarray, labels: np.ndarray, k: int | None = None) -> float:
    """
    k-Nearest Class Preservation (k-NCP): promedio, sobre clases, de la fracción de
    vecinos de clase preservados entre alto y bajo.
    """
    Xh = np.asarray(X_high)
    Xl = np.asarray(X_low)
    C, classes = _check_inputs_kncp(Xh, Xl, labels)

    if k is None:
        k_eff = max(1, min((C + 2) // 4, C - 1))
    else:
        if not isinstance(k, (int, np.integer)):
            raise InvalidKError("k debe ser un entero.")
        if not (1 <= k < C):
            raise InvalidKError(f"k debe estar en [1, {C-1}].")
        k_eff = int(k)

    # Centroides por clase (en el mismo orden que 'classes')
    cent_high = np.vstack([Xh[labels == c].mean(axis=0) for c in classes])
    cent_low  = np.vstack([Xl[labels == c].mean(axis=0)  for c in classes])

    # Distancias entre centroides (euclídeas por defecto)
    Dn = pairwise_distances(cent_high)  # (C, C)
    Dr = pairwise_distances(cent_low)   # (C, C)

    # Excluir la clase propia de la vecindad
    np.fill_diagonal(Dn, np.inf)
    np.fill_diagonal(Dr, np.inf)

    # Selección de los k vecinos más cercanos sin ordenar todo (O(C^2))
    # Para cada fila, cogemos los k índices con menor distancia
    # (no necesitamos orden total para la intersección)
    nh = np.argpartition(Dn, kth=k_eff-1, axis=1)[:, :k_eff]  # (C, k)
    nl = np.argpartition(Dr, kth=k_eff-1, axis=1)[:, :k_eff]  # (C, k)

    # Fracción de solape por clase y media
    preserved = 0.0
    for idx in range(C):
        # set para O(1) en pertenencia
        set_h = set(nh[idx])
        common = sum(1 for j in nl[idx] if j in set_h)
        preserved += common / k_eff

    return float(preserved / C)

# Si quieres mantener el nombre original como alias público:
# k_nearest_class_preservation = kncp_score
