import os
import sys
import types
import pandas as pd
import unittest

from src.utils.account_categories import CategoryCalculator

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


def patch_qt_modules():
    """Provide minimal PyQt6 stubs so AccountCategoryDialog can be imported."""
    class Signal:
        def __init__(self):
            self._slots = []

        def connect(self, slot):
            self._slots.append(slot)

        def emit(self, *args, **kwargs):
            for s in list(self._slots):
                s(*args, **kwargs)

    class Qt:
        class ItemFlag:
            ItemIsUserCheckable = 1

        class CheckState:
            Unchecked = 0
            Checked = 2

    class QListWidgetItem:
        def __init__(self, text=""):
            self._text = text
            self._flags = 0
            self._check_state = Qt.CheckState.Unchecked

        def text(self):
            return self._text

        def setFlags(self, flags):
            self._flags = flags

        def flags(self):
            return self._flags

        def setCheckState(self, state):
            self._check_state = state

        def checkState(self):
            return self._check_state

    class QListWidget:
        def __init__(self):
            self.items = []
            self.currentItemChanged = Signal()
            self.itemChanged = Signal()
            self._current = None

        def addItems(self, items):
            for text in items:
                self.addItem(QListWidgetItem(text))

        def addItem(self, item):
            if isinstance(item, str):
                item = QListWidgetItem(item)
            self.items.append(item)

        def item(self, index):
            return self.items[index]

        def count(self):
            return len(self.items)

        def clear(self):
            self.items.clear()

        def blockSignals(self, flag):
            pass

        def setCurrentItem(self, item):
            prev = self._current
            self._current = item
            self.currentItemChanged.emit(item, prev)

        def currentItem(self):
            return self._current

    class QWidget:
        def __init__(self, *args, **kwargs):
            pass

        def addWidget(self, *args, **kwargs):
            pass

        def addLayout(self, *args, **kwargs):
            pass

    class QDialog(QWidget):
        pass

    class QVBoxLayout(QWidget):
        pass

    class QHBoxLayout(QWidget):
        pass

    class QPushButton(QWidget):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.clicked = Signal()

    class QLineEdit(QWidget):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self._text = ""
            self.textChanged = Signal()

        def text(self):
            return self._text

        def setText(self, text):
            self._text = text
            self.textChanged.emit(text)

    class QLabel(QWidget):
        pass

    class QTabWidget(QWidget):
        def addTab(self, *args, **kwargs):
            pass

    class QDialogButtonBox(QWidget):
        class StandardButton:
            Ok = 1
            Cancel = 2

        def __init__(self, *args, **kwargs):
            super().__init__()
            self.accepted = Signal()
            self.rejected = Signal()

    class QInputDialog:
        @staticmethod
        def getText(*args, **kwargs):
            return "", False

    widgets = types.ModuleType('PyQt6.QtWidgets')
    for name, obj in {
        'QDialog': QDialog,
        'QVBoxLayout': QVBoxLayout,
        'QHBoxLayout': QHBoxLayout,
        'QListWidget': QListWidget,
        'QListWidgetItem': QListWidgetItem,
        'QPushButton': QPushButton,
        'QLineEdit': QLineEdit,
        'QInputDialog': QInputDialog,
        'QLabel': QLabel,
        'QTabWidget': QTabWidget,
        'QWidget': QWidget,
        'QDialogButtonBox': QDialogButtonBox,
    }.items():
        setattr(widgets, name, obj)

    core = types.ModuleType('PyQt6.QtCore')
    core.Qt = Qt

    sys.modules.setdefault('PyQt6', types.ModuleType('PyQt6'))
    sys.modules['PyQt6.QtWidgets'] = widgets
    sys.modules['PyQt6.QtCore'] = core
    sys.modules.setdefault('PyQt6.QtGui', types.ModuleType('PyQt6.QtGui'))


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
        df = pd.read_csv(os.path.join(FIXTURES, 'sql_data.csv'))
        self.rows = df.to_dict(orient='records')
        self.categories = {
            'CatA': ['1234-5678'],
            'CatB': ['9999-0000'],
        }
        self.formulas = {
            'Net': 'CatA + CatB'
        }

    def test_compute_totals_and_formulas(self):
        calc = CategoryCalculator(self.categories, self.formulas)
        result = calc.compute(list(self.rows))
        self.assertEqual(len(result), len(self.rows) + 3)
        cat_a = next(r for r in result if r['CAReportName'] == 'CatA')
        self.assertEqual(cat_a['Amount'], -100)
        cat_b = next(r for r in result if r['CAReportName'] == 'CatB')
        self.assertEqual(cat_b['Amount'], 50)
        net = next(r for r in result if r['CAReportName'] == 'Net')
        self.assertEqual(net['Amount'], -50)

    def test_compute_detects_account_column(self):
        rows = [
            {'Center': 1, 'Account': '1234-5678', 'Amount': -100},
            {'Center': 2, 'Account': '9999-0000', 'Amount': 50},
        ]
        calc = CategoryCalculator(self.categories, self.formulas)
        result = calc.compute(rows)
        self.assertEqual(len(result), len(rows) + 3)
        cat_a = next(r for r in result if r['Account'] == 'CatA')
        self.assertEqual(cat_a['Amount'], -100)
        cat_b = next(r for r in result if r['Account'] == 'CatB')
        self.assertEqual(cat_b['Amount'], 50)
        net = next(r for r in result if r['Account'] == 'Net')
        self.assertEqual(net['Amount'], -50)

    def test_grouped_totals_and_formulas(self):
        calc = CategoryCalculator(self.categories, self.formulas, group_column="Center")
        result = calc.compute(list(self.rows))
        self.assertEqual(len(result), len(self.rows) + 6)

        cat_a_c1 = next(r for r in result if r['CAReportName'] == 'CatA' and r['Center'] == 1)
        self.assertEqual(cat_a_c1['Amount'], -100)
        cat_b_c2 = next(r for r in result if r['CAReportName'] == 'CatB' and r['Center'] == 2)
        self.assertEqual(cat_b_c2['Amount'], 50)

        net_c1 = next(r for r in result if r['CAReportName'] == 'Net' and r['Center'] == 1)
        self.assertEqual(net_c1['Amount'], -100)
        net_c2 = next(r for r in result if r['CAReportName'] == 'Net' and r['Center'] == 2)
        self.assertEqual(net_c2['Amount'], 50)


class TestAccountCategoryDialog(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        from src.ui.account_category_dialog import AccountCategoryDialog
        self.Dialog = AccountCategoryDialog

    def test_account_list_populated(self):
        accounts = ['1111', '2222', '3333']
        config = DummyConfig()
        dialog = self.Dialog(config, 'Test', accounts)
        from PyQt6.QtCore import Qt

        self.assertEqual(dialog.account_list.count(), len(accounts))
        texts = [dialog.account_list.item(i).text() for i in range(dialog.account_list.count())]
        self.assertEqual(texts, sorted(accounts))
        for i in range(dialog.account_list.count()):
            item = dialog.account_list.item(i)
            self.assertTrue(item.flags() & Qt.ItemFlag.ItemIsUserCheckable)
            self.assertEqual(item.checkState(), Qt.CheckState.Unchecked)

    def test_accounts_sorted_after_add(self):
        accounts = ['2222', '3333']
        config = DummyConfig()
        dialog = self.Dialog(config, 'Test', accounts)
        from PyQt6.QtWidgets import QInputDialog

        def fake_get_text(*args, **kwargs):
            return '1111', True

        QInputDialog.getText = staticmethod(fake_get_text)
        dialog._add_account()

        texts = [dialog.account_list.item(i).text() for i in range(dialog.account_list.count())]
        self.assertEqual(texts, sorted(accounts + ['1111']))


if __name__ == '__main__':
    unittest.main()
