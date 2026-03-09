# FAQ

## Why is this repo private?

Because the current staged truth is not ready for public release.

## Is the lane currently green?

No. The latest known workspace snapshot says `NO-GO`.

## Why is there a proof snapshot if the repo is not green?

Because evidence custody matters. The staged proof subset preserves the current known state without pretending it is a clean run-of-record.

## Why are the datasets not bundled?

They are too large and do not belong in the repo boundary.

## Why is Gate A still a known problem?

Its inputs were historically machine-local. This repo normalizes the path logic, but the actual input files are still not bundled here.

## Where do those Gate A inputs belong?

Place them under `docs/inputs/` or supply them via:

- `ZPE_VIDEO_NET_NEW_PACK_MD`
- `ZPE_VIDEO_NET_NEW_PACK_PDF`
- `ZPE_VIDEO_GAP_CLOSURE_MD`

