"""
epe_maria: Symbolic audit framework for model divergence and integrity.

Available functions:
- phi(f, g, domain=None): Structural divergence
- delta_phi(f, g, domain=None): Rate divergence
- phi_star(f, g, alpha=0.5, beta=0.5, domain=None): Fusion metric
- drift(f, g, domain=None): Directional drift
- curvature(f, domain=None): Average curvature
"""

import numpy as np
from epe_maria.utils import to_coeffs, robust_derivative
from epe_maria.core import normalize_coeffs, MetricConfig

# Structural divergence
def phi(f, g, domain=(-1, 1), basis='chebyshev', normalize=True, config=None):
    """
    Structural divergence between two functions f and g.
    """
    try:
        if config:
            domain = config.domain
            basis = config.basis
            normalize = config.normalize

        coeffs_f = to_coeffs(f, domain, basis)
        coeffs_g = to_coeffs(g, domain, basis)

        if normalize:
            coeffs_f = normalize_coeffs(coeffs_f)
            coeffs_g = normalize_coeffs(coeffs_g)

        max_len = max(len(coeffs_f), len(coeffs_g))
        coeffs_f = np.pad(coeffs_f, (0, max_len - len(coeffs_f)))
        coeffs_g = np.pad(coeffs_g, (0, max_len - len(coeffs_g)))

        return np.linalg.norm(coeffs_f - coeffs_g, ord=2)

    except Exception as e:
        raise RuntimeError(f"phi() failed: {e}")

# Rate divergence
def delta_phi(f, g, domain=(-1, 1), basis='chebyshev', normalize=True, config=None):
    """
    Rate divergence between two functions f and g.
    Computes phi() on their derivatives.
    """
    try:
        if config:
            domain = config.domain
            basis = config.basis
            normalize = config.normalize

        df = robust_derivative(f, domain)
        dg = robust_derivative(g, domain)

        return phi(df, dg, domain=domain, basis=basis, normalize=normalize)

    except Exception as e:
        raise RuntimeError(f"delta_phi() failed: {e}")

# Import remaining metrics
from .monitor import drift, curvature

# Placeholder for phi_star (to be implemented next)
def phi_star(f, g, alpha=0.5, beta=0.5, domain=(-1, 1), basis='chebyshev', normalize=True, config=None):
    """
    Fusion metric combining structural and rate divergence.
    """
    if config:
        domain = config.domain
        basis = config.basis
        normalize = config.normalize
        alpha = config.alpha
        beta = config.beta

    s = phi(f, g, domain=domain, basis=basis, normalize=normalize)
    r = delta_phi(f, g, domain=domain, basis=basis, normalize=normalize)
    return alpha * s + beta * r

def drift(f, g, domain=(-1, 1), resolution=1000):
    """
    Directional drift between f and g over a domain.
    Positive = f > g on average, Negative = f < g
    
    Parameters:
    - f, g: callables or symbolic expressions
    - domain: tuple (min, max)
    - resolution: number of points to sample
    
    Returns:
    - Mean signed difference: avg(f(x) - g(x))
    """
    try:
        x = np.linspace(domain[0], domain[1], resolution)

        # Evaluate callables or lambdify symbolic
        if callable(f):
            fx = f(x)
        else:
            from sympy import lambdify
            fx = lambdify('x', f, 'numpy')(x)

        if callable(g):
            gx = g(x)
        else:
            from sympy import lambdify
            gx = lambdify('x', g, 'numpy')(x)

        return np.mean(fx - gx)

    except Exception as e:
        raise RuntimeError(f"drift() failed: {e}")
    
def curvature(f, domain=(-1, 1), resolution=1000, method='symbolic'):
    """
    Average curvature of f over a domain.
    Defined as mean of second derivative magnitude.
    
    Parameters:
    - f: callable or symbolic expression
    - domain: tuple (min, max)
    - resolution: number of points to sample
    - method: 'symbolic' or 'numeric'
    
    Returns:
    - Mean absolute second derivative
    """
    try:
        x = np.linspace(domain[0], domain[1], resolution)

        if method == 'symbolic':
            from sympy import lambdify
            f2 = f.diff().diff() if hasattr(f, 'diff') else None
            if f2 is None:
                raise TypeError("Symbolic input required for symbolic curvature")
            f2x = lambdify('x', f2, 'numpy')(x)

        else:
            if callable(f):
                y = f(x)
            else:
                from sympy import lambdify
                y = lambdify('x', f, 'numpy')(x)
            f2x = np.gradient(np.gradient(y, x), x)

        return np.mean(np.abs(f2x))

    except Exception as e:
        raise RuntimeError(f"curvature() failed: {e}")


__all__ = ["phi", "delta_phi", "phi_star", "drift", "curvature"]
