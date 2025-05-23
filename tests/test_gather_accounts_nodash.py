import os
import sys
import types
import unittest
from unittest.mock import MagicMock

from tests.qt_stubs import patch_qt_modules

import pandas as pd
from src.analyzer.excel_analyzer import ExcelAnalyzer

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')




class TestGatherAccountsNoDash(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        file_path = os.path.join(FIXTURES, 'excel_data_nodash.csv')
        df = pd.read_csv(file_path)
        self.analyzer = ExcelAnalyzer(file_path)
        sheet = 'Sheet1'
        self.analyzer.sheet_names = [sheet]
        self.analyzer.sheet_data[sheet] = {
            'dataframe': df,
            'header_indexes': [0]
        }

    def test_gather_accounts_no_dash(self):
        from src.ui.main_window import MainWindow

        window = MainWindow.__new__(MainWindow)
        window.excel_analyzer = self.analyzer
        window.logger = MagicMock()

        accounts = window._gather_accounts_from_excel()
        self.assertEqual(accounts, ['12345678', '87654321'])


if __name__ == '__main__':
    unittest.main()
