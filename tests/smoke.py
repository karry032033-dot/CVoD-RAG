"""Offline synthetic software checks, with no benchmark data or model calls."""

import csv
import json
from math import isclose
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "evaluation")]

from m2_dr_implementation import action
from official_answer_scorer import exact_match_score, f1_score

EXAMPLES = [
    ("York", "The New York", "New York"),
    ("no", "yes", "yes"),
    ("blue", "green", "blue"),
]


def main():
    assert action("OFF_TOPIC") == "RE_SOLVE"
    assert action("OK") == action("OFF_TOPIC because") == "RETAIN_T1"
    assert f1_score("", "")[0] == 0
    assert exact_match_score("", "") == 1

    with tempfile.TemporaryDirectory() as temp:
        scores = Path(temp) / "fixture.jsonl"
        output = Path(temp) / "comparison.csv"
        with scores.open("w", encoding="utf-8") as f:
            for index, (baseline, candidate, reference) in enumerate(EXAMPLES):
                for name, answer in (("baseline", baseline), ("candidate", candidate)):
                    row = {
                        "example_id": f"synthetic-{index}",
                        "condition_label": name,
                        "answer_f1": f1_score(answer, reference)[0],
                        "answer_em": int(exact_match_score(answer, reference)),
                    }
                    f.write(json.dumps(row) + "\n")

        scorer = ROOT / "evaluation" / "paired_stats.py"
        for metric, target, expected in [("answer_f1", (2/3, 5/9), 1/9), ("answer_em", (2/3, 1/3), 1/3)]:
            subprocess.run([sys.executable, "-B", str(scorer), str(scores),
                            "--compare", "candidate", "baseline", "synthetic",
                            "--metric", metric, "--bootstrap-iterations", "1000", "--seed", "77",
                            "--out", str(output)], check=True, capture_output=True)
            with output.open(encoding="utf-8", newline="") as f:
                result = next(csv.DictReader(f))
            a, b = (float(result[f"condition_{arm}_mean"]) for arm in ("a", "b"))
            delta = float(result["mean_difference"])
            assert result["n"] == "3" and isclose(delta, expected)
            assert all(isclose(x, y) for x, y in zip((a, b), target))
            ci = [float(result[k]) for k in ("ci95_low", "ci95_high")]
            print(f"SYNTHETIC {metric} n=3 candidate={a:.9f} baseline={b:.9f} delta={delta:+.9f} ci95=[{ci[0]:.6f}, {ci[1]:.6f}]")


if __name__ == "__main__":
    main()
