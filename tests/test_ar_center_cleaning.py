import unittest
import pandas as pd
from tests.qt_stubs import patch_qt_modules

class TestARCenterCleaning(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()

    def test_careportname_prefixed_with_sheet(self):
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 1,
            'description': ''
        }
        viewer.report_type = 'AR Center'

        df = pd.DataFrame([
            ['CAReportName', 'Val1'],
            ['0 - 30 days', 1],
            ['31 - 60 days', 2]
        ])

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'facility')
        self.assertIsNotNone(cleaned)
        self.assertEqual(list(cleaned.columns), ['CAReportName', 'Val1'])
        self.assertEqual(cleaned.iloc[0].tolist(), ['Facility: 0 - 30 days', 1.0])
        self.assertEqual(cleaned.iloc[1].tolist(), ['Facility: 31 - 60 days', 2.0])

    def test_comparison_with_prefixed_sql(self):
        """Comparison should succeed when SQL rows are prefixed like Excel."""
        from src.ui.excel_viewer import ExcelViewer
        from src.analyzer.comparison_engine import ComparisonEngine

        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 1,
            'description': ''
        }
        viewer.report_type = 'AR Center'

        df = pd.DataFrame([
            ['CAReportName', 'Val1'],
            ['0 - 30 days', 1],
            ['31 - 60 days', 2]
        ])

        excel_df = ExcelViewer._clean_dataframe(viewer, df, 'facility')

        sql_df = pd.DataFrame({
            'CAReportName': ['0 - 30 days', '31 - 60 days'],
            'Val1': [1, 2]
        })
        sql_df['CAReportName'] = sql_df['CAReportName'].apply(
            lambda v: f"Facility: {v}"
        )

        engine = ComparisonEngine()
        result = engine.compare_dataframes(excel_df, sql_df)
        self.assertTrue(result['summary']['overall_match'])

if __name__ == '__main__':
    unittest.main()
