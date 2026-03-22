# Insights, Discoveries, And Anomalies

Date: `2026-03-22`

## Insights

- The primitive-native structural packet is still the correct central object. The recent work did not disprove the packet; it disproved specific scorer and carrier interpretations layered on top of it.
- Carrier separation is real. Both `09.1` and `09.2` show that flat treatment of the stream is too coarse.
- Richer temporal logic helps, but only boundedly. Memory, locality, hysteresis, and explicit layers all moved the frontier without closing it.

## Discoveries

- The earlier Phase 9 family established that sparse branch-like negative-space descriptors can recover topology in a way graph-only and radial signatures did not.
- The Seedance analogy is useful only when translated into deterministic carrier contracts and then judged harshly. As soon as the persistence carrier fails to beat a simpler temporal-only split, the analogy loses authority.
- The layered scorer can preserve high retention while suppressing more work than the older conservative candidate, but it does not survive the near-half regime. That means it improves routing discipline more than it improves wedge strength.

## Anomalies

- `09.1` summary drift: `/Users/Zer0pa/ZPE/ZPE Video/.gpd/phases/09.1-seedance-informed-video-subchannel-factorization-hypothesis/09.1-01-SUMMARY.md` says the phase closes as `bounded_signal_only` with one set of aggregate totals, while `/Users/Zer0pa/ZPE/ZPE Video/zpe_video_lab/reports/phase9_1_video_subchannel_factorization/summary.json` records verdict `flat_lane_still_dominant` with different aggregate totals and clip count. The JSON plus the explicit decision note should be treated as authoritative.
- `09-09` versus `09.2` safe-side reference drift: the `09-09` narrative summary lists lower best `>= 95%` suppression values than the prior-safe-side anchors cited inside the `09.2` comparison section. That means at least one narrative layer is lagging or selecting a different comparison slice.
- `09.2` cost anomaly: the layered scorer improved the safe frontier only marginally while packet extraction mean cost rose to `374.57 ms` in the run-of-record, compared with `200.32 ms` on the `09-09` temporal rerun.
- Repo boundary anomaly: the canonical research story lives partly outside the GitHub repo. That is workable for active lane execution but weak for handoff and audit unless bridged explicitly, which this pack is doing.

## Practical Reading Rule

When results conflict, trust:

1. run-of-record JSON
2. explicit decision note
3. narrative summary
