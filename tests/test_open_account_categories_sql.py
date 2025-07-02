import os
import unittest
from unittest.mock import MagicMock
import types
import pandas as pd

from tests.qt_stubs import patch_qt_modules

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


class DummyConfig:
    def get_account_categories(self, report_type, sheet_name=None):
        return {}

    def get_account_formulas(self, report_type, sheet_name=None):
        return {}


class DummySelector:
    def __init__(self, text):
        self._text = text

    def currentText(self):
        return self._text


class DummyStatusBar:
    def __init__(self):
        self.message = ""

    def showMessage(self, msg):
        self.message = msg


class TestOpenAccountCategoriesSQL(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        from importlib import import_module
        import sys
        sys.modules.pop('src.ui.main_window', None)
        sys.modules.pop('src.ui.account_category_dialog', None)
        self.main_mod = import_module('src.ui.main_window')
        self.dialog_mod = import_module('src.ui.account_category_dialog')
        self.MainWindow = self.main_mod.MainWindow
        self.AccountCategoryDialog = self.dialog_mod.AccountCategoryDialog
        self.df = pd.read_csv(os.path.join(FIXTURES, 'sql_data.csv'))

    def test_dialog_receives_sql_accounts(self):
        captured = {}

        class StubDialog:
            def __init__(self, config, report_type, accounts, sheet_names=None, parent=None):
                captured['accounts'] = accounts
                captured['sheets'] = sheet_names
            def exec(self):
                return True

        self.main_mod.AccountCategoryDialog = StubDialog

        window = self.MainWindow.__new__(self.MainWindow)
        window.config = DummyConfig()
        window.report_selector = DummySelector('Test')
        window.status_bar = DummyStatusBar()
        window.logger = MagicMock()
        window.results_viewer = types.SimpleNamespace(
            results_data=self.df.to_dict(orient='records'),
            get_dataframe=lambda: self.df,
            has_results=lambda: True,
        )

        window.open_account_categories()

        self.assertEqual(captured.get('accounts'), ['1234-5678', '9999-0000'])
        self.assertEqual(captured.get('sheets'), [])
        self.assertEqual(window.status_bar.message, 'Account categories updated')


if __name__ == '__main__':
    unittest.main()
