# ReduMetrics

**ReduMetrics** is a lightweight library to evaluate the quality of dimensionality reductions, independent of the projection method (PCA, t-SNE, UMAP, …).  
It provides five complementary metrics:

| Metric | Meaning | Range |
|:--------|:---------|:------|
| **ULSE** | Local neighborhood preservation | [0, 1] |
| **RTA** | Random triplet accuracy | [0, 1] |
| **Spearman** | Rank correlation of sampled distances | [−1, 1] |
| **k-NCP** | *k*-nearest class preservation | [0, 1] |
| **CDC** | Centroid distance correlation | [−1, 1] |

Pure functions — NumPy in/out.  
Tested with **Python 3.9 – 3.12**.  

**Dependencies:**  
`numpy`, `scipy`, `scikit-learn`  

---

## Installation

```bash
pip install ReduMetrics
```
---
## Usage

```import numpy as np
from ReduMetrics.metrics.ulse import ulse_score
from ReduMetrics.metrics.rta import rta_score
from ReduMetrics.metrics.spearman import spearman_correlation
from ReduMetrics.metrics.k_ncp import kncp_score
from ReduMetrics.metrics.cdc import cdc_score

# X_high: (m, n) high-dim data, X_low: (m, r) embedding, labels: (m,)
rng = np.random.default_rng(42)
m, n, r = 1000, 50, 2
X_high = rng.normal(size=(m, n))
X_low  = X_high[:, :r]          # toy projection
labels = rng.integers(0, 10, size=m)

# Metrics
ulse = ulse_score(X_high, X_low, k=10)                         # -> [0, 1]
rta  = rta_score (X_high, X_low, T=10000, random_state=0)      # -> [0, 1]
rho  = spearman_correlation(X_high, X_low, P=20000, random_state=0)  # -> [-1, 1]
kncp = kncp_score(X_high, X_low, labels)                       # -> [0, 1]
cdc  = cdc_score (X_high, X_low, labels)                       # -> [-1, 1]

print(ulse, rta, rho, kncp, cdc)
