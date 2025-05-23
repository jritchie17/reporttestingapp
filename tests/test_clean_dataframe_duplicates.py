import os
import sys
import types
import unittest

from tests.qt_stubs import patch_qt_modules

import pandas as pd




class TestCleanDataframeDuplicates(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()

    def test_duplicate_headers_converted(self):
        from src.ui.excel_viewer import ExcelViewer

        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 1,
            'description': ''
        }

        df = pd.DataFrame([
            ['A', 'A', 'B'],
            ['desc', '1', '2'],
            ['desc2', '3', '4']
        ])

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        self.assertEqual(list(cleaned.columns), ['Sheet_Name', 'A', 'A_1', 'B'])
        self.assertEqual(cleaned.iloc[0, 2], 1.0)
        self.assertEqual(cleaned.iloc[1, 2], 3.0)
        self.assertTrue(pd.api.types.is_float_dtype(cleaned['A_1']))


if __name__ == '__main__':
    unittest.main()
