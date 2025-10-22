import numpy as np

class MetricConfig:
    def __init__(self, domain=(-1, 1), basis='chebyshev', 
                 normalize=True, alpha=0.5, beta=0.5):
        self.domain = domain
        self.basis = basis
        self.normalize = normalize
        self.alpha = alpha
        self.beta = beta

def normalize_coeffs(coeffs, method='l2'):
    """
    Normalize coefficient vector for scale invariance.
    Converts symbolic types to native floats before applying norms.
    """
    coeffs = np.array(coeffs, dtype=np.float64)  # Ensures compatibility with NumPy

    if method == 'l2':
        norm = np.linalg.norm(coeffs)
        return coeffs / norm if norm > 0 else coeffs

    elif method == 'max':
        max_val = np.max(np.abs(coeffs))
        return coeffs / max_val if max_val > 0 else coeffs

    elif method == 'none':
        return coeffs

    else:
        raise ValueError(f"Unsupported normalization method: {method}")
