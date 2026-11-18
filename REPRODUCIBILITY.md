# Reproducibility

## Run the included checks

From the repository root, run:

```text
python src/m2_dr_implementation.py
python evaluation/paired_stats.py --help
```

The first command validates the historical S routing decision. The second documents the generic paired analysis CLI. Neither requires a model server or a dataset.

## Fixed-evidence policy

The eight-arm policy implementation exposes `execute_arm(sample, invoke, factory, arm, decisions=[])` in `src/r5_executor.py`. Add `src/` to the module search path, pass the accumulator by keyword, and create a new list for each independent run. The L/S/T settings are in `r2_executor.ARMS`. `B7` enables all three. The historical full-development run and the controlled ablation share the routing design but have different execution and recovery protocols.

1. Obtain a dataset and retrieve evidence once. Freeze the question, serialized context, and model per example. The settings in `configs/hotpotqa_initial_retrieval.yaml` describe the dense paragraph retrieval and initial generation. The original retrieval runner and serialized contexts are external inputs.
2. Construct the initial grounded prompt with `src/generation.py` and obtain the initial answer without extended thinking. Pass `sample_id`, `question`, `context`, and `y0` to the policy. Historical initial responses are separate inputs.
3. Load `configs/R2_PROTOCOL.json` and obtain the exact template from the specified model on the local Ollama installation. The public JSON records the original template SHA-256 but omits the template itself. Put the template in a private copy of the configuration JSON and pass that copy to `r2_requests.load_protocol(path)`. The loader checks the template bytes. A mismatch leaves the configured request identity unverified.
4. Pass the validated protocol to `r2_requests.request_factory`. For an offline check, supply a local fixture callback as `invoke`. For live use, supply a verified local model adapter. `r2_adapter.ollama_payload` constructs the payload and `parse_response` parses the HTTP result. The callback is responsible for response provenance, answer extraction via `clean_answer`, and verification of model identity, effective context and decoding, completion status, and fallback eligibility. The private runtime, trusted checkpoint receipts, and GPU validation are external dependencies.

The first reasoning candidate can serve either L or T when its complete request identity matches. On S, the diagnostic uses the current answer and question. Re-solving uses the original question and context. B7 runs its final T only when neither L nor S triggered. Fallback retains the current answer for eligible, verified failures as specified by the corresponding S/T policy. The public implementation contains no automatic live entry point.

`configs/hotpotqa_full_m2.json` and the two S prompts in `src/` describe the historical full-development S stage. `configs/hotpotqa_full_selective.json` records the historical final T decoding, recovery levels, and bootstrap ranks. `configs/R2_PROTOCOL.json` instead records the prospective eight-arm ablation's request protocol, including its explicit context size. Its T repair entries document the original protocol fields. The released executor applies the later bounded fallback policy and does not automatically launch those repair requests.

## Evaluate locally

Use `f1_score(prediction, reference)[0]` and `exact_match_score(prediction, reference)` in `evaluation/official_answer_scorer.py` for strict HotpotQA answer F1 and EM. The functions match the pinned [upstream scorer](https://github.com/hotpotqa/hotpot/blob/3635853403a8735609ee997664e1528f4480762a/hotpot_evaluate_v1.py). The archived helper in `evaluation/metrics.py` returns F1 = 1 when both strings normalize to empty. The strict scorer returns F1 = 0 for that case. For 2WikiMultiHopQA, obtain the official alias-aware evaluator separately.

For the generic bootstrap CLI, supply your own scored JSONL with `example_id`, `condition_label`, and the selected metric. Before running, require one row per example per condition, identical ID sets, and complete metric fields. The CLI pairs on the ID intersection and uses interpolated percentiles.

```text
python evaluation/paired_stats.py local_scores.jsonl --compare CVoD M2 CVoD_vs_M2 --metric official_answer_f1 --bootstrap-iterations 10000 --seed 20260910 --out local_comparison.csv
```

For the exact eight-arm convention, align all conditions in frozen sample order. Subtract right-arm scores from left-arm scores for each ID, call `bootstrap_paired(differences, 10000, 20261113)`, and sort the resulting means. Read the rank indices and contrasts from `configs/hotpotqa_ablation_statistics.json`. The pointwise and corrected intervals use empirical ranks, so the generic CLI's interpolated limits do not reproduce them. Evaluate F1 and EM separately.

The historical full-development F1 comparison has its own rank indices in `configs/hotpotqa_full_selective.json`. To reproduce that procedure, use differences in the original population order and its recorded seed and rank indices.

To estimate offline CVoD for a state, use an M2 answer, an additional candidate, and a reference answer for each contributing example. Pair on the same ID, subtract the M2 score from the additional candidate's score, and summarize the differences by the recorded post-diagnostic state. Running the selective online policy alone produces no additional candidates for unselected cases and cannot estimate CVoD for those states.

## Scope of validation

CPU checks cover the policy functions, provenance-dependent fallback, prompt and request construction, answer scoring, and paired bootstrap on software test fixtures. The released code has not been used to regenerate the historical runs. The public package omits the frozen ablation population, original response archive, serialized evidence, and research cost ledger. It does not establish that the archived per-example predictions and compute records correspond to every number in V37.
