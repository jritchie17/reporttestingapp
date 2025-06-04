import os
import pandas as pd
import unittest
from unittest.mock import MagicMock

from tests.qt_stubs import patch_qt_modules

class TestExtractSQLCodes(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        from src.ui.excel_viewer import ExcelViewer
        self.ExcelViewer = ExcelViewer

    def test_extract_careportname(self):
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.df = pd.DataFrame({
            'CAReportName': ['Acct A', 'Acct B'],
            'Value': [1, 2]
        })
        viewer.sheet_name = '2001-001'
        viewer.report_type = 'SOO MFR'
        viewer.select_sheets_dialog = lambda sheets: [viewer.sheet_name]
        captured = {}
        viewer.show_extracted_sql = lambda cs, asql, centers, accounts, *a, **k: captured.update({
            'center_sql': cs, 'account_sql': asql, 'centers': centers, 'accounts': accounts
        })
        from PyQt6.QtWidgets import QInputDialog
        QInputDialog.getItem = staticmethod(lambda *a, **k: ('CAReportName', True))

        viewer.extract_sql_codes()

        self.assertEqual(captured['accounts'], {'Acct A', 'Acct B'})
        self.assertIn("'Acct A'", captured['account_sql'])
        self.assertIn('2001-001', captured['centers'])

    def test_extract_first_column_mfr(self):
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.df = pd.DataFrame({
            'A': ['Acct A', 'Acct B'],
            'B': [1, 2]
        })
        viewer.sheet_name = '2001-001'
        viewer.report_type = 'SOO MFR'
        viewer.select_sheets_dialog = lambda sheets: [viewer.sheet_name]
        captured = {}
        viewer.show_extracted_sql = lambda cs, asql, centers, accounts, *a, **k: captured.update({
            'center_sql': cs, 'account_sql': asql, 'centers': centers, 'accounts': accounts
        })
        from PyQt6.QtWidgets import QInputDialog
        QInputDialog.getItem = staticmethod(lambda *a, **k: ('A', True))

        viewer.extract_sql_codes()

        self.assertEqual(captured['accounts'], {'Acct A', 'Acct B'})
        self.assertIn("'Acct A'", captured['account_sql'])
        self.assertIn('2001-001', captured['centers'])

if __name__ == '__main__':
    unittest.main()
