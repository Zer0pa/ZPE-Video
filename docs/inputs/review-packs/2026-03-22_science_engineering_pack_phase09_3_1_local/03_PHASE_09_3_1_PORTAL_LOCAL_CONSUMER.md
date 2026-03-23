# Phase 09.3.1 Portal-Local Consumer

## Why This Phase Existed

`09.3` proved that the right owned narrow surface was sparse facility-event surveillance, but that full-frame packet delta was too blunt there.

So `09.3.1` asked a sharper question:

- if the surface stays fixed,
- and the aperture tightens around the event-linked actor portal,
- does the packet become materially more selective?

## Surface Definition

Selected cohort:

- `VIRAT_S_010204_04_000646_000754`
- `VIRAT_S_010200_00_000060_000218`
- `VIRAT_S_010203_06_000620_000760`
- `VIRAT_S_010204_01_000072_000225`

Event scope:

- `9` facility events
- `59` portal-local samples total
- `27` positive samples
- `32` negative samples

Portal rule:

- use VIRAT `events`, `objects`, and `mapping`
- link each facility event to its actor track
- take the union of that actor’s boxes across the event
- pad that union locally at runtime

Critical boundary:

- the box is the aperture only
- the score comes from primitive-local state inside the crop

## Best Rules

Best single-feature rule:

- `stroke_delta >= 0.006493506493506494`
- `96.30%` recall
- `31.25%` suppression

Best aggregate rule:

- `stroke_delta >= 0.006493506493506494 AND point_delta <= 0.1233644859813084`
- `96.30%` recall
- `34.38%` suppression

## Per-Clip Breakdown Under The Global Rule

- `VIRAT_S_010204_04_000646_000754`: `100%` recall, `50.00%` suppression
- `VIRAT_S_010200_00_000060_000218`: `100%` recall, `25.00%` suppression
- `VIRAT_S_010203_06_000620_000760`: `100%` recall, `41.67%` suppression
- `VIRAT_S_010204_01_000072_000225`: `88.89%` recall, `25.00%` suppression

## Holdout Check

Leave-one-clip-out behavior stays unstable.

- multiple holdouts collapse to `66.67%` recall under the best training rule
- the remaining holdout retains recall but only at weak suppression

That is why the phase closes as `bounded_signal_only` despite the aggregate improvement.

## Verdict

`09.3.1` is the strongest narrow sparse-facility signal yet.

It also proves the remaining problem is not “no local signal exists.” The problem is that the current portal-local consumer does not yet survive clip changes well enough to count as a wedge.
