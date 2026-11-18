# CVoD-RAG: History-Aware Regeneration under Fixed Evidence

**Official Code and Reproducibility Resources**

CVoD-RAG is a research framework for investigating the conditional value of additional generation in retrieval-augmented question answering. It focuses on improving the utilization of already retrieved evidence through sequential answer diagnostics and history-aware regeneration, without modifying the underlying retrieval results.

This repository accompanies the research manuscript:

**CVoD-RAG: An Empirical Study of History-Aware Regeneration under Fixed Evidence**

*Submitted to Information (MDPI), Special Issue: Advanced Retrieval-Augmented Generation Systems Based on Large Language Models.*

The repository provides the core algorithmic components, selected experimental configurations, evaluation utilities, and technical documentation associated with the study.

---

## 1. Introduction

Retrieval-augmented generation (RAG) enhances large language models by incorporating external evidence into the answer-generation process. However, obtaining relevant evidence does not necessarily guarantee that the generator will utilize it effectively. Even when the retrieved context is sufficient, generated responses may remain incomplete, irrelevant, or incorrect.

A common approach to addressing these failures is to introduce additional generation or reasoning steps. Nevertheless, repeated generation incurs computational overhead and does not consistently improve answer quality. In some cases, it may even replace a previously correct answer with an incorrect one.

These observations motivate an important research question:

**Under a fixed evidence setting, when is an additional generation step beneficial, and when does it introduce unnecessary computation or answer degradation?**

CVoD-RAG investigates this question through a history-aware regeneration procedure and an offline analysis of the conditional effects of additional generation.

Rather than repeatedly retrieving evidence or learning a separate routing model, the framework reuses the same question, retrieved context, and generator, while regulating the execution of additional generation based on previously observed diagnostic and generation history.

## 2. Method Overview

CVoD-RAG integrates sequential answer diagnostics with a prespecified, training-free regeneration policy.

The framework consists of three principal components:

| Component | Description | Function |
|---|---|---|
| **L — Lexical Diagnosis** | Evaluates lexical evidence associated with the current answer, including a specific exemption for yes/no questions. | Identifies conditions requiring further answer examination or regeneration. |
| **S — Semantic Diagnosis** | Examines question–answer relevance and identifies the `OFF_TOPIC` diagnostic state. | Triggers a fresh generation when the current answer is judged insufficiently relevant to the question. |
| **T — Terminal Regeneration** | Performs an additional thinking-mode generation step when neither preceding diagnostic stage has already triggered regeneration. | Controls the final regeneration action using the recorded generation history. |

### 2.1. Sequential Answer Diagnostics

The framework starts from an initial answer generated using the original question and fixed retrieved evidence.

The L and S components subsequently examine the answer through complementary diagnostic criteria.

The lexical diagnostic considers answer-related lexical evidence, while the semantic diagnostic evaluates the relationship between the question and the generated answer. When an eligible diagnostic condition is satisfied, the corresponding procedure may trigger an additional generation action.

The diagnostic stages are applied sequentially, and their outcomes contribute to the generation history used by the terminal decision.

### 2.2. History-Aware Regeneration

The terminal component determines whether an additional thinking-mode generation should be executed.

Its decision depends on whether earlier diagnostic stages have already triggered regeneration. If regeneration has occurred, the terminal stage avoids scheduling another regeneration action under the prespecified policy.

This design distinguishes CVoD-RAG from strategies that uniformly allocate an additional thinking-mode generation to every question.

The online policy is training-free and does not require access to reference answers during execution.

### 2.3. Conditional Value of Deliberation

Beyond the online regeneration procedure, CVoD-RAG evaluates the effects of additional generation through an offline, question-level analysis.

The analysis considers both:

- **Answer improvement:** cases in which additional generation increases answer quality.
- **Answer degradation:** cases in which additional generation reduces answer quality.

These effects are examined conditionally using recorded diagnostic states and paired responses.

Reference answers are used for offline evaluation and statistical analysis, rather than for determining online regeneration actions.

The resulting analysis provides an empirical characterization of the potential benefits and risks associated with additional generation under fixed evidence.

---

## 3. Repository Organization

The repository contains the essential research implementation and documentation.

| Directory / File | Description |
|---|---|
| `src/` | Core CVoD-RAG logic, prompt construction, L/S/T decision procedures, historical semantic prompts, and generation fallback handling. |
| `evaluation/` | HotpotQA answer-scoring functions, archived scoring utilities, and paired statistical analysis code. |
| `configs/` | Selected experimental settings, frozen HotpotQA configurations, and bootstrap conventions. |
| `README.md` | Research overview, methodological description, and repository introduction. |
| `DATASETS.md` | Official benchmark sources and dataset acquisition information. |
| `REPRODUCIBILITY.md` | Technical interfaces, required inputs, and available reproduction procedures. |
| `requirements.txt` | Python dependency information. |
| `.gitignore` | Git exclusion rules for development and temporary files. |

Only the essential public-facing components are included. Internal project archives and unrelated experimental materials are excluded from this repository.

## 4. Experimental Evaluation

The accompanying manuscript evaluates CVoD-RAG using multi-hop question-answering benchmarks and controlled generation comparisons.

The experimental methodology includes the following aspects.

### 4.1. Answer Quality

Answer quality is assessed using standard question-answering evaluation metrics, including:

- Exact Match (EM).
- Token-level F1.

The supplied scoring utilities support answer-level evaluation in accordance with the documented HotpotQA scoring conventions.

### 4.2. Component Ablation

The experimental framework examines the contributions of the lexical diagnostic, semantic diagnostic, and terminal regeneration components.

The accompanying manuscript reports comparisons involving the complete framework, component-removal configurations, and alternative generation procedures.

These experiments are intended to distinguish the contribution of individual processing components from improvements associated with additional generation more generally.

### 4.3. Paired Statistical Analysis

The repository includes paired bootstrap utilities for evaluating answer-quality differences between experimental conditions.

The analysis operates on aligned question-level observations and supports confidence-interval estimation under the documented experimental protocol.

Detailed statistical conventions and required inputs are provided in the reproducibility documentation.

### 4.4. Computational Evaluation

The accompanying research also investigates computational expenditure associated with selective regeneration, including generation calls, output tokens, and recorded response times.

Importantly, final-stage computational measurements are distinguished from complete-workflow computation.

The repository does not include the private execution logs required to independently reconstruct every computational result reported in the manuscript.

---

## 5. Installation and Environment

### 5.1. Requirements

The public code package is designed for Python 3.11 or newer.

The included modules use the Python standard library. External model execution environments, benchmark resources, and experiment-specific inputs must be supplied separately where required.

### 5.2. Obtain the Repository

Clone the public repository:

`git clone https://github.com/karry032033-dot/CVoD-RAG.git`

Then enter the repository:

`cd CVoD-RAG`

### 5.3. Environment Preparation

Consult `requirements.txt` for the documented dependency information and `REPRODUCIBILITY.md` for the available executable interfaces.

The repository does not distribute model checkpoints or provide a bundled model-serving environment.

Users are responsible for configuring any external generator or inference backend required by the research procedures.

## 6. Datasets

The accompanying study uses publicly available multi-hop question-answering benchmarks.

### HotpotQA

HotpotQA is a multi-hop question-answering benchmark involving reasoning across multiple supporting documents.

Official dataset website:

https://hotpotqa.github.io/

### 2WikiMultiHopQA

2WikiMultiHopQA is a multi-hop question-answering benchmark constructed using information from multiple Wikipedia passages.

Official dataset repository:

https://github.com/Alab-NII/2wikimultihop

Dataset acquisition, applicable splits, and preparation requirements are described in `DATASETS.md`.

**The benchmark datasets themselves are not redistributed through this repository.** Users should obtain them from their original providers and comply with the applicable licenses and usage conditions.

## 7. Reproducibility

This repository provides a documented implementation package for examining the CVoD-RAG method and selected evaluation procedures.

To use the available resources:

1. Obtain the relevant benchmark datasets from their official sources.
2. Review the experimental configurations under `configs/`.
3. Configure the model environment and supply the inputs required by the implementation.
4. Follow the executable interfaces documented in `REPRODUCIBILITY.md`.
5. Use the evaluation utilities to score available predictions.
6. Apply the paired statistical analysis utilities to appropriately aligned experimental observations.

### Scope of Reproducibility

The public release provides method code, selected configurations, and evaluation utilities. However, the original experimental predictions, underlying research records, and execution logs are maintained separately by the authors.

Consequently, **the public repository alone is not a complete end-to-end reproduction package for all numerical results reported in the manuscript.**

Reproducing specific tables or statistical comparisons may require additional experiment outputs or regenerated predictions under the documented protocols.

This distinction is maintained to ensure that the repository accurately represents the research assets that have been released.

## 8. Data and Code Availability

### Publicly Available Resources

The following research resources are provided through this GitHub repository:

- Essential CVoD-RAG implementation code.
- Selected and sanitized experimental configurations.
- Answer-scoring and paired statistical analysis utilities.
- Benchmark dataset references.
- Reproducibility and technical documentation.

### Research Data Access

The question-level predictions, evaluation records, and execution logs generated during the study are retained by the authors and are not publicly distributed.

Their external distribution is subject to approval by the research team.

Requests for access may be directed to the corresponding author and will be considered on a case-by-case basis, subject to authorization.

The public code repository should not be interpreted as containing the complete experimental data underlying the manuscript.

---

## 9. Licensing and Third-Party Components

The repository includes an extract of the official HotpotQA answer-scoring implementation.

The corresponding upstream licensing terms are provided in:

`evaluation/HOTPOTQA_LICENSE.txt`

The upstream extract is distributed under the Apache License 2.0 license, as indicated by the accompanying license notice.

This upstream license does not automatically apply to all original CVoD-RAG source files.

Reuse and redistribution of other repository components remain subject to their respective applicable rights and any separately provided licensing terms.

## 10. Citation

If this repository is useful for your research, please cite the associated manuscript once its bibliographic publication details become available.

**Manuscript title:**

*CVoD-RAG: An Empirical Study of History-Aware Regeneration under Fixed Evidence*

**Journal:** Information (MDPI)

**Manuscript status:** Submitted

Formal publication metadata, including a DOI, will be added if and when the manuscript is published.

## 11. Research Scope and Limitations

CVoD-RAG is developed and evaluated within a fixed-evidence generation setting.

Its current empirical findings should be interpreted within the evaluated benchmarks, generation protocols, and model configurations.

In particular:

- The framework does not perform additional retrieval during its regeneration decisions.
- The online policy is prespecified and training-free.
- Offline reference-based analysis is not used as an online routing predictor.
- Improvements from additional generation are not assumed to occur uniformly across questions.
- Stage-specific computational savings should not be interpreted as complete-workflow savings without corresponding measurements.
- The public release does not contain every original experimental artifact.

These distinctions define the scope of the method and the available reproducibility resources.

---

**CVoD-RAG — Research code, evaluation utilities, and reproducibility documentation for history-aware regeneration under fixed evidence.**
