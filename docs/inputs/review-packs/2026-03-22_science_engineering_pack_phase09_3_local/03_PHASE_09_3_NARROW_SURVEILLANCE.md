# Phase 09.3 Narrow Surveillance Probe

## Why This Phase Existed

The lane had already bounded:

- scalar control-plane routing
- richer temporal routing
- primitive-layered routing

The honest next move was to test whether narrowing the surface could expose a real wedge if it existed.

## Surface Definition

Selected cohort:

- `VIRAT_S_010204_04_000646_000754`
- `VIRAT_S_010200_00_000060_000218`
- `VIRAT_S_010203_06_000620_000760`
- `VIRAT_S_010204_01_000072_000225`

Why these:

- they were the four sparsest available facility-event clips on the repo-owned VIRAT candidate surface
- facility-event coverage ranged from about `3.11%` to `5.95%`
- this kept the evaluator narrow instead of saturating it with always-on event time

## Result

The surface is real but mixed.

Per-clip delta separation ratio:

- `010204_04`: `1.25x`
- `010200_00`: `1.08x`
- `010203_06`: `0.75x`
- `010204_01`: `0.93x`

So:

- two clips show positive separation
- two clips do not

That clip heterogeneity is the key `09.3` discovery.

## Verdict

`bounded_signal_only`

Narrowing to sparse facility events was the right thought. The current delta rule still does not become a selective surveillance wedge there.
