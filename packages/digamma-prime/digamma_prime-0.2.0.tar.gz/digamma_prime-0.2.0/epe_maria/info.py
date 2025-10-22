def teach():
    print("""
📘 Welcome to Digamma Prime — Symbolic Audit Framework

This tutorial will walk you through the core concepts, modules, and usage of `digamma-ep`.

---

🔍 What is Symbolic Auditing?

Unlike statistical tests, symbolic auditing compares the *shape*, *rate*, and *curvature* of model outputs or distributions. It reveals how models evolve, destabilize, or diverge — even when statistical metrics say "no difference."

---

📦 Module Overview

1. `metrics.py` — Core symbolic metrics:
   - `phi(x, y)`: Structural divergence
   - `delta_phi(x, y)`: Rate divergence
   - `second_order_divergence(x, y)`: Curvature divergence

2. `temporal.py` — Time-aware metrics:
   - `second_order_divergence()` over time
   - Use for monitoring drift or instability

3. `benchmark.py` — Compare symbolic vs statistical:
   - `benchmark_epe_vs_ks(x, y)`
   - KS test vs symbolic divergence

4. `monitor.py` — Audit pipelines:
   - Combine metrics into monitoring workflows

---

🚀 Quickstart Example

```python
import numpy as np
from epe_maria.metrics import phi, delta_phi
from epe_maria.temporal import second_order_divergence

x = np.linspace(-2, 2, 100)
reference = x**4
current = x**4 - 1

print("ϝ =", phi(reference, current))
print("δϝ =", delta_phi(reference, current))
print("δ²ϝ =", second_order_divergence(reference, current)).""")
