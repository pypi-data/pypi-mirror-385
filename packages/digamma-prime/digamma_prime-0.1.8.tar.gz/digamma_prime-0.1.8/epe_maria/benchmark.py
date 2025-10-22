from epe_maria.metrics import phi
from scipy.stats import ks_2samp

def benchmark_epe_vs_ks(reference, current):
    """
    Compara a métrica Epe (ϝ) com o KS-test.
    Retorna os scores e interpretações.
    """
    epe_score = phi(reference, current)
    ks_stat, ks_p = ks_2samp(reference, current)

    result = {
        "ϝ (Epe)": round(epe_score, 6),
        "KS-stat": round(ks_stat, 6),
        "KS-p": round(ks_p, 6),
        "KS drift detected": ks_p < 0.05
    }
    return result
