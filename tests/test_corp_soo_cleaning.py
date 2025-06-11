import unittest
import pandas as pd
from tests.qt_stubs import patch_qt_modules

class TestCorpSOOCleaning(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()

    def test_corp_soo_clean(self):
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 2,
            'description': ''
        }
        viewer.report_type = 'Corp SOO'

        df = pd.DataFrame([
            ['A','B','C'],
            ['acct1','', ''],
            ['acct2',1,2],
            ['acct2',0,'foo'],
            ['', '', ''],
            ['acct3',0,0]
        ])

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        self.assertEqual(list(cleaned.columns), ['A','B','C'])
        self.assertEqual(len(cleaned), 3)
        self.assertEqual(cleaned.iloc[0].tolist(), ['acct2', 1.0, 2.0])
        self.assertEqual(cleaned.iloc[1].tolist(), ['acct2', 0, 'foo'])
        self.assertEqual(cleaned.iloc[2].tolist(), ['acct3', 0, 0.0])

    def test_text_column_not_dropped(self):
        """Purely textual columns should be preserved when cleaning."""
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 2,
            'description': ''
        }
        viewer.report_type = 'Corp SOO'

        df = pd.DataFrame([
            ['CAReportName', 'Val1', 'Val2'],
            ['TextA', 0, 0],
            ['TextB', 1, 2]
        ])

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        self.assertEqual(list(cleaned.columns), ['CAReportName', 'Val1', 'Val2'])
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned.iloc[0].tolist(), ['TextA', 0, 0.0])
        self.assertEqual(cleaned.iloc[1].tolist(), ['TextB', 1, 2.0])

    def test_zero_numeric_rows_preserved(self):
        """Rows with text in the first column and zero numeric values remain."""
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 2,
            'description': ''
        }
        viewer.report_type = 'Corp SOO'

        df = pd.DataFrame([
            ['A', 'B', 'C'],
            ['RowZero', 0, 0],
            ['RowData', 1, 2]
        ])

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned.iloc[0].tolist(), ['RowZero', 0, 0.0])
        self.assertEqual(cleaned.iloc[1].tolist(), ['RowData', 1, 2.0])

if __name__ == '__main__':
    unittest.main()
