import os
import sys
import types
import unittest
import pandas as pd

from tests.qt_stubs import patch_qt_modules


class TestGatherSheetNamesSQL(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        from importlib import import_module
        sys.modules.pop('src.ui.main_window', None)
        self.MainWindow = import_module('src.ui.main_window').MainWindow

    def _gather(self, df):
        window = self.MainWindow.__new__(self.MainWindow)
        window.results_viewer = types.SimpleNamespace(
            results_data=df.to_dict(orient='records'),
            get_dataframe=lambda: df,
            has_results=lambda: True,
        )
        window.logger = types.SimpleNamespace(error=lambda *a, **k: None)
        return window._gather_sheet_names_from_sql()

    def test_lowercase_column_names(self):
        for cand in ["sheet_name", "sheet", "sheetname"]:
            df = pd.DataFrame({cand: ["Foo", "Bar", "Foo"], "Amount": [1, 2, 3]})
            sheets = self._gather(df)
            self.assertEqual(sheets, ["Bar", "Foo"])


if __name__ == '__main__':
    unittest.main()
