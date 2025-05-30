import unittest
import pandas as pd
from tests.qt_stubs import patch_qt_modules


class TestRemoveDuplicateHeaderRow(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()

    def test_duplicate_header_row_removed(self):
        from src.ui.excel_viewer import ExcelViewer

        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 1,
            'description': ''
        }

        # Row 0 is the header, row 1 repeats the header which should be removed
        df = pd.DataFrame([
            ['A', 'B', 'C'],
            ['A', 'B', 'C'],
            ['desc', '1', '2'],
        ])

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        # After removing the duplicate header row we should only have one data row
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(list(cleaned.columns), ['Sheet_Name', 'A', 'B', 'C'])
        self.assertEqual(cleaned.iloc[0, 1], 'desc')
        self.assertEqual(cleaned.iloc[0, 2], 1.0)
        self.assertEqual(cleaned.iloc[0, 3], 2.0)


if __name__ == '__main__':
    unittest.main()
