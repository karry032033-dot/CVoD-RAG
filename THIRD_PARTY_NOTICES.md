# Third-party notices

The [HotpotQA answer scorer](evaluation/official_answer_scorer.py) extracts the three answer-scoring functions from the [pinned upstream evaluator](https://github.com/hotpotqa/hotpot/blob/3635853403a8735609ee997664e1528f4480762a/hotpot_evaluate_v1.py). Their definitions are preserved. The module selects the required imports and records the upstream commit and file hash. The upstream [Apache License 2.0 text](evaluation/HOTPOTQA_LICENSE.txt) is included.

The [historical scoring helper](evaluation/metrics.py) contains a modified implementation of HotpotQA answer-scoring rules. Its empty-pair handling differs from the upstream scorer and is retained for compatibility. Attribution and the license above apply to the upstream material.

[Benchmark sources](DATASETS.md) lists dataset providers and terms separately. The original CVoD-RAG project code is covered by the [MIT License](LICENSE). The upstream terms above apply to the HotpotQA material.
