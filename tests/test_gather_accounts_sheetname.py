import os
import sys
import types
import unittest
from unittest.mock import MagicMock

import pandas as pd
from src.analyzer.excel_analyzer import ExcelAnalyzer


def patch_qt_modules():
    """Patch PyQt6 and related UI modules so main_window can be imported."""
    widgets = types.ModuleType('PyQt6.QtWidgets')
    widget_attrs = [
        "QMainWindow", "QTabWidget", "QApplication", "QWidget", "QVBoxLayout",
        "QHBoxLayout", "QLabel", "QPushButton", "QFileDialog", "QMessageBox",
        "QStatusBar", "QMenuBar", "QMenu", "QToolBar", "QSplitter",
        "QComboBox", "QLineEdit", "QProgressDialog", "QDialog", "QListWidget",
        "QDialogButtonBox"
    ]
    for attr in widget_attrs:
        setattr(widgets, attr, type(attr, (), {}))

    core = types.ModuleType('PyQt6.QtCore')
    for attr in ["Qt", "QSize"]:
        setattr(core, attr, type(attr, (), {}))

    gui = types.ModuleType('PyQt6.QtGui')
    for attr in ["QIcon", "QAction", "QFont"]:
        setattr(gui, attr, type(attr, (), {}))

    sys.modules.setdefault('PyQt6', types.ModuleType('PyQt6'))
    sys.modules['PyQt6.QtWidgets'] = widgets
    sys.modules['PyQt6.QtCore'] = core
    sys.modules['PyQt6.QtGui'] = gui

    qta = types.ModuleType('qtawesome')
    qta.icon = lambda *args, **kwargs: None
    sys.modules['qtawesome'] = qta

    for name in [
        'src.ui.excel_viewer', 'src.ui.sql_editor', 'src.ui.results_viewer',
        'src.ui.comparison_view', 'src.ui.settings_dialog',
        'src.ui.account_category_dialog', 'src.ui.report_config_dialog',
        'src.ui.hover_anim_filter'
    ]:
        sys.modules.setdefault(name, types.ModuleType(name))


class TestGatherAccountsSheetName(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        # Create dataframe where the account column is second and Sheet_Name is first
        df = pd.DataFrame({
            'Sheet_Name': ['Sheet1', 'Sheet1'],
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
