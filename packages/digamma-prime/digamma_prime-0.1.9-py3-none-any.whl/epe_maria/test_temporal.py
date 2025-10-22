{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "f882c9ae",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Second-order divergence (δ²ϝ) = 1.7320508075688772\n"
     ]
    }
   ],
   "source": [
    "import numpy as np\n",
    "\n",
    "def second_order_divergence(series1, series2):\n",
    "    \"\"\"\n",
    "    Calcula a divergência de segunda ordem entre duas séries temporais.\n",
    "    Mede a diferença na aceleração (curvatura).\n",
    "    \"\"\"\n",
    "    d2_series1 = np.diff(series1, n=2)\n",
    "    d2_series2 = np.diff(series2, n=2)\n",
    "\n",
    "    min_len = min(len(d2_series1), len(d2_series2))\n",
    "    d2_series1 = d2_series1[:min_len]\n",
    "    d2_series2 = d2_series2[:min_len]\n",
    "\n",
    "    divergence = np.linalg.norm(d2_series1 - d2_series2)\n",
    "    return divergence\n",
    "\n",
    "# Teste direto\n",
    "series1 = np.array([1, 2, 4, 7, 11])  # aceleração crescente\n",
    "series2 = np.array([1, 2, 3, 4, 5])   # aceleração constante\n",
    "\n",
    "delta2_phi = second_order_divergence(series1, series2)\n",
    "print(\"Second-order divergence (δ²ϝ) =\", delta2_phi)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "ea1905e7",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
