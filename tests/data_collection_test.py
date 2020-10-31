import sys
sys.path.append("..")

import unittest
import pandas as pd

from data_collection.collector import DataCollector

class TestQueries(unittest.TestCase):
    def test_inference_collection(self):
        addresses = ['0x00009277775ac7d0d59eaad8fee3d10ac6c805e8','0x0002bda54cb772d040f779e88eb453cac0daa244']
        collector = DataCollector(inference=True)
        df = collector.main(inference_addresses=addresses)

        print(len(df))
        assert len(df) == 2