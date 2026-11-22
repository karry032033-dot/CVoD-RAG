# Aggregate outcomes and reproduction inputs

These are cohort summaries from the manuscript. Enabling independent recomputation of the paper intervals requires the paired records described below.

| Comparison | N | Result |
|---|---:|---|
| HotpotQA full development, selective vs diagnostic baseline | 7,405 | F1 0.727103 to 0.765239, paired +0.038136, 95% CI [0.032348, 0.044048] |
| G1 Full vs Uniform T | 500 | F1 0.773780 vs 0.774367, paired −0.000587, 95% CI [−0.005643, 0.003413] |
| G3 selective vs uniform final-stage regeneration | 1,000 | 813 vs 1,000 calls, 236,716 vs 315,175 retained output tokens |

The G1 comparison leaves a Full advantage unestablished. The reductions of 18.7% in calls and 24.9% in retained output tokens apply to the final stage after diagnostics.

| G1 arm | F1 | EM |
|---|---:|---:|
| B0 | 0.701944 | 0.568000 |
| B1 | 0.713016 | 0.580000 |
| B2 | 0.718508 | 0.584000 |
| B3 | 0.774367 | 0.634000 |
| B4 | 0.725837 | 0.594000 |
| B5 | 0.774367 | 0.634000 |
| B6 | 0.773780 | 0.634000 |
| B7 | 0.773780 | 0.634000 |

## Figure 4 paired decomposition

| Cohort | Mean benefit (pp) | Mean loss magnitude (pp) | Net (pp) |
|---|---:|---:|---:|
| Full development (7,405) | 6.18 | 2.37 | 3.81 |
| G3 efficiency cohort (1,000) | 4.92 | 2.45 | 2.46 |

The G3 conditional groups describe changes in the retained candidate relative to its diagnostic baseline. Their F1 changes are +3.03 pp (813 no-trigger examples), −8.61 pp (39 lexical-only), +2.01 pp (131 relevance-only), and approximately 0 pp (17 dual-trigger).

## Minimum data required for exact score-based reproduction

| Analysis | Rows | Minimum fields |
|---|---:|---|
| Full development intervals and paired benefit/loss | 7,405 | Stable unique question ID, diagnostic and selective official F1 and EM on the same question. Preserve frozen row order to replay the registered bootstrap. |
| G1 quality and ablation intervals | 500 | Stable unique question ID, F1 and EM for each of B0 through B7, and frozen row order. |
| G3 costs and Figure 4 | 1,000 | Stable unique question ID, diagnostic and retained candidate F1, selection flag and retained candidate output tokens. Include paired EM for Table 1 quality, response duration for Table 1 time, and recorded L/S history for the Figure 4 groups. |

The identifiers and scores must refer to the registered cohorts. Recomputing official scores from scratch additionally requires the paired predictions and reference answers. Policy cost reconstruction additionally needs the applicable cost records. Access to retained materials may be requested from the corresponding author and depends on applicable permissions. The full historical request and response archive cannot be reproduced from these inputs.

[Frozen CLI and statistical conventions](../REPRODUCIBILITY.md)
