import numpy as np
from sympy import Expr

def to_coeffs(f, domain=(-1, 1), basis='chebyshev', max_degree=20):
    """
    Convert various function types to coefficient vectors.
    Supports: numpy arrays, callables, SymPy expressions.
    """
    if isinstance(f, np.ndarray):
        return f

    elif callable(f):
        x = np.linspace(domain[0], domain[1], 1000)
        y = f(x)
        return _project_to_basis(x, y, basis, max_degree)

    elif isinstance(f, Expr) and hasattr(f, 'as_poly'):
        poly = f.as_poly()
        coeffs = poly.all_coeffs()[::-1]
        return np.array(coeffs)

    else:
        raise TypeError(f"Unsupported input type: {type(f)}")

def _project_to_basis(x, y, basis='chebyshev', max_degree=20):
    if basis == 'chebyshev':
        return np.polynomial.chebyshev.chebfit(x, y, max_degree)
    elif basis == 'legendre':
        return np.polynomial.legendre.legfit(x, y, max_degree)
    elif basis == 'monomial':
        return np.polyfit(x, y, max_degree)
    else:
        raise ValueError(f"Unsupported basis: {basis}")
    

def robust_derivative(f, domain=(-1, 1), method='savitzky_golay'):
    """
    Estimate the derivative of f over the domain.
    Supports: SymPy expressions, callables, coefficient arrays.
    """
    if isinstance(f, Expr) and hasattr(f, 'diff'):
        return f.diff()

    elif callable(f):
        x = np.linspace(domain[0], domain[1], 1000)
        y = f(x)

        if method == 'savitzky_golay':
            from scipy.signal import savgol_filter
            dy = savgol_filter(y, window_length=51, polyorder=3, deriv=1)
        else:
            dy = np.gradient(y, x)

        return lambda x_val: np.interp(x_val, x, dy)

    elif isinstance(f, np.ndarray):
        return np.polyder(f)

    else:
        raise TypeError(f"Unsupported input type for derivative: {type(f)}")

