import unittest
import pandas as pd
from tests.qt_stubs import patch_qt_modules


class TestMFRCleaning(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()

    def test_mfr_headers_prefixed(self):
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 4,
            'description': ''
        }
        viewer.report_type = 'SOO MFR'

        df = pd.DataFrame([
            ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S'],
            [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
        ])

        from PyQt6.QtWidgets import QInputDialog
        responses = iter([('May', True), ('2025', True)])
        QInputDialog.getItem = staticmethod(lambda *a, **k: next(responses))

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        expected = [
            'Sheet_Name','A','B','C',
            'May 2025 D','May 2025 E','May 2025 F','May 2025 G','May 2025 H','May 2025 I',
            'May 2024 J','May 2024 K','May 2024 L',
            'YTD May 2025 M','YTD May 2025 N','YTD May 2025 O','YTD May 2025 P',
            'YTD May 2024 Q','YTD May 2024 R','YTD May 2024 S'
        ]
        self.assertEqual(list(cleaned.columns), expected)

    def test_mfr_preclose_headers_prefixed(self):
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 4,
            'description': ''
        }
        viewer.report_type = 'MFR PreClose'

        df = pd.DataFrame([
            ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S'],
            [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
        ])

        from PyQt6.QtWidgets import QInputDialog
        responses = iter([('May', True), ('2025', True)])
        QInputDialog.getItem = staticmethod(lambda *a, **k: next(responses))

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        expected = [
            'Sheet_Name','A','B','C',
            'May 2025 D','May 2025 E','May 2025 F','May 2025 G','May 2025 H','May 2025 I',
            'May 2024 J','May 2024 K','May 2024 L',
            'YTD May 2025 M','YTD May 2025 N','YTD May 2025 O','YTD May 2025 P',
            'YTD May 2024 Q','YTD May 2024 R','YTD May 2024 S'
        ]
        self.assertEqual(list(cleaned.columns), expected)


if __name__ == '__main__':
    unittest.main()
