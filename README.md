# CVoD-RAG

Companion code for **CVoD-RAG: Evaluating Regeneration Value and History-Aware Scheduling under Fixed Evidence**. The manuscript is in preparation for submission to *Computers* (MDPI), in the Special Issue *Trustworthy and Efficient Large Language Models: Methods, Systems and Applications*. It has not been submitted to Computers.

## Fixed-evidence workflow

Supply a question and frozen evidence context. The initial prompt builder uses that evidence, and the caller supplies the initial answer and the model-response callback. Subsequent answer generation uses the same question and evidence.

- **L** checks that the first token of the normalized question exists and is outside the fixed auxiliary set. It triggers when the normalized initial answer is nonempty and absent as a contiguous substring of the normalized evidence.
- **S** sees the question and current answer. The exact OFF_TOPIC label triggers re-solving against the original question and evidence.
- **T** uses the recorded L/S history. The final thinking-mode attempt is scheduled only when both trigger flags are zero. Verified G1 empty or truncated results retain the appropriate previous valid answer.

The paired benefit and loss measure uses answer and reference scores offline. It does not enter the scheduler. The fixed-evidence components do not run retrieval or a historical inference backend.

## Install and test

Run the following from the repository root with Python 3.11 or later:

    python -m pip install -r requirements.txt
    python tests/smoke.py
    python tests/test_control_flow.py
    python src/m2_dr_implementation.py
    python evaluation/paired_stats.py --help
    python evaluation/reproduce_frozen.py --help

The included tests use synthetic examples. The score and interval recomputation commands described in [Reproducibility](REPRODUCIBILITY.md) need separately authorized frozen score exports. [Benchmark sources](DATASETS.md) links to the original datasets.

## Code and data availability

- [src](src/) contains the initial prompt, diagnostics, request construction, and G1 dispatch and fallback.
- [configs](configs/) contains selected protocol and statistics settings, including separate G1 and historical Full settings.
- [evaluation](evaluation/) contains HotpotQA answer scoring and paired offline statistics.
- [tests](tests/) contains the synthetic fixture and CPU smoke tests.
- [public_results](public_results/) contains manuscript-level aggregates and the minimum required input schema.
- [SHA256SUMS.txt](SHA256SUMS.txt) lists checksums for the complete published file set.

The original project code is available under the [MIT License](LICENSE). See [Third-party notices](THIRD_PARTY_NOTICES.md) for HotpotQA software attribution and separate license terms.

Retained per-example predictions, scores, request receipts, and experiment caches remain subject to applicable permissions. Researchers may request access to retained material from the corresponding author listed in the manuscript. The complete historical execution archive and some request-to-output mappings are unavailable.
