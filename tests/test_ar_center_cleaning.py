import unittest
import pandas as pd
from tests.qt_stubs import patch_qt_modules
import types
from unittest.mock import MagicMock


class DummySelector:
    def __init__(self, text):
        self._text = text

    def currentText(self):
        return self._text


class DummyStatusBar:
    def __init__(self):
        self.message = ""

    def showMessage(self, msg):
        self.message = msg

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

    def test_compare_results_with_prefixed_sql_rows(self):
        """MainWindow.compare_results should handle already-prefixed SQL."""
        from src.ui.excel_viewer import ExcelViewer
        from src.analyzer.comparison_engine import ComparisonEngine
        from src.analyzer.excel_analyzer import ExcelAnalyzer
        from src.ui.main_window import MainWindow

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

        analyzer = ExcelAnalyzer('dummy.xlsx')
        analyzer.sheet_names = ['facility']
        analyzer.sheet_data['facility'] = {'dataframe': excel_df}

        sql_df = pd.DataFrame({
            'CAReportName': ['Facility: 0 - 30 days', 'Facility: 31 - 60 days'],
            'Val1': [1, 2]
        })

        window = MainWindow.__new__(MainWindow)
        window.excel_analyzer = analyzer
        window.results_viewer = types.SimpleNamespace(
            has_results=lambda: True,
            get_dataframe=lambda: sql_df
        )
        window.comparison_engine = ComparisonEngine()
        window.report_selector = DummySelector('AR Center')
        window.sheet_selector = DummySelector('facility')
        window.status_bar = DummyStatusBar()
        window.logger = MagicMock()
        window.comparison_view = types.SimpleNamespace(
            set_report=lambda *a, **k: None,
            set_discrepancies=lambda *a, **k: None,
        )
        window.tab_widget = types.SimpleNamespace(setCurrentIndex=lambda *a, **k: None)
        window._select_sheets_for_comparison = lambda sheets: ['facility']
        window._generate_combined_comparison_report = lambda *a, **k: ('', pd.DataFrame())

        window.compare_results()

        results = window.comparison_results_by_sheet.get('facility')
        self.assertIsNotNone(results)
        self.assertGreater(results['row_counts']['matched'], 0)

if __name__ == '__main__':
    unittest.main()
