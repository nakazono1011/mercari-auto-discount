import unittest

from crawler.mercari.discount_crawler import extract_update_time_text, should_skip_item


class ExtractUpdateTimeTextTest(unittest.TestCase):
    def test_uses_time_text_even_when_fewer_than_four_icons(self):
        texts = ["12", "3", "2日前"]
        self.assertEqual(extract_update_time_text(texts), "2日前")

    def test_picks_time_pattern_instead_of_fixed_index(self):
        texts = ["1", "0", "3時間前", ">"]
        self.assertEqual(extract_update_time_text(texts), "3時間前")

    def test_returns_empty_when_no_texts(self):
        self.assertEqual(extract_update_time_text([]), "")


class ShouldSkipItemTest(unittest.TestCase):
    def test_skips_item_updated_hours_ago(self):
        self.assertTrue(should_skip_item("靴", "2時間前"))

    def test_does_not_skip_item_updated_days_ago(self):
        self.assertFalse(should_skip_item("靴", "3日前"))

    def test_skips_starred_title(self):
        self.assertTrue(should_skip_item("★セール", "3日前"))


if __name__ == "__main__":
    unittest.main()
