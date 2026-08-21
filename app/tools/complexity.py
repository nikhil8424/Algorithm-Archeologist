import math
from typing import List, Tuple, Optional

class ComplexityEstimator:
    """Estimates empirical scaling complexity by regression curve fitting."""

    def fit_curve(self, data_points: List[Tuple[int, float]]) -> str:
        # data_points is [(N, runtime_ms), ...]
        valid = [(n, t) for n, t in data_points if n > 0 and t > 0]
        if len(valid) < 2:
            return "O(N) (insufficient samples)"

        # Compare ratios:
        # If t2 / t1 ~ n2 / n1 => O(N)
        # If t2 / t1 ~ (n2/n1)^2 => O(N^2)
        # If t2 / t1 ~ log(n2)/log(n1) => O(log N)
        # If t2 / t1 ~ 1 => O(1)

        p_first = valid[0]
        p_last = valid[-1]
        
        n_ratio = p_last[0] / p_first[0]
        t_ratio = p_last[1] / max(p_first[1], 0.001)

        if n_ratio <= 1.0:
            return "O(N)"

        # power alpha: t_ratio = (n_ratio)^alpha => alpha = ln(t_ratio) / ln(n_ratio)
        try:
            alpha = math.log(max(t_ratio, 0.0001)) / math.log(n_ratio)
        except Exception:
            return "O(N)"

        if alpha < 0.2:
            return "O(1)"
        elif alpha < 0.6:
            return "O(log N)"
        elif alpha < 1.3:
            return "O(N) ~ O(N log N)"
        elif alpha < 2.4:
            return "O(N^2)"
        elif alpha < 3.4:
            return "O(N^3)"
        else:
            return "O(2^N) Exponential"

complexity_estimator = ComplexityEstimator()
