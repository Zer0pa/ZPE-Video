# Pod Shutdown And Re-Engagement

## Before Pod Shutdown

Nothing in the current `09.3.1` lane requires the pod to stay alive.

Make sure the Mac retains these exact surfaces:

- workspace root: `/Users/Zer0pa/ZPE/ZPE Video`
- local lab runtime: `zpe_video_lab/.venv-arm64/`
- current run-of-record: `zpe_video_lab/reports/phase9_3_1_portal_anchored_event_consumer/summary.json`
- baseline narrow-surface report: `zpe_video_lab/reports/phase9_3_narrow_surveillance_wedge/summary.json`
- current phase docs under `.gpd/phases/09.3.1-portal-anchored-primitive-event-consumer-on-sparse-facility-crossing/`

## What The Team Should Analyze

- is the `09.3.1` portal-local gain enough to justify one more bounded surveillance iteration?
- if yes, what tighter facility-crossing state contract should replace the current shallow threshold family?
- if no, what artifact class should replace surveillance triage as the next narrow wedge attempt?

## Re-Engagement Starting Point

When we resume, the shortest truthful restart path is:

1. read this pack
2. open the `09.3.1` report JSON
3. confirm whether the team wants Option `2` from `07_NEXT_EXPERIMENT_OPTIONS.md`
4. if yes, plan the next bounded portal-local primitive state machine phase

## Bottom Line

The pod can be shut down.

The current engineering truth is already local, already captured, and already packaged for team analysis.
