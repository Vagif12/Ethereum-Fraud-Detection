import sys
sys.path.append("..")

import unittest
import pandas as pd

from modelling.model import FraudDetector

df = pd.read_csv('https://raw.githubusercontent.com/Vagif12/Ethereum-Fraud-Detection/master/datasets/final_combined_dataset.csv')

class TestQueries(unittest.TestCase):

    def test_model(self):
        detector = FraudDetector(df)
        detector.train_model()
        test_f1_score = detector.evaluate()
        assert test_f1_score > 0.93