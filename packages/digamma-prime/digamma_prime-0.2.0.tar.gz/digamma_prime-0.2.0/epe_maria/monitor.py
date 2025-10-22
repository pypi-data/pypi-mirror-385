def drift(f, g, domain=None):
    """
    Measures directional drift between two functions over a domain.
    Positive if f tends to exceed g, negative if g exceeds f.
    """
    if domain is None:
        domain = range(-10, 11)
    return sum(f(x) - g(x) for x in domain) / len(domain)


def curvature(f, domain=None):
    """
    Estimates average curvature of a function over a domain.
    Uses second derivative approximation.
    """
    if domain is None:
        domain = range(-10, 11)

    def second_derivative(func, x, h=1e-5):
        return (func(x + h) - 2 * func(x) + func(x - h)) / (h ** 2)

    return sum(abs(second_derivative(f, x)) for x in domain) / len(domain)
