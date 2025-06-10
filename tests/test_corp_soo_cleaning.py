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
            ['', '', ''],
            ['acct3',0,0]
        ])

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        self.assertEqual(list(cleaned.columns), ['A','B','C'])
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0].tolist(), ['acct2', 1.0, 2.0])

if __name__ == '__main__':
    unittest.main()
