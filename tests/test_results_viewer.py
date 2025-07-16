import unittest
import importlib
import sys
import os
import types
import pandas as pd

from tests.qt_stubs import patch_qt_modules
from src.utils.account_categories import CategoryCalculator

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class DummyConfig:
    def __init__(self):
        self.categories = {}
        self.formulas = {}
        self.formula_library = {}
        self.report_type = ""

    def get_account_categories(self, report_type, sheet_name=None):
        return self.categories.get(report_type, {}).get(sheet_name or "__default__", {})

    def get_account_formulas(self, report_type, sheet_name=None):
        mapping = self.formulas.get(report_type, {}).get(sheet_name or "__default__", {})
        result = dict(mapping)
        for name, info in self.formula_library.items():
            sheets = info.get("sheets") or []
            if sheet_name is None or sheet_name in sheets or "__default__" in sheets:
                result.setdefault(name, info.get("expr", ""))
        return result

    def set_account_categories(self, report_type, cats, sheet_name=None):
        sheet_name = sheet_name or "__default__"
        self.categories.setdefault(report_type, {})[sheet_name] = cats

    def set_account_formulas(self, report_type, formulas, sheet_name=None):
        sheet_name = sheet_name or "__default__"
        self.formulas.setdefault(report_type, {})[sheet_name] = formulas

    def get_formula_library(self):
        return self.formula_library

    def set_formula_library(self, lib):
        self.formula_library = lib

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


class ApplyCalculationsTest(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        sys.modules.pop("src.ui.results_viewer", None)
        sys.modules.pop("src.ui.main_window", None)
        self.rv_mod = importlib.import_module("src.ui.results_viewer")
        self.ResultsViewer = self.rv_mod.ResultsViewer
        self.ResultsTableModel = self.rv_mod.ResultsTableModel
        self.MainWindow = importlib.import_module("src.ui.main_window").MainWindow

    def test_apply_calculations_appends_rows(self):
        parent = self.MainWindow.__new__(self.MainWindow)
        parent.config = DummyConfig()
        parent.config.set_account_categories(
            "Test", {"CatA": ["1234-5678"], "CatB": ["9999-0000"]}
        )
        parent.config.set_formula_library(
            {"Net": {"expr": "CatA + CatB", "display_name": "Net"}}
        )
        parent.config.report_type = "Test"
        parent.comparison_engine = type("CE", (), {"sign_flip_accounts": []})()
        parent.sheet_selector = DummySelector("Foo")
        parent.sheet_selector = DummySelector("Foo")

        viewer = self.ResultsViewer.__new__(self.ResultsViewer)
        viewer.results_data = [
            {"Sheet": "Foo", "Center": 1, "CAReportName": "1234-5678", "Amount": -100},
            {"Sheet": "Foo", "Center": 2, "CAReportName": "9999-0000", "Amount": 50},
        ]
        viewer.columns = ["Sheet", "Center", "CAReportName", "Amount"]
        viewer.table_view = DummyTable()
        viewer.status_label = DummyLabel()
        viewer.window = lambda: parent

        viewer.apply_calculations()

        calc = CategoryCalculator(
            {"CatA": ["1234-5678"], "CatB": ["9999-0000"]},
            {"Net": "CatA + CatB"},
            group_column="Sheet",
        )
        expected = calc.compute(
            [
                {
                    "Sheet": "Foo",
                    "Center": 1,
                    "CAReportName": "1234-5678",
                    "Amount": -100,
                },
                {
                    "Sheet": "Foo",
                    "Center": 2,
                    "CAReportName": "9999-0000",
                    "Amount": 50,
                },
            ],
            include_categories=False,
        )

        self.assertEqual(viewer.results_data, expected)
        self.assertIsInstance(viewer.model, self.ResultsTableModel)
        self.assertEqual(
            viewer.status_label.text,
            f"{len(expected)} rows, {len(viewer.columns)} columns returned",
        )
        self.assertIn("Sheet", viewer.columns)

    def test_apply_calculations_groups_by_sheet(self):
        parent = self.MainWindow.__new__(self.MainWindow)
        parent.config = DummyConfig()
        parent.config.set_account_categories(
            "Test", {"CatA": ["1234-5678"], "CatB": ["9999-0000"]}
        )
        parent.config.set_formula_library(
            {"Net": {"expr": "CatA + CatB", "display_name": "Net"}}
        )
        parent.config.report_type = "Test"
        parent.comparison_engine = type("CE", (), {"sign_flip_accounts": []})()

        viewer = self.ResultsViewer.__new__(self.ResultsViewer)
        viewer.results_data = [
            {
                "Sheet": "Foo",
                "CAReportName": "1234-5678",
                "Amount": -100,
            },
            {
                "Sheet": "Bar",
                "CAReportName": "9999-0000",
                "Amount": 50,
            },
        ]
        viewer.columns = ["Sheet", "CAReportName", "Amount"]
        viewer.table_view = DummyTable()
        viewer.status_label = DummyLabel()
        viewer.window = lambda: parent

        viewer.apply_calculations()

        calc = CategoryCalculator(
            {"CatA": ["1234-5678"], "CatB": ["9999-0000"]},
            {"Net": "CatA + CatB"},
            group_column="Sheet",
        )
        expected = calc.compute(
            [
                {"Sheet": "Foo", "CAReportName": "1234-5678", "Amount": -100},
                {"Sheet": "Bar", "CAReportName": "9999-0000", "Amount": 50},
            ],
            include_categories=False,
        )

        self.assertEqual(viewer.results_data, expected)
        net_rows = [
            row for row in viewer.results_data if row.get("CAReportName") == "Net"
        ]
        sheets = {row.get("Sheet") for row in net_rows}
        self.assertEqual(len(net_rows), 2)
        self.assertEqual(sheets, {"Foo", "Bar"})
        self.assertIn("Sheet", viewer.columns)

    def test_apply_calculations_adds_sheet_column(self):
        parent = self.MainWindow.__new__(self.MainWindow)
        parent.config = DummyConfig()
        parent.config.set_account_categories(
            "Test", {"CatA": ["1234-5678"], "CatB": ["9999-0000"]}
        )
        parent.config.set_formula_library(
            {"Net": {"expr": "CatA + CatB", "display_name": "Net"}}
        )
        parent.config.report_type = "Test"
        parent.comparison_engine = type("CE", (), {"sign_flip_accounts": []})()
        parent.sheet_selector = DummySelector("Foo")

        viewer = self.ResultsViewer.__new__(self.ResultsViewer)
        viewer.results_data = [
            {"CAReportName": "1234-5678", "Amount": -100},
            {"CAReportName": "9999-0000", "Amount": 50},
        ]
        viewer.columns = ["CAReportName", "Amount"]
        viewer.table_view = DummyTable()
        viewer.status_label = DummyLabel()
        viewer.window = lambda: parent

        viewer.apply_calculations()

        net_rows = [
            row for row in viewer.results_data if row.get("CAReportName") == "Net"
        ]
        self.assertEqual(len(net_rows), 1)
        self.assertEqual(net_rows[0].get("Sheet"), "Foo")
        self.assertIn("Sheet", viewer.columns)

    def test_apply_calculations_uses_existing_sheetname(self):
        parent = self.MainWindow.__new__(self.MainWindow)
        parent.config = DummyConfig()
        parent.config.set_account_categories("Test", {"CatA": ["1234-5678"]})
        parent.config.set_formula_library(
            {"Net": {"expr": "CatA", "display_name": "Net"}}
        )
        parent.config.report_type = "Test"
        parent.comparison_engine = type("CE", (), {"sign_flip_accounts": []})()

        viewer = self.ResultsViewer.__new__(self.ResultsViewer)
        viewer.results_data = [
            {"SheetName": "Foo", "CAReportName": "1234-5678", "Amount": 10}
        ]
        viewer.columns = ["SheetName", "CAReportName", "Amount"]
        viewer.table_view = DummyTable()
        viewer.status_label = DummyLabel()
        viewer.window = lambda: parent

        viewer.apply_calculations()

        self.assertNotIn("Sheet", viewer.columns)
        self.assertIn("SheetName", viewer.columns)

    def test_apply_calculations_formula_rows_unprefixed(self):
        parent = self.MainWindow.__new__(self.MainWindow)
        parent.config = DummyConfig()
        parent.config.set_account_categories(
            "AR Center",
            {"Bad debt": ["Bad debt"]},
        )
        parent.config.set_formula_library(
            {"Bad debt percentage": {"expr": "Bad debt", "display_name": "Bad debt percentage", "sheets": ["facility"]}}
        )
        parent.config.report_type = "AR Center"
        parent.comparison_engine = type("CE", (), {"sign_flip_accounts": []})()
        parent.sheet_selector = DummySelector("facility")

        viewer = self.ResultsViewer.__new__(self.ResultsViewer)
        viewer.results_data = [
            {"CAReportName": "Facility: Bad debt", "Amount": 100},
        ]
        viewer.columns = ["CAReportName", "Amount"]
        viewer.table_view = DummyTable()
        viewer.status_label = DummyLabel()
        viewer.window = lambda: parent

        viewer.apply_calculations()

        # Formula rows should not be prefixed with the sheet name
        has_formula = any(
            row.get("CAReportName") == "Bad debt percentage"
            for row in viewer.results_data
        )
        self.assertTrue(has_formula)

    def test_apply_calculations_respects_row_sheet(self):
        parent = self.MainWindow.__new__(self.MainWindow)
        parent.config = DummyConfig()
        parent.config.set_account_categories(
            "AR Center",
            {"Bad debt": ["Bad debt"]},
        )
        parent.config.set_formula_library(
            {"Bad debt percentage": {"expr": "Bad debt", "display_name": "Bad debt percentage", "sheets": ["facility", "anesthesia"]}}
        )
        parent.config.report_type = "AR Center"
        parent.comparison_engine = type("CE", (), {"sign_flip_accounts": []})()
        parent.sheet_selector = DummySelector("facility")

        viewer = self.ResultsViewer.__new__(self.ResultsViewer)
        viewer.results_data = [
            {"Sheet": "facility", "CAReportName": "Facility: Bad debt", "Amount": 100},
            {
                "Sheet": "anesthesia",
                "CAReportName": "Anesthesia: Bad debt",
                "Amount": 50,
            },
        ]
        viewer.columns = ["Sheet", "CAReportName", "Amount"]
        viewer.table_view = DummyTable()
        viewer.status_label = DummyLabel()
        viewer.window = lambda: parent

        viewer.apply_calculations()

        fac_row = any(
            row.get("CAReportName") == "Bad debt percentage" and row.get("Sheet") == "facility"
            for row in viewer.results_data
        )
        ane_row = any(
            row.get("CAReportName") == "Bad debt percentage" and row.get("Sheet") == "anesthesia"
            for row in viewer.results_data
        )
        self.assertTrue(fac_row)
        self.assertTrue(ane_row)


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
