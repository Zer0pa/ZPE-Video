# Phase 09.3.2 Key Tables

## Full-Surface Best Defended Result

| Surface | Family | Recall | Suppression | Result |
| --- | --- | ---: | ---: | --- |
| Full sparse VIRAT surface | `stroke_plus_point_state_machine` | `26/27 = 96.30%` | `12/32 = 37.50%` | meaningful lift, still below gate |
| `09.3.1` reference | flat portal-local pair rule | `26/27 = 96.30%` | `11/32 = 34.38%` | prior defended point |

## Per-Clip Recall Under Full-Surface Best Defended Rule

| Clip | Recall | Suppression |
| --- | ---: | ---: |
| `VIRAT_S_010200_00_000060_000218` | `5/6 = 83.33%` | `2/4 = 50.00%` |
| `VIRAT_S_010203_06_000620_000760` | `9/9 = 100.00%` | `4/12 = 33.33%` |
| `VIRAT_S_010204_01_000072_000225` | `9/9 = 100.00%` | `5/12 = 41.67%` |
| `VIRAT_S_010204_04_000646_000754` | `3/3 = 100.00%` | `1/4 = 25.00%` |

## Leave-One-Clip-Out Recall

| Held-Out Clip | Recall | Suppression |
| --- | ---: | ---: |
| `VIRAT_S_010200_00_000060_000218` | `5/6 = 83.33%` | `2/4 = 50.00%` |
| `VIRAT_S_010203_06_000620_000760` | `6/9 = 66.67%` | `6/12 = 50.00%` |
| `VIRAT_S_010204_01_000072_000225` | `9/9 = 100.00%` | `3/12 = 25.00%` |
| `VIRAT_S_010204_04_000646_000754` | `2/3 = 66.67%` | `1/4 = 25.00%` |

## Narrowed Diagnostic Splits

| Split | Recall | Suppression | Status |
| --- | ---: | ---: | --- |
| entering-only | `18/18 = 100.00%` | `9/24 = 37.50%` | below split gate, LOOCV still fails |
| exiting-only | `9/9 = 100.00%` | `0/8 = 0.00%` | dead as a wedge |

## Family Ledger

| Family | Safe Candidates | Best Safe Recall | Best Safe Suppression |
| --- | ---: | ---: | ---: |
| `stroke_plus_point_state_machine` | `4` | `96.30%` | `37.50%` |
| `stroke_only_state_machine` | `4` | `96.30%` | `34.38%` |
| `stroke_plus_point_hysteresis_state_machine` | `7` | `96.30%` | `34.38%` |
| `ablation_without_stroke_delta` | `6` | `100.00%` | `12.50%` |
| `phase_tightened_state_machine` | `0` | `-` | `-` |
| `stroke_plus_count_guard_state_machine` | `0` | `-` | `-` |
