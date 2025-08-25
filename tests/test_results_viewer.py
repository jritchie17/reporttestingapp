import unittest
import importlib
import sys
import os
import types
import pandas as pd

from tests.qt_stubs import patch_qt_modules

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class DummyConfig:
    def __init__(self):
        self.categories = {}
        self.report_formulas = {}
        self.report_type = ""

    def get_account_categories(self, report_type, sheet_name=None):
        mapping = self.categories.get(report_type, {})
        if sheet_name is None:
            return mapping.get("__default__", {})
        return mapping.get(sheet_name) or mapping.get("__default__", {})

    def get_report_formulas(self, report_type, sheet_name=None):
        mapping = self.report_formulas.get(report_type, {})
        result = {}
        for name, info in mapping.items():
            sheets = info.get("sheets") or []
            if sheet_name is None or not sheets or sheet_name in sheets or "__default__" in sheets:
                result[name] = info
        return result

    def set_account_categories(self, report_type, cats, sheet_name=None):
        sheet_name = sheet_name or "__default__"
        self.categories.setdefault(report_type, {})[sheet_name] = cats

    def set_report_formulas(self, report_type, formulas):
        self.report_formulas[report_type] = formulas

    def get(self, section, key=None):
        if section == "excel" and key == "report_type":
            return self.report_type
        return None


class DummyTable:
    def __init__(self):
        self.model = None

    def setModel(self, model):
        self.model = model

    def resizeColumnsToContents(self):
        pass


class DummyLabel:
    def __init__(self):
        self.text = ""

    def setText(self, text):
        self.text = text


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


class SQLAccountExtractionTest(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        sys.modules.pop("src.ui.main_window", None)
        self.MainWindow = importlib.import_module("src.ui.main_window").MainWindow
        self.df = pd.read_csv(os.path.join(FIXTURES, "sql_data.csv"))

    def test_gather_accounts_from_sql(self):
        window = self.MainWindow.__new__(self.MainWindow)
        window.results_viewer = types.SimpleNamespace(
            results_data=self.df.to_dict(orient="records"),
            get_dataframe=lambda: self.df,
            has_results=lambda: True,
        )
        window.logger = types.SimpleNamespace(error=lambda *a, **k: None)

        accounts = window._gather_accounts_from_sql()

        self.assertEqual(accounts, ["1234-5678", "9999-0000"])

    def test_gather_accounts_sql_fallback(self):
        df = pd.DataFrame(
            {
                "Acct": ["1234-5678", "9999-0000"],
                "Amount": [1, 2],
            }
        )
        window = self.MainWindow.__new__(self.MainWindow)
        window.results_viewer = types.SimpleNamespace(
            results_data=df.to_dict(orient="records"),
            get_dataframe=lambda: df,
            has_results=lambda: True,
        )
        window.logger = types.SimpleNamespace(error=lambda *a, **k: None)

        accounts = window._gather_accounts_from_sql()

        self.assertEqual(accounts, ["1234-5678", "9999-0000"])

    def test_open_account_categories_after_sql(self):
        captured = {}

        class StubDialog:
            def __init__(
                self, config, report_type, accounts, sheet_names=None, parent=None
            ):
                captured["accounts"] = accounts
                captured["sheets"] = sheet_names

            def refresh_accounts(self, accounts):
                captured["refresh"] = accounts

            def exec(self):
                return True

        mod = importlib.import_module("src.ui.main_window")
        mod.AccountCategoryDialog = StubDialog

        window = self.MainWindow.__new__(self.MainWindow)
        window.config = DummyConfig()
        window.report_selector = DummySelector("Test")
        window.status_bar = DummyStatusBar()
        window.logger = types.SimpleNamespace()
        window.results_viewer = types.SimpleNamespace(
            results_data=self.df.to_dict(orient="records"),
            get_dataframe=lambda: self.df,
            has_results=lambda: True,
        )

        window.open_account_categories()

        self.assertEqual(captured.get("accounts"), ["1234-5678", "9999-0000"])
        self.assertEqual(captured.get("refresh"), ["1234-5678", "9999-0000"])
        self.assertEqual(captured.get("sheets"), [])
        self.assertEqual(window.status_bar.message, "Account categories updated")


class ARCenterResultsLoadTest(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        sys.modules.pop("src.ui.results_viewer", None)
        sys.modules.pop("src.ui.main_window", None)
        self.ResultsViewer = importlib.import_module(
            "src.ui.results_viewer"
        ).ResultsViewer
        self.MainWindow = importlib.import_module("src.ui.main_window").MainWindow

    def _load(self, data, columns=None, sheet="facility"):
        parent = self.MainWindow.__new__(self.MainWindow)
        parent.config = DummyConfig()
        parent.config.report_type = "AR Center"
        parent.sheet_selector = DummySelector(sheet)

        viewer = self.ResultsViewer.__new__(self.ResultsViewer)
        viewer.table_view = DummyTable()
        viewer.status_label = DummyLabel()
        viewer.window = lambda: parent
        viewer.logger = types.SimpleNamespace(debug=lambda *a, **k: None)

        viewer.load_results(list(data), columns)
        return viewer

    def test_load_results_prefixes_careportname(self):
        data = [
            {"CAReportName": "0 - 30 days", "Val": 1},
            {"CAReportName": "31 - 60 days", "Val": 2},
        ]
        viewer = self._load(data, ["CAReportName", "Val"], sheet="facility")
        self.assertEqual(
            [row["CAReportName"] for row in viewer.results_data],
            ["0 - 30 days", "31 - 60 days"],
        )

    def test_load_results_prefixes_first_column(self):
        data = [
            {"Acct": "0 - 30 days", "Val": 1},
            {"Acct": "31 - 60 days", "Val": 2},
        ]
        viewer = self._load(data, ["Acct", "Val"], sheet="facility")
        self.assertEqual(
            [row["Acct"] for row in viewer.results_data],
            ["0 - 30 days", "31 - 60 days"],
        )

    def test_load_results_avoids_double_prefix(self):
        data = [
            {"CAReportName": "Facility: Bad debt", "Val": 1},
        ]
        viewer = self._load(data, ["CAReportName", "Val"], sheet="facility")
        self.assertEqual(viewer.results_data[0]["CAReportName"], "Facility: Bad debt")

    def test_load_results_uses_sheet_column(self):
        data = [
            {"Sheet": "facility", "CAReportName": "0 - 30 days"},
            {"Sheet": "anesthesia", "CAReportName": "Bad debt"},
        ]
        viewer = self._load(data, ["Sheet", "CAReportName"], sheet="facility")
        self.assertEqual(
            [row["CAReportName"] for row in viewer.results_data],
            ["0 - 30 days", "Bad debt"],
        )


if __name__ == "__main__":
    unittest.main()
