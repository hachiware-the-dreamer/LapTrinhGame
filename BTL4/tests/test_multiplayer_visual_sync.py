import unittest

from scripts.screens import _card_signature_sort_key


class MultiplayerVisualSyncTest(unittest.TestCase):
    def test_card_signature_sort_key_handles_none_values(self) -> None:
        signatures = [
            (None, "wild", None, "red"),
            ("red", "number", 7, None),
            ("blue", "number", 0, None),
            (None, "wild_draw_four", None, None),
        ]

        ordered = sorted(signatures, key=_card_signature_sort_key)

        self.assertEqual(len(ordered), 4)
        self.assertIn((None, "wild", None, "red"), ordered)
        self.assertIn(("red", "number", 7, None), ordered)


if __name__ == "__main__":
    unittest.main()
