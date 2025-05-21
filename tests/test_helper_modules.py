import os
import pandas as pd
import unittest

from src.analyzer import sign_flip, column_matching, row_comparison, report_generator

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')

class TestHelperModules(unittest.TestCase):
    def setUp(self):
        self.excel_df = pd.read_csv(os.path.join(FIXTURES, 'excel_data.csv'))
        self.sql_df = pd.read_csv(os.path.join(FIXTURES, 'sql_data.csv'))

    def test_sign_flip_apply(self):
        val = sign_flip.apply(100, '1234-5678', ['1234-5678'])
        self.assertEqual(val, -100.0)
        self.assertFalse(sign_flip.should_flip('9999-0000', ['1234-5678']))

    def test_column_matching(self):
        mapping = column_matching.find_matching_columns(self.excel_df.columns, self.sql_df.columns)
        self.assertEqual(len(mapping), 3)
        self.assertEqual(mapping[0]['excel_column'], 'Center')

    def test_row_comparison(self):
        excel_series = self.excel_df['Amount']
        sql_series = self.sql_df['Amount']
        acct_series = self.excel_df['CAReportName']
        res = row_comparison.compare_series(excel_series, sql_series, acct_series, sign_flip_accounts=['1234-5678'])
        self.assertEqual(res['mismatch_count'], 0)

    def test_report_generator(self):
        comparison_results = {
            'summary': {'mismatch_percentage': 0, 'matching_cells': 3, 'total_cells': 3},
            'row_counts': {'excel': 2, 'sql': 2, 'matched': 2}
        }
        report = report_generator.generate_report('Sheet1', comparison_results, ['1234-5678'])
        self.assertIn('PERFECT MATCH', report)
        self.assertIn('Sign Flip Accounts Applied', report)

    def test_api_compare_and_report(self):
        from src.analyzer.api import compare_and_report
        results, report = compare_and_report("Sheet1", self.excel_df, self.sql_df, ["1234-5678"])
        self.assertTrue(results["summary"]["overall_match"])
        self.assertIn("PERFECT MATCH", report)

if __name__ == '__main__':
    unittest.main()
