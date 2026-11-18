# Datasets

| Benchmark | Official source | Relevant evaluation data |
| --- | --- | --- |
| HotpotQA | [Project and downloads](https://hotpotqa.github.io/) · [Evaluator source](https://github.com/hotpotqa/hotpot/blob/3635853403a8735609ee997664e1528f4480762a/hotpot_evaluate_v1.py) | Development distractor split for the full development evaluation. The controlled ablation uses a separately frozen subset. |
| 2WikiMultiHopQA | [Maintainers’ repository](https://github.com/Alab-NII/2wikimultihop) | Use the maintainers’ download and split instructions for development-set data. Paper-specific sample selection and derived contexts are separate artifacts. |

Obtain the datasets from their maintainers and follow the accompanying terms of use. Keep dataset files outside this repository. The public benchmarks provide the source questions, reference answers, and evidence. Reproducing a reported run additionally requires its frozen question IDs, evidence selection and serialization, and any required archived model outputs.

Pass questions and retrieved evidence to the inference code. Use reference answers only in the offline evaluation step.
