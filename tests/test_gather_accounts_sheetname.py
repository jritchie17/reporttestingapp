import os
import unittest
from unittest.mock import MagicMock

from tests.qt_stubs import patch_qt_modules

import pandas as pd
from src.analyzer.excel_analyzer import ExcelAnalyzer


class TestGatherAccountsSheetName(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        # Create dataframe where the account column is second and a Sheet column is first
        df = pd.DataFrame({
            'Sheet': ['Sheet1', 'Sheet1'],
            'ColA': ['1234-5678', '9999-0000'],
            'Other': [1, 2]
        })
        self.analyzer = ExcelAnalyzer('dummy.xlsx')
        sheet = 'Sheet1'
        self.analyzer.sheet_names = [sheet]
        self.analyzer.sheet_data[sheet] = {
            'dataframe': df,
            'header_indexes': [0]
        }

    def test_gather_accounts_with_sheet_name(self):
        from src.ui.main_window import MainWindow

        window = MainWindow.__new__(MainWindow)
        window.excel_analyzer = self.analyzer
        window.logger = MagicMock()

        accounts = window._gather_accounts_from_excel()
        self.assertEqual(accounts, ['1234-5678', '9999-0000'])


if __name__ == '__main__':
    unittest.main()
