import sys
sys.path.append('../google_trendy')

import unittest
from google_trendy import *

class GoogleTrendsTest(unittest.TestCase):
    
    def test_init(self):
        trends = GoogleTrends()
        self.assertIsNotNone(trends)

    def test_get_trends(self):
        trends = GoogleTrends()
        trends.get_trends()
        self.assertGreater(len(trends.trends), 0)
    
    def test_daily_trends(self):
        trends = GoogleTrends()
        self.assertIsNotNone(trends.daily_trends())

    def test_trend_urls(self):
        trends = GoogleTrends()
        trends.get_trends()
        for id in trends.trend_ids:
            self.assertIn("http", trends.trend_url(id))

if __name__ == '__main__':
    unittest.main()

