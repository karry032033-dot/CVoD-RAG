"""Recompute paired intervals from separately supplied frozen score CSVs on CPU."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from paired_stats import bootstrap_paired


ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "g1": (500, "sample_id", "c6a5eae451456d785c90c6496a403ed08b174dfd122c005eadb18337ac0b882d"),
    "full": (7405, "example_id", "d5e9687b7e4ac1d6676eddfa4914cdf59348b3c87633c1e6533ee494fcb8a3cb"),
}


def mean(values):
    return sum(values) / len(values)


def comparison(rows, left, right, metric, draws, seed, indices, adjusted_indices=()):
    a = [float(r[f"{left}_{metric}"]) for r in rows]
    b = [float(r[f"{right}_{metric}"]) for r in rows]
    if any(not math.isfinite(x) or not 0 <= x <= 1 for x in a + b):
        raise ValueError(f"Invalid score for {left} minus {right}, {metric}")
    delta = [x - y for x, y in zip(a, b)]
    boot = sorted(bootstrap_paired(delta, draws, seed))
    result = {
        "contrast": f"{left}-{right}",
        "metric": metric,
        "left_mean": mean(a),
        "right_mean": mean(b),
        "delta": mean(delta),
        "ci95": [boot[i] for i in indices],
        "improved": sum(x > 0 for x in delta),
        "degraded": sum(x < 0 for x in delta),
        "unchanged": sum(x == 0 for x in delta),
    }
    if adjusted_indices:
        result["bonferroni_six"] = [boot[i] for i in adjusted_indices]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cohort", choices=FROZEN)
    parser.add_argument("scores_csv", type=Path)
    args = parser.parse_args()
    n, id_key, expected_hash = FROZEN[args.cohort]
    if hashlib.sha256(args.scores_csv.read_bytes()).hexdigest() != expected_hash:
        parser.error("Score CSV does not match the frozen export, including its row order")
    with args.scores_csv.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != n or len({row[id_key] for row in rows if row[id_key]}) != n:
        parser.error(f"Expected {n} unique nonempty IDs")
    if args.cohort == "g1":
        cfg = json.loads((ROOT / "configs/hotpotqa_ablation_statistics.json").read_bytes())
        draws, seed = cfg["bootstrap_draws"], cfg["bootstrap_seed"]
        ranks = cfg["ci95_zero_based_indices"]
        adjusted = cfg["bonferroni_six_zero_based_indices"]
        pairs, metrics = cfg["paired_contrasts"], cfg["metrics"]
    else:
        cfg = json.loads((ROOT / "configs/hotpotqa_full_selective.json").read_bytes())["bootstrap"]
        draws, seed = cfg["draws"], cfg["seed"]
        # Corrected central 95% ranks used in the manuscript.
        ranks, adjusted = (249, 9749), ()
        pairs, metrics = (("m7", "m2"),), ("f1", "em")
    results = [comparison(rows, a, b, m, draws, seed, ranks, adjusted)
               for a, b in pairs for m in metrics]
    print(json.dumps({"cohort": args.cohort, "n": n, "csv_sha256": expected_hash,
                      "bootstrap_seed": seed, "draws": draws, "rank_indices": ranks,
                      "comparisons": results}, indent=2))


if __name__ == "__main__":
    main()

