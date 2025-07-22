import os
import unittest
import pandas as pd
from tests.qt_stubs import patch_qt_modules

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')

class TestCSVCleaning(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()

    def test_duplicate_header_row_csv(self):
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 1,
            'description': ''
        }
        path = os.path.join(FIXTURES, 'duplicate_header_rows.csv')
        df = pd.read_csv(path, header=None)
        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(list(cleaned.columns), ['Sheet_Name', 'A', 'A_1', 'B'])
        self.assertEqual(cleaned.iloc[0, 1], 'val1')
        self.assertEqual(cleaned.iloc[1, 2], 3.0)

    def test_corp_soo_zero_rows_csv(self):
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_type = 'Corp SOO'
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 2,
            'description': ''
        }
        path = os.path.join(FIXTURES, 'corp_soo_zero_rows.csv')
        df = pd.read_csv(path, header=None)
        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(list(cleaned.columns), ['A', 'B', 'C'])
        self.assertEqual(cleaned.iloc[0].tolist(), ['acct1', 1, 2.0])
        self.assertEqual(cleaned.iloc[1].tolist(), ['acct2', 0, 0.0])

if __name__ == '__main__':
    unittest.main()
