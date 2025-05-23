import os
import sys
import types
import pandas as pd
import unittest
from decimal import Decimal

from tests.qt_stubs import patch_qt_modules

from src.utils.account_categories import CategoryCalculator

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")



class DummyConfig:
    def __init__(self):
        self.categories = {}
        self.formulas = {}

    def get_account_categories(self, report_type):
        return self.categories.get(report_type, {})

    def get_account_formulas(self, report_type):
        return self.formulas.get(report_type, {})

    def set_account_categories(self, report_type, cats):
        self.categories[report_type] = cats

    def set_account_formulas(self, report_type, formulas):
        self.formulas[report_type] = formulas


class TestCategoryCalculator(unittest.TestCase):
    def setUp(self):
        df = pd.read_csv(os.path.join(FIXTURES, "sql_data.csv"))
        self.rows = df.to_dict(orient="records")
        self.categories = {
            "CatA": ["1234-5678"],
            "CatB": ["9999-0000"],
        }
        self.formulas = {"Net": "CatA + CatB"}

    def test_compute_totals_and_formulas(self):
        calc = CategoryCalculator(self.categories, self.formulas)
        result = calc.compute(list(self.rows))
        self.assertEqual(len(result), len(self.rows) + 3)
        cat_a = next(r for r in result if r["CAReportName"] == "CatA")
        self.assertEqual(cat_a["Amount"], -100)
        cat_b = next(r for r in result if r["CAReportName"] == "CatB")
        self.assertEqual(cat_b["Amount"], 50)
        net = next(r for r in result if r["CAReportName"] == "Net")
        self.assertEqual(net["Amount"], -50)

    def test_compute_with_sign_flip(self):
        calc = CategoryCalculator(
            self.categories, self.formulas, sign_flip_accounts=["1234-5678"]
        )
        result = calc.compute(list(self.rows))
        cat_a = next(r for r in result if r["CAReportName"] == "CatA")
        self.assertEqual(cat_a["Amount"], 100)
        net = next(r for r in result if r["CAReportName"] == "Net")
        self.assertEqual(net["Amount"], 150)

    def test_compute_detects_account_column(self):
        rows = [
            {"Center": 1, "Account": "1234-5678", "Amount": -100},
            {"Center": 2, "Account": "9999-0000", "Amount": 50},
        ]
        calc = CategoryCalculator(self.categories, self.formulas)
        result = calc.compute(rows)
        self.assertEqual(len(result), len(rows) + 3)
        cat_a = next(r for r in result if r["Account"] == "CatA")
        self.assertEqual(cat_a["Amount"], -100)
        cat_b = next(r for r in result if r["Account"] == "CatB")
        self.assertEqual(cat_b["Amount"], 50)
        net = next(r for r in result if r["Account"] == "Net")
        self.assertEqual(net["Amount"], -50)

    def test_account_code_with_text(self):
        rows = [
            {"CAReportName": "1234-5678", "Amount": -100},
            {"CAReportName": "6101-6001 GI revenue", "Amount": 30},
            {"CAReportName": "9999-0000", "Amount": 50},
        ]
        categories = {
            "CatA": ["1234-5678"],
            "CatB": ["9999-0000"],
            "GI": ["61016001"],
        }
        formulas = {"Net": "CatA + CatB + GI"}
        calc = CategoryCalculator(categories, formulas)
        result = calc.compute(rows)

        self.assertEqual(len(result), len(rows) + 4)
        gi = next(r for r in result if r["CAReportName"] == "GI")
        self.assertEqual(gi["Amount"], 30)
        net = next(r for r in result if r["CAReportName"] == "Net")
        self.assertEqual(net["Amount"], -20)

    def test_numeric_columns_skip_group_column(self):
        calc = CategoryCalculator(self.categories, self.formulas, group_column="Center")
        numeric = calc._numeric_columns(self.rows)
        self.assertEqual(numeric, ["Amount"])

    def test_grouped_totals_and_formulas(self):
        calc = CategoryCalculator(self.categories, self.formulas, group_column="Center")
        result = calc.compute(list(self.rows))
        self.assertEqual(len(result), len(self.rows) + 6)

        cat_a_c1 = next(
            r for r in result if r["CAReportName"] == "CatA" and r["Center"] == 1
        )
        self.assertEqual(cat_a_c1["Amount"], -100)
        cat_b_c2 = next(
            r for r in result if r["CAReportName"] == "CatB" and r["Center"] == 2
        )
        self.assertEqual(cat_b_c2["Amount"], 50)

        net_c1 = next(
            r for r in result if r["CAReportName"] == "Net" and r["Center"] == 1
        )
        self.assertEqual(net_c1["Amount"], -100)
        net_c2 = next(
            r for r in result if r["CAReportName"] == "Net" and r["Center"] == 2
        )
        self.assertEqual(net_c2["Amount"], 50)

    def test_decimal_values_grouped(self):
        rows = [
            {"Center": 1, "CAReportName": "1234-5678", "Amount": Decimal("1.5")},
            {"Center": 1, "CAReportName": "9999-0000", "Amount": Decimal("2.5")},
            {
                "Center": 2,
                "CAReportName": "1234-5678",
                "Amount": Decimal("3.5"),
                "Qty": Decimal("1"),
            },
            {
                "Center": 2,
                "CAReportName": "9999-0000",
                "Amount": Decimal("4.5"),
                "Qty": Decimal("2"),
            },
        ]
        calc = CategoryCalculator(self.categories, self.formulas, group_column="Center")
        result = calc.compute(rows)

        self.assertEqual(len(result), len(rows) + 6)

        cat_a_c1 = next(
            r for r in result if r["CAReportName"] == "CatA" and r["Center"] == 1
        )
        self.assertEqual(cat_a_c1["Amount"], 1.5)
        self.assertEqual(cat_a_c1.get("Qty", 0), 0)

        cat_b_c1 = next(
            r for r in result if r["CAReportName"] == "CatB" and r["Center"] == 1
        )
        self.assertEqual(cat_b_c1["Amount"], 2.5)
        self.assertEqual(cat_b_c1.get("Qty", 0), 0)

        net_c1 = next(
            r for r in result if r["CAReportName"] == "Net" and r["Center"] == 1
        )
        self.assertEqual(net_c1["Amount"], 4.0)
        self.assertEqual(net_c1.get("Qty", 0), 0)

        cat_a_c2 = next(
            r for r in result if r["CAReportName"] == "CatA" and r["Center"] == 2
        )
        self.assertEqual(cat_a_c2["Amount"], 3.5)
        self.assertEqual(cat_a_c2["Qty"], 1)

        cat_b_c2 = next(
            r for r in result if r["CAReportName"] == "CatB" and r["Center"] == 2
        )
        self.assertEqual(cat_b_c2["Amount"], 4.5)
        self.assertEqual(cat_b_c2["Qty"], 2)

        net_c2 = next(
            r for r in result if r["CAReportName"] == "Net" and r["Center"] == 2
        )
        self.assertEqual(net_c2["Amount"], 8.0)
        self.assertEqual(net_c2["Qty"], 3)

    def test_decimal_amounts_non_numeric_first_row_grouped(self):
        """Ensure numeric column detection scans all rows and ignores bools."""
        rows = [
            {"Center": 1, "CAReportName": "1234-5678", "Amount": "N/A", "Flag": True},
            {"Center": 1, "CAReportName": "9999-0000", "Amount": Decimal("2")},
            {"Center": 2, "CAReportName": "1234-5678", "Amount": Decimal("3")},
            {
                "Center": 2,
                "CAReportName": "9999-0000",
                "Amount": Decimal("4"),
                "Flag": False,
            },
        ]

        calc = CategoryCalculator(self.categories, self.formulas, group_column="Center")
        result = calc.compute(rows)

        cat_a_c1 = next(
            r for r in result if r["CAReportName"] == "CatA" and r["Center"] == 1
        )
        self.assertEqual(cat_a_c1["Amount"], 0)
        self.assertNotIn("Flag", cat_a_c1)

        cat_b_c1 = next(
            r for r in result if r["CAReportName"] == "CatB" and r["Center"] == 1
        )
        self.assertEqual(cat_b_c1["Amount"], 2)
        self.assertNotIn("Flag", cat_b_c1)

        net_c1 = next(
            r for r in result if r["CAReportName"] == "Net" and r["Center"] == 1
        )
        self.assertEqual(net_c1["Amount"], 2)

        cat_a_c2 = next(
            r for r in result if r["CAReportName"] == "CatA" and r["Center"] == 2
        )
        self.assertEqual(cat_a_c2["Amount"], 3)

        cat_b_c2 = next(
            r for r in result if r["CAReportName"] == "CatB" and r["Center"] == 2
        )
        self.assertEqual(cat_b_c2["Amount"], 4)

        net_c2 = next(
            r for r in result if r["CAReportName"] == "Net" and r["Center"] == 2
        )
        self.assertEqual(net_c2["Amount"], 7)

    def test_formula_with_account_reference(self):
        rows = [
            {"CAReportName": "1234-5678", "Amount": -100},
            {"CAReportName": "5555-5555", "Amount": 20},
        ]
        categories = {"CatA": ["1234-5678"]}
        formulas = {"NetAcct": "CatA + 5555-5555"}
        calc = CategoryCalculator(categories, formulas)
        result = calc.compute(list(rows))

        net = next(r for r in result if r["CAReportName"] == "NetAcct")
        self.assertEqual(net["Amount"], -80)
        self.assertFalse(any(r["CAReportName"] == "5555-5555" for r in result))

    def test_all_decimal_amounts_grouped(self):
        rows = [
            {"Center": 1, "CAReportName": "1234-5678", "Amount": Decimal("1")},
            {"Center": 1, "CAReportName": "9999-0000", "Amount": Decimal("2")},
            {"Center": 2, "CAReportName": "1234-5678", "Amount": Decimal("3")},
            {"Center": 2, "CAReportName": "9999-0000", "Amount": Decimal("4")},
        ]

        calc = CategoryCalculator(self.categories, self.formulas, group_column="Center")
        result = calc.compute(rows)

        self.assertEqual(len(result), len(rows) + 6)

        cat_a_c1 = next(
            r for r in result if r["CAReportName"] == "CatA" and r["Center"] == 1
        )
        self.assertEqual(cat_a_c1["Amount"], 1)

        cat_b_c1 = next(
            r for r in result if r["CAReportName"] == "CatB" and r["Center"] == 1
        )
        self.assertEqual(cat_b_c1["Amount"], 2)

        net_c1 = next(
            r for r in result if r["CAReportName"] == "Net" and r["Center"] == 1
        )
        self.assertEqual(net_c1["Amount"], 3)

        cat_a_c2 = next(
            r for r in result if r["CAReportName"] == "CatA" and r["Center"] == 2
        )
        self.assertEqual(cat_a_c2["Amount"], 3)

        cat_b_c2 = next(
            r for r in result if r["CAReportName"] == "CatB" and r["Center"] == 2
        )
        self.assertEqual(cat_b_c2["Amount"], 4)

        net_c2 = next(
            r for r in result if r["CAReportName"] == "Net" and r["Center"] == 2
        )
        self.assertEqual(net_c2["Amount"], 7)

    def test_formula_with_special_category_names(self):
        categories = {
            "Revenue Accounts": ["1234-5678"],
            "Expense-Accounts": ["9999-0000"],
        }
        formulas = {"Net Profit": "Revenue Accounts + Expense-Accounts"}
        calc = CategoryCalculator(categories, formulas)
        result = calc.compute(list(self.rows))
        profit = next(r for r in result if r["CAReportName"] == "Net Profit")
        self.assertEqual(profit["Amount"], -50)


class TestAccountCategoryDialog(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        from src.ui.account_category_dialog import AccountCategoryDialog

        self.Dialog = AccountCategoryDialog

    def test_account_list_populated(self):
        accounts = ["1111", "2222", "3333"]
        config = DummyConfig()
        dialog = self.Dialog(config, "Test", accounts)
        from PyQt6.QtCore import Qt

        self.assertEqual(dialog.account_list.count(), len(accounts))
        texts = [
            dialog.account_list.item(i).text()
            for i in range(dialog.account_list.count())
        ]
        self.assertEqual(texts, sorted(accounts))
        for i in range(dialog.account_list.count()):
            item = dialog.account_list.item(i)
            self.assertTrue(item.flags() & Qt.ItemFlag.ItemIsUserCheckable)
            self.assertEqual(item.checkState(), Qt.CheckState.Unchecked)

    def test_accounts_sorted_after_add(self):
        accounts = ["2222", "3333"]
        config = DummyConfig()
        dialog = self.Dialog(config, "Test", accounts)
        from PyQt6.QtWidgets import QInputDialog

        def fake_get_text(*args, **kwargs):
            return "1111", True

        QInputDialog.getText = staticmethod(fake_get_text)
        dialog._add_account()

        texts = [
            dialog.account_list.item(i).text()
            for i in range(dialog.account_list.count())
        ]
        self.assertEqual(texts, sorted(accounts + ["1111"]))

    def test_add_delete_and_save(self):
        config = DummyConfig()
        dialog = self.Dialog(config, "Test", [])

        from PyQt6.QtWidgets import QInputDialog

        QInputDialog.getText = staticmethod(lambda *a, **k: ("Cat1", True))
        dialog._add_category()
        QInputDialog.getText = staticmethod(lambda *a, **k: ("Form1", True))
        dialog._add_formula()

        dialog._delete_category()
        dialog._delete_formula()

        dialog.save()

        self.assertEqual(config.get_account_categories("Test"), {})
        self.assertEqual(config.get_account_formulas("Test"), {})

    def test_reject_discards_changes(self):
        config = DummyConfig()
        config.set_account_categories("Test", {"Orig": ["1"]})
        config.set_account_formulas("Test", {"F": "Orig"})

        dialog = self.Dialog(config, "Test", [])

        dialog.category_list.setCurrentRow(0)
        dialog._delete_category()
        dialog.formula_list.setCurrentRow(0)
        dialog._delete_formula()

        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.next_result = QMessageBox.StandardButton.Discard
        dialog.reject()

        self.assertEqual(config.get_account_categories("Test"), {"Orig": ["1"]})
        self.assertEqual(config.get_account_formulas("Test"), {"F": "Orig"})


if __name__ == "__main__":
    unittest.main()
