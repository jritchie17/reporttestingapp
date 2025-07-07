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
        self.assertEqual(list(cleaned.columns), ['Sheet_Name', 'CAReportName', 'Val1'])
        self.assertEqual(cleaned.iloc[0].tolist(), ['Facility', 'Facility: 0 - 30 days', 1.0])
        self.assertEqual(cleaned.iloc[1].tolist(), ['Facility', 'Facility: 31 - 60 days', 2.0])

if __name__ == '__main__':
    unittest.main()
