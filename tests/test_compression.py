import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

from decoder import decompress
from encoder import compress


class CompressionRoundTripTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def write_text(self, file_name, content):
        file_path = os.path.join(self.temp_dir.name, file_name)
        with open(file_path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return file_path

    def write_seed(self, file_name, patterns):
        file_path = os.path.join(self.temp_dir.name, file_name)
        with open(file_path, "w", encoding="utf-8") as handle:
            json.dump(patterns, handle)
        return file_path

    def round_trip(self, source_text, patterns):
        source_file = self.write_text("input.py", source_text)
        compressed_file = os.path.join(self.temp_dir.name, "output.lzw")
        restored_file = os.path.join(self.temp_dir.name, "restored.py")
        seed_file = self.write_seed("seed.json", patterns)

        with redirect_stdout(StringIO()):
            compress(source_file, compressed_file, seed_file)
            decompress(compressed_file, restored_file, seed_file)

        with open(restored_file, "r", encoding="utf-8") as handle:
            return handle.read(), os.path.getsize(compressed_file)

    def test_round_trip_with_seed_dictionary(self):
        source_text = "import requests\n\nfor _ in range(3):\n    print('test')\n"
        restored_text, _ = self.round_trip(source_text, ["import ", "requests", "print", "range("])
        self.assertEqual(restored_text, source_text)

    def test_round_trip_with_empty_seed_dictionary(self):
        source_text = "def example():\n    return 'abcabcabc'\n"
        restored_text, _ = self.round_trip(source_text, [])
        self.assertEqual(restored_text, source_text)

    def test_seeded_dictionary_does_not_expand_simple_repetitive_input(self):
        source_text = "import requests\nimport requests\nimport requests\n"
        _, baseline_size = self.round_trip(source_text, [])
        _, seeded_size = self.round_trip(source_text, ["import requests", "requests"])
        self.assertLessEqual(seeded_size, baseline_size)


if __name__ == "__main__":
    unittest.main()