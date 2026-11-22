import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import stdev


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_csv(rows, path):
    rows = list(rows)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run_label",
        "comparison",
        "condition_a",
        "condition_b",
        "metric",
        "n",
        "condition_a_mean",
        "condition_b_mean",
        "mean_difference",
        "ci95_low",
        "ci95_high",
        "p_bootstrap",
        "cohen_dz",
        "bootstrap_iterations",
        "seed",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def percentile(values, pct):
    values = sorted(values)
    pos = (len(values) - 1) * pct
    lo = int(pos)
    hi = min(lo + 1, len(values) - 1)
    frac = pos - lo
    return values[lo] * (1.0 - frac) + values[hi] * frac


def bootstrap_paired(values, iterations, seed):
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(iterations):
        total = 0.0
        for _ in range(n):
            total += values[rng.randrange(n)]
        means.append(total / n)
    return means


def condition_groups(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["condition_label"]].append(row)
    return groups


def paired_difference(rows, condition_a, condition_b, metric, iterations, seed):
    groups = condition_groups(rows)
    if condition_a not in groups:
        raise ValueError(f"condition not found: {condition_a}")
    if condition_b not in groups:
        raise ValueError(f"condition not found: {condition_b}")

    a_by_id = {row["example_id"]: row for row in groups[condition_a]}
    b_by_id = {row["example_id"]: row for row in groups[condition_b]}
    example_ids = sorted(set(a_by_id) & set(b_by_id))
    if not example_ids:
        raise ValueError(f"no matched examples for {condition_a} vs {condition_b}")

    a_values = [float(a_by_id[example_id].get(metric, 0.0) or 0.0) for example_id in example_ids]
    b_values = [float(b_by_id[example_id].get(metric, 0.0) or 0.0) for example_id in example_ids]
    diffs = [a - b for a, b in zip(a_values, b_values)]
    mean_diff = sum(diffs) / len(diffs)
    samples = bootstrap_paired(diffs, iterations, seed)
    le_zero = sum(1 for value in samples if value <= 0.0)
    ge_zero = sum(1 for value in samples if value >= 0.0)
    # The +1 correction avoids reporting a Monte Carlo p-value of exactly zero.
    tail_count = min(le_zero, ge_zero)
    p_value = min(1.0, 2.0 * (tail_count + 1) / (len(samples) + 1))
    sd = stdev(diffs) if len(diffs) > 1 else 0.0
    cohen_dz = mean_diff / sd if sd else 0.0
    return {
        "n": len(diffs),
        "condition_a_mean": sum(a_values) / len(a_values),
        "condition_b_mean": sum(b_values) / len(b_values),
        "mean_difference": mean_diff,
        "ci95_low": percentile(samples, 0.025),
        "ci95_high": percentile(samples, 0.975),
        "p_bootstrap": p_value,
        "cohen_dz": cohen_dz,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Compute paired bootstrap differences between named prediction conditions."
    )
    parser.add_argument("predictions_jsonl")
    parser.add_argument(
        "--compare",
        action="append",
        nargs=3,
        metavar=("CONDITION_A", "CONDITION_B", "LABEL"),
        required=True,
        help="Repeatable comparison specification.",
    )
    parser.add_argument("--metric", default="answer_f1")
    parser.add_argument("--run-label", default="")
    parser.add_argument("--bootstrap-iterations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=77)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    predictions_path = Path(args.predictions_jsonl)
    rows = read_jsonl(predictions_path)
    out_rows = []
    for condition_a, condition_b, label in args.compare:
        stats = paired_difference(
            rows,
            condition_a=condition_a,
            condition_b=condition_b,
            metric=args.metric,
            iterations=args.bootstrap_iterations,
            seed=args.seed,
        )
        out_rows.append(
            {
                "run_label": args.run_label,
                "comparison": label,
                "condition_a": condition_a,
                "condition_b": condition_b,
                "metric": args.metric,
                "bootstrap_iterations": args.bootstrap_iterations,
                "seed": args.seed,
                **stats,
            }
        )

    out_path = Path(args.out) if args.out else predictions_path.parent / "paired_stats.csv"
    write_csv(out_rows, out_path)
    print("wrote:", out_path)


if __name__ == "__main__":
    main()
