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
        self.assertIn('CAReportName', df.columns)
        self.assertEqual(df['CAReportName'].iloc[0], 'Acct A')

    def test_pivot_results_single_row_per_record(self):
        excel_df = pd.DataFrame({
            'Center': [1, 2],
            'CAReportName': ['Acct A', 'Acct B'],
            'Amount': [100, 200],
            'Quantity': [5, 10]
        })
        sql_df = pd.DataFrame({
            'Center': [1, 2],
            'CAReportName': ['Acct A', 'Acct B'],
            'Amount': [100, 200],
            'Quantity': [5, 10]
        })
        engine = ComparisonEngine()
        df = engine.generate_detailed_comparison_dataframe(
            'Sheet1', excel_df, sql_df, pivot_results=True
        )
        self.assertEqual(len(df), 2)
        self.assertIn('Amount Excel', df.columns)
        self.assertIn('Quantity Database', df.columns)

    def test_key_column_synonyms(self):
        excel_df = pd.DataFrame({
            'Facility': [1],
            'Account': ['1234-5678'],
            'Amount': [100]
        })
        sql_df = pd.DataFrame({
            'Facility Number': [1],
            'Account Number': ['1234-5678'],
            'Amount': [100]
        })
        engine = ComparisonEngine()
        df = engine.generate_detailed_comparison_dataframe('Sheet1', excel_df, sql_df)
        self.assertTrue((df['Result'] == 'Match').all())

    def test_key_column_keyword_detection(self):
        excel_df = pd.DataFrame({
            'My Facility ID': [1],
            'Acct - Desc': ['1234-5678'],
            'Amount': [100]
        })
        sql_df = pd.DataFrame({
            'Center_ID': [1],
            'Account Number': ['1234-5678'],
            'Amount': [100]
        })
        engine = ComparisonEngine()
        df = engine.generate_detailed_comparison_dataframe('Sheet1', excel_df, sql_df)
        self.assertTrue((df['Result'] == 'Match').all())

    def test_empty_sql_dataframe_returns_empty(self):
        empty_sql = pd.DataFrame(columns=self.sql_df.columns)
        df = self.engine.generate_detailed_comparison_dataframe(
            'Sheet1', self.excel_df, empty_sql
        )
        self.assertTrue(df.empty)

    def test_missing_key_columns_raise(self):
        excel_df = pd.DataFrame({'Amount': [100]})
        sql_df = pd.DataFrame({'Amount': [100]})
        column_mappings = {
            0: {'excel_column': 'Center', 'sql_column': 'Center', 'match_score': 1.0},
            1: {'excel_column': 'CAReportName', 'sql_column': 'CAReportName', 'match_score': 1.0},
            2: {'excel_column': 'Amount', 'sql_column': 'Amount', 'match_score': 1.0},
        }
        with self.assertRaises(ValueError):
            self.engine.generate_detailed_comparison_dataframe(
                'Sheet1', excel_df, sql_df, column_mappings=column_mappings
            )

    def test_generate_comparison_report_content(self):
        self.engine.set_sign_flip_accounts(['1234-5678'])
        results = self.engine.compare_dataframes(self.excel_df, self.sql_df)
        df = self.engine.generate_detailed_comparison_dataframe('Sheet1', self.excel_df, self.sql_df)
        report = self.engine.generate_comparison_report('Sheet1', results, mismatches_df=df)
        self.assertIn('PERFECT MATCH', report)
        self.assertIn('Per-Column Mismatches', report)
        self.assertIn('## Mismatches', report)
