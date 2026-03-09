from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from zpe_video.codec import decode_sequence, encode_sequence
from zpe_video.constants import GATE_SEEDS
from zpe_video.fixtures import generate_proxy_corpus
from zpe_video.metrics import sha256_file


class CodecTests(unittest.TestCase):
    def test_encode_deterministic_hash(self) -> None:
        corpus = generate_proxy_corpus(seed=GATE_SEEDS["B"])
        sequence = corpus["virat_proxy"]
        with tempfile.TemporaryDirectory() as td:
            p1 = Path(td) / "a.zpvid"
            p2 = Path(td) / "b.zpvid"
            encode_sequence(sequence, str(p1), seed=GATE_SEEDS["B"])
            encode_sequence(sequence, str(p2), seed=GATE_SEEDS["B"])
            self.assertEqual(sha256_file(str(p1)), sha256_file(str(p2)))

    def test_decode_malformed_stream_no_uncaught_exception(self) -> None:
        corpus = generate_proxy_corpus(seed=GATE_SEEDS["B"])
        sequence = corpus["virat_proxy"]
        with tempfile.TemporaryDirectory() as td:
            stream_path = Path(td) / "orig.zpvid"
            encode_sequence(sequence, str(stream_path), seed=GATE_SEEDS["B"])
            blob = bytearray(stream_path.read_bytes())
            if len(blob) > 120:
                blob = blob[:-80]
            bad_path = Path(td) / "bad.zpvid"
            bad_path.write_bytes(bytes(blob))
            result = decode_sequence(str(bad_path), tolerate_corruption=True)
            # fatal_error is reserved for decoder-level crashes.
            self.assertIsNone(result.fatal_error)
            self.assertTrue(result.errors)


if __name__ == "__main__":
    unittest.main()
