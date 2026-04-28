# Examples

Three runnable examples covering the public API. None require network
egress, a GPU, or datasets. All run on pure stdlib after `pip install`.

| Example | What it shows |
| ------- | ------------- |
| [`01_round_trip.py`](01_round_trip.py) | Encode a receipt, hash it, round-trip decode. |
| [`02_cross_writer.py`](02_cross_writer.py) | Hand-rolled from-spec encoder produces byte-identical output to the library — this is the wedge. |
| [`03_file_round_trip.py`](03_file_round_trip.py) | Write a receipt to disk, verify CRC + expected hash on read. |

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Run all three

```bash
python examples/01_round_trip.py
python examples/02_cross_writer.py
python examples/03_file_round_trip.py
```

Expected output: the cross-writer script should print
`cross-writer wedge: VERIFIED`. If it does not, the commercial wedge of
this library is broken and the failure should be treated as a P0 bug.
