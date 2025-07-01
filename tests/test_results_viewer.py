import unittest
import importlib
import sys

from tests.qt_stubs import patch_qt_modules
from src.utils.account_categories import CategoryCalculator


class DummyConfig:
    def __init__(self):
        self.categories = {}
        self.formulas = {}
        self.report_type = ""

    def get_account_categories(self, report_type):
        return self.categories.get(report_type, {})

    def get_account_formulas(self, report_type):
        return self.formulas.get(report_type, {})

    def set_account_categories(self, report_type, cats):
        self.categories[report_type] = cats

    def set_account_formulas(self, report_type, formulas):
        self.formulas[report_type] = formulas

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
        parent.config.set_account_formulas("Test", {"Net": "CatA + CatB"})
        parent.config.report_type = "Test"
        parent.comparison_engine = type("CE", (), {"sign_flip_accounts": []})()

        viewer = self.ResultsViewer.__new__(self.ResultsViewer)
        viewer.results_data = [
            {"Center": 1, "CAReportName": "1234-5678", "Amount": -100},
            {"Center": 2, "CAReportName": "9999-0000", "Amount": 50},
        ]
        viewer.columns = ["Center", "CAReportName", "Amount"]
        viewer.table_view = DummyTable()
        viewer.status_label = DummyLabel()
        viewer.window = lambda: parent

        viewer.apply_calculations()

        calc = CategoryCalculator(
            {"CatA": ["1234-5678"], "CatB": ["9999-0000"]},
            {"Net": "CatA + CatB"},
            group_column="Center",
        )
        expected = calc.compute([
            {"Center": 1, "CAReportName": "1234-5678", "Amount": -100},
            {"Center": 2, "CAReportName": "9999-0000", "Amount": 50},
        ])

        self.assertEqual(viewer.results_data, expected)
        self.assertIsInstance(viewer.model, self.ResultsTableModel)
        self.assertEqual(
            viewer.status_label.text,
            f"{len(expected)} rows, {len(viewer.columns)} columns returned",
        )


if __name__ == "__main__":
    unittest.main()
