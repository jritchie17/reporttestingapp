import os
import unittest
from unittest.mock import MagicMock
import types
import pandas as pd

from tests.qt_stubs import patch_qt_modules

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestGatherAccountsSQL(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        from importlib import import_module
        import sys
        sys.modules.pop('src.ui.main_window', None)
        self.MainWindow = import_module('src.ui.main_window').MainWindow
        self.df = pd.read_csv(os.path.join(FIXTURES, 'sql_data.csv'))
        self.results_viewer = types.SimpleNamespace(
            results_data=self.df.to_dict(orient='records'),
            get_dataframe=lambda: self.df,
            has_results=lambda: True,
        )

    def test_gather_accounts_from_sql(self):
        window = self.MainWindow.__new__(self.MainWindow)
        window.results_viewer = self.results_viewer
        window.logger = MagicMock()

        accounts = window._gather_accounts_from_sql()
        self.assertEqual(accounts, ['1234-5678', '9999-0000'])


if __name__ == '__main__':
    unittest.main()
