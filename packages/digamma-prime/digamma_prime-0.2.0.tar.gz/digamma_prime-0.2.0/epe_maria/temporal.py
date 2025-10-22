import numpy as np

def second_order_divergence(series1, series2):
    """
    Calcula a divergência de segunda ordem entre duas séries temporais.
    Mede a diferença na aceleração (curvatura).
    """
    d1_series1 = np.diff(series1, n=1)
    d1_series2 = np.diff(series2, n=1)

    d2_series1 = np.diff(d1_series1, n=1)
    d2_series2 = np.diff(d1_series2, n=1)

    min_len = min(len(d2_series1), len(d2_series2))
    d2_series1 = d2_series1[:min_len]
    d2_series2 = d2_series2[:min_len]

    divergence = np.linalg.norm(d2_series1 - d2_series2)
    return divergence
