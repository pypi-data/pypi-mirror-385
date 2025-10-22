import numpy as np

def phi(f, g, domain=None):
    """
    Structural divergence between two functions f and g.
    Measures average absolute difference over a domain.
    """
    if domain is None:
        domain = range(-10, 11)

    differences = [abs(f(x) - g(x)) for x in domain]
    return np.mean(differences)


def delta_phi(f, g, domain=None):
    """
    Rate divergence between two functions f and g.
    Measures average absolute difference in derivatives.
    """
    if domain is None:
        domain = range(-10, 11)

    def derivative(func, x, h=1e-5):
        return (func(x + h) - func(x - h)) / (2 * h)

    rate_diffs = [abs(derivative(f, x) - derivative(g, x)) for x in domain]
    return np.mean(rate_diffs)


def phi_star(f, g, alpha=0.5, beta=0.5, domain=None):
    """
    Fusion metric combining structural and rate divergence.
    Weighted sum of phi and delta_phi.
    """
    if domain is None:
        domain = range(-10, 11)

    phi_val = phi(f, g, domain)
    delta_val = delta_phi(f, g, domain)

    return alpha * phi_val + beta * delta_val
