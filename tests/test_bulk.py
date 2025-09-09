import os
import glob
import unittest

import notam


class TestBulkParsing(unittest.TestCase):
    """Parse every NOTAM test data file to ensure the parser doesn't regress.

    Each *.txt file in tests/test_data is assumed to contain one complete NOTAM.
    The test simply asserts parsing succeeds and yields a Notam instance with an id.
    """

    def test_all_notam_files_parse(self):
        data_dir = os.path.join(os.path.dirname(__file__), "test_data")
        pattern = os.path.join(data_dir, "*.txt")
        files = sorted(glob.glob(pattern))
        self.assertTrue(files, "No NOTAM test data files found")
        for path in files:
            fname = os.path.basename(path)
            # Allow easily parking known broken samples by prefixing filename with 'skip_'
            if fname.startswith("skip_"):
                continue
            with self.subTest(file=fname):
                with open(path, "r", encoding="utf-8") as fh:
                    content = fh.read().strip()
                self.assertTrue(content, "File is empty")
                try:
                    n = notam.Notam.from_str(content)
                except Exception as e:  # Catch any parse failure and surface filename
                    self.fail(f"Parsing failed for {fname}: {e}")
                self.assertIsInstance(n, notam.Notam)
                self.assertIsNotNone(n.notam_id, f"Parsed NOTAM missing id in {fname}")
                # test decoding
                self.assertTrue(n.decoded(), f"Decoding failed for {fname}")


if __name__ == "__main__":
    unittest.main()
