# CVoD-RAG Reproducibility

This repository accompanies the CVoD-RAG manuscript prepared for *Information*. It contains the core decision code, selected experiment settings, answer-scoring functions, and paired bootstrap code.

CVoD-RAG studies when one more generation helps after retrieval is fixed. It uses the same question, retrieved context, and generator for each answer generation. The lexical step (L) checks for answer absence, with a yes/no question exemption. The semantic step (S) checks the question against the current answer and triggers a fresh generation on `OFF_TOPIC`. The terminal step (T) makes one additional reasoning call when neither previous diagnosis triggered. The policy is prespecified and uses no reference answer. CVoD estimates quality change offline, using reference answers and paired responses by state.

| Path | Contents |
| --- | --- |
| `src/` | Initial prompt builder, L/S/T policy and request construction, historical S prompts, and S/T fallback handling |
| `evaluation/` | HotpotQA answer scoring, archived local scorer, and paired bootstrap utilities |
| `configs/` | Frozen HotpotQA settings and ablation bootstrap conventions |

Use Python 3.11 or newer. The included modules use the standard library. See [Reproducibility](REPRODUCIBILITY.md) for the executable interfaces and required user-supplied inputs, and [Datasets](DATASETS.md) for the benchmark providers.

Experimental predictions, source data, and run logs are held separately. The supplied code and settings do not reproduce the manuscript's result tables on their own.

The official HotpotQA answer-scoring extract is distributed under the accompanying [upstream Apache 2.0 license](evaluation/HOTPOTQA_LICENSE.txt). That license applies to the upstream extract.
