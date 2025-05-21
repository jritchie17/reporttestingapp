import os
import unittest
import pandas as pd
from src.analyzer.comparison_engine import ComparisonEngine

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')

class TestComparisonEngineSignFlip(unittest.TestCase):
    def setUp(self):
        self.excel_df = pd.read_csv(os.path.join(FIXTURES, 'excel_data.csv'))
        self.sql_df = pd.read_csv(os.path.join(FIXTURES, 'sql_data.csv'))
        self.engine = ComparisonEngine()

    def test_sign_flip(self):
        result_no_flip = self.engine.compare_dataframes(self.excel_df, self.sql_df)
        self.assertGreater(result_no_flip['summary']['mismatch_percentage'], 0)

        self.engine.set_sign_flip_accounts(['1234-5678'])
        result_flip = self.engine.compare_dataframes(self.excel_df, self.sql_df)
        self.assertEqual(result_flip['summary']['mismatch_percentage'], 0)
        self.assertTrue(result_flip['summary']['overall_match'])

    def test_detailed_dataframe_mismatch(self):
        sql_mod = self.sql_df.copy()
        sql_mod.loc[0, 'Amount'] = -90
        self.engine.set_sign_flip_accounts(['1234-5678'])
        df = self.engine.generate_detailed_comparison_dataframe('Sheet1', self.excel_df, sql_mod)
        self.assertIn('Does Not Match', df['Result'].values)

    def test_identify_account_discrepancies(self):
        discrepancies = self.engine.identify_account_discrepancies(self.excel_df, self.sql_df)
        self.assertFalse(discrepancies.empty)
        row = discrepancies.iloc[0]
        self.assertEqual(row['Center'], 1)
        self.assertEqual(row['Account'], '1234-5678')
        self.assertAlmostEqual(row['Variance'], 200)

        self.engine.set_sign_flip_accounts(['1234-5678'])
        discrepancies_flip = self.engine.identify_account_discrepancies(self.excel_df, self.sql_df)
        self.assertTrue(discrepancies_flip.empty)

    def test_explain_variances(self):
        discrepancies = self.engine.identify_account_discrepancies(self.excel_df, self.sql_df)
        messages = self.engine.explain_variances(discrepancies)
        self.assertEqual(len(messages), len(discrepancies))
        self.assertIn('Variance of', messages[0])
