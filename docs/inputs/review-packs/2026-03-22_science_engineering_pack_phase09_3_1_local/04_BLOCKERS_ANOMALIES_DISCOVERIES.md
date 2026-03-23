# Blockers, Anomalies, And Discoveries

## Main Blockers

- The local rule still misses the `>= 50%` suppression gate by a wide margin.
- Cross-clip stability is still weak enough to break the defended recall floor on one selected clip.
- Leave-one-clip-out splits still collapse, so the current signal is not yet robust.
- The artifact is still being consumed by a relatively shallow rule family rather than a richer portal-local state machine.

## Anomalies

- The same global portal-local rule behaves very differently across clips on the same narrow surface.
- Some portal events show strong stroke-change separation while others stay nearly flat or invert.
- The best aggregate rule still uses a very simple two-term structure, which suggests the next gain may come from event-phase logic rather than from larger threshold ladders.

## Discoveries

- The P8-aligned correction was real: keeping annotations as aperture only and scoring primitive-local state materially improved the narrow-surface result.
- `stroke_delta` is the strongest simple primitive-local signal on this surface.
- The sparse facility-event surface is not dead; it is stronger than `09.3` and still bounded.
- The engineering question is now stability and event-phase structure, not whether any signal exists at all.

## What These Mean

The next move should not be “smaller threshold steps.”

The blocker is now:

- how to stabilize and structure the portal-local primitive consumer across clips,

not:

- whether to keep rescoring the old full-frame packet.
