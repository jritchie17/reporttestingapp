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
        self.assertIn('Issue', df.columns)

    def test_identify_account_discrepancies(self):
        discrepancies = self.engine.identify_account_discrepancies(self.excel_df, self.sql_df)
        self.assertFalse(discrepancies.empty)
        row = discrepancies.iloc[0]
        self.assertEqual(row['Center'], 1)
        self.assertEqual(row['Account'], '1234-5678')
        self.assertAlmostEqual(row['Variance'], 200)
        self.assertIn('Severity', discrepancies.columns)
        self.assertEqual(row['Severity'], 'major')

        self.engine.set_sign_flip_accounts(['1234-5678'])
        discrepancies_flip = self.engine.identify_account_discrepancies(self.excel_df, self.sql_df)
        self.assertTrue(discrepancies_flip.empty)

    def test_explain_variances(self):
        discrepancies = self.engine.identify_account_discrepancies(self.excel_df, self.sql_df)
        messages = self.engine.explain_variances(discrepancies)
        self.assertEqual(len(messages), len(discrepancies))
        self.assertIn('Variance of', messages[0])

    def test_compare_results_include_severity(self):
        results = self.engine.compare_dataframes(self.excel_df, self.sql_df)
        self.assertIn('discrepancy_severity', results)
        self.assertIn('major', results['discrepancy_severity'])

    def test_key_whitespace_and_case_normalization(self):
        excel_df = pd.DataFrame({
            'Center': [1],
            'CAReportName': ['Acct A '],
            'Amount': [100]
        })
        sql_df = pd.DataFrame({
            'Center': [1],
            'CAReportName': ['acct a'],
            'Amount': [100]
        })
        engine = ComparisonEngine()
        results = engine.compare_dataframes(excel_df, sql_df)
        self.assertEqual(results['row_counts']['matched'], 1)
        detailed = engine.generate_detailed_comparison_dataframe('Sheet1', excel_df, sql_df)
        self.assertTrue((detailed['Result'] == 'Match').all())

    def test_careportname_column_variations(self):
        excel_df = pd.DataFrame({
            'Center': [1],
            'CaReportName': ['Acct A'],
            'Amount': [100]
        })
        sql_df = pd.DataFrame({
            'Center': [1],
            'CA Report Name': ['Acct A'],
            'Amount': [100]
        })
        engine = ComparisonEngine()
        df = engine.generate_detailed_comparison_dataframe('Sheet1', excel_df, sql_df)
        self.assertIn('CAReport Name', df.columns)
        self.assertEqual(df['CAReport Name'].iloc[0], 'Acct A')
