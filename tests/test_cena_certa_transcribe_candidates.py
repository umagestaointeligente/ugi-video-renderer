from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from cena_certa_transcribe_candidates import offline_guard, cues, srt_time


class TranscriptionTests(unittest.TestCase):
    def test_network_and_telemetry_component_are_forbidden(self):
        for event, args in [('socket.connect', (None, ('example.invalid', 443))),
                            ('socket.getaddrinfo', ('example.invalid',)),
                            ('import', ('onnxruntime',)),
                            ('import', ('onnxruntime.capi',))]:
            with self.assertRaises(RuntimeError):
                offline_guard(event, args)
        offline_guard('import', ('numpy',))

    def test_timestamp_rounding_carries_across_minute(self):
        self.assertEqual(srt_time(59.9996), '00:01:00,000')

    def test_cues_preserve_words_and_source_timestamps(self):
        words = [dict(word=' palavra', start=i*0.4, end=i*0.4+0.3) for i in range(19)]
        groups = list(cues(words))
        self.assertEqual([w for group in groups for w in group], words)
        self.assertTrue(all(len(g) <= 6 for g in groups))
        self.assertTrue(all(len(' '.join(w['word'].strip() for w in g)) <= 31 for g in groups))


if __name__ == '__main__':
    unittest.main()
