import unittest
from pathlib import Path

import pandas as pd


class ABTestingDataQualityTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.read_csv(Path("data/marketing_ab.csv"))

    def test_required_columns_exist(self):
        required = {
            "user_id",
            "variant",
            "converted",
            "total_ads",
            "most_ads_day",
            "most_ads_hour",
        }
        self.assertTrue(required.issubset(self.data.columns))

    def test_experiment_groups_are_valid(self):
        self.assertGreater(len(self.data), 100000)
        self.assertEqual(
            set(self.data["variant"].unique()),
            {"Ad Campaign", "Public Service Announcement"},
        )
        self.assertGreater(self.data["converted"].mean(), 0)
        self.assertTrue((self.data["total_ads"] >= 0).all())


if __name__ == "__main__":
    unittest.main()
