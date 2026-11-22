# Reproducibility

In preparation for submission to Computers (MDPI); not yet submitted. See [Code and data availability](README.md#code-and-data-availability) for the release and data-access status.

## Run the included offline checks

Run from the repository root with Python 3.11 or newer. The offline tools use the Python standard library.

    python -m pip install -r requirements.txt
    python tests/smoke.py
    python tests/test_control_flow.py
    python src/m2_dr_implementation.py
    python evaluation/paired_stats.py --help
    python evaluation/reproduce_frozen.py --help

The smoke tests use synthetic answer pairs and a fixed-seed paired-statistics CLI. The control-flow fixture also checks the initial prompt, fixed context reuse, exact S label, L/S/T routing, and verified G1 fallbacks. Its output is a software test. The examples carry no benchmark results.

## Recompute archived paired statistics with authorized scores

Replace the CSV names below with paths to the unchanged, separately authorized score exports. Those inputs are external to the ZIP.

    python evaluation/reproduce_frozen.py g1 R9_PER_EXAMPLE_OFFICIAL_SCORES.csv
    python evaluation/reproduce_frozen.py full m7_paired_comparison.csv

The script checks the file hash, unique IDs, and score range and prints JSON. G1 uses 500 ordered examples, six prespecified contrasts, F1 and EM, 10,000 paired resamples, seed 20261113, and zero-based ranks [249, 9749] for the ordinary interval and [41, 9958] for the Bonferroni-adjusted interval. Full uses 7,405 ordered examples, M7 minus M2, 10,000 resamples, seed 20260910 and paper ranks [249, 9749]. The earlier wider interval [124, 9874] remains documented in [the historical Full configuration](configs/hotpotqa_full_selective.json).

The [generic paired-statistics tool](evaluation/paired_stats.py) accepts one JSONL row per condition and ID, takes the ID intersection, and uses interpolated percentiles. Run the frozen-score CLI for the paper intervals.

## Score answers and interpret costs

Use the functions f1_score and exact_match_score from [the official answer scorer extract](evaluation/official_answer_scorer.py). Use [the historical helper](evaluation/metrics.py) only for legacy checks: when both answers normalize to empty, its F1 is 1 while the official F1 is 0. The separate alias-aware 2WikiMultiHopQA scorer is available from its maintainers, listed in [Benchmark sources](DATASETS.md).

G1's 1,104 distinct physical response receipts and attributed policy costs require the archive's receipts and traces. The G3 Table 1 calculation needs the retained final-stage cache. Its cost boundary begins after both diagnostics. The Full-7,405 research archive contains final predictions and paired scores. The complete historical request and response archive and some request-to-output mappings could not be recovered.

## Use the fixed-evidence components

1. Freeze the retrieval evidence and question per example. [The prompt builder](src/generation.py) constructs the initial answer prompt. The retrieval runner, serialized evidence, and historical initial answers are external.
2. Load the [G1 configuration](configs/R2_PROTOCOL.json) with load_protocol in [the request module](src/r2_requests.py). The configuration records the template hash and the target backend. Supply a matching model template in a private copy, then validate it. The archived Full settings are separate from G1's.
3. Use request_factory and the execute_arm function from [the R5 executor](src/r5_executor.py) with the source directory on the module search path. Provide sample_id, question, context, y0 and a fresh decisions list. The caller provides model serving, verified responses, and provenance appropriate for fallback.
4. Use reference answers only for offline scoring. Offline conditional values need baseline and candidate answers from valid pairs for every state evaluated.

[Third-party notices](THIRD_PARTY_NOTICES.md) records the scorer's provenance and license.

[Aggregate results and required input schema](public_results/README.md) describes the information required to reproduce the paper’s core statistics.
