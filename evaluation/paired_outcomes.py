"""Offline benefit and loss over one frozen cohort of paired scores."""

import math


def decompose(deltas):
    deltas = list(deltas)
    if not deltas or any(not math.isfinite(x) or not -1 <= x <= 1 for x in deltas):
        raise ValueError("Expected a nonempty sequence of score changes in [-1, 1]")
    n = len(deltas)
    return {
        "n": n,
        "benefit": math.fsum(max(x, 0.0) for x in deltas) / n,
        "loss": math.fsum(max(-x, 0.0) for x in deltas) / n,
        "net": math.fsum(deltas) / n,
        "improved": sum(x > 0 for x in deltas),
        "degraded": sum(x < 0 for x in deltas),
        "unchanged": sum(x == 0 for x in deltas),
    }
