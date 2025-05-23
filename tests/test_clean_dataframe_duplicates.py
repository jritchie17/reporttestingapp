import os
import sys
import types
import unittest

import pandas as pd


def patch_qt_modules():
    """Provide minimal PyQt stubs so ExcelViewer can be imported."""
    widgets = types.ModuleType('PyQt6.QtWidgets')
    widget_attrs = [
        'QWidget', 'QVBoxLayout', 'QHBoxLayout', 'QTableView', 'QLabel',
        'QPushButton', 'QComboBox', 'QLineEdit', 'QHeaderView', 'QSplitter',
        'QCheckBox', 'QGroupBox', 'QFormLayout', 'QSpinBox', 'QTabWidget',
        'QStyledItemDelegate', 'QInputDialog', 'QListWidget', 'QDialog',
        'QTextEdit', 'QDialogButtonBox', 'QRadioButton', 'QButtonGroup',
        'QListWidgetItem'
    ]
    for attr in widget_attrs:
        setattr(widgets, attr, type(attr, (), {}))

    core = types.ModuleType('PyQt6.QtCore')
    for attr in [
        'Qt', 'QAbstractTableModel', 'QModelIndex', 'QVariant',
        'pyqtSignal', 'QEvent', 'QSize'
    ]:
        setattr(core, attr, type(attr, (), {}))

    gui = types.ModuleType('PyQt6.QtGui')
    for attr in ['QFont', 'QColor', 'QBrush', 'QIcon', 'QGuiApplication', 'QCursor']:
        setattr(gui, attr, type(attr, (), {}))

    sys.modules.setdefault('PyQt6', types.ModuleType('PyQt6'))
    sys.modules['PyQt6.QtWidgets'] = widgets
    sys.modules['PyQt6.QtCore'] = core
    sys.modules['PyQt6.QtGui'] = gui

    qta = types.ModuleType('qtawesome')
    qta.icon = lambda *args, **kwargs: None
    sys.modules['qtawesome'] = qta


class TestCleanDataframeDuplicates(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()

    def test_duplicate_headers_converted(self):
        from src.ui.excel_viewer import ExcelViewer

        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 1,
            'description': ''
        }

        df = pd.DataFrame([
            ['A', 'A', 'B'],
            ['desc', '1', '2'],
            ['desc2', '3', '4']
        ])

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        self.assertEqual(list(cleaned.columns), ['Sheet_Name', 'A', 'A_1', 'B'])
        self.assertEqual(cleaned.iloc[0, 2], 1.0)
        self.assertEqual(cleaned.iloc[1, 2], 3.0)
        self.assertTrue(pd.api.types.is_float_dtype(cleaned['A_1']))


if __name__ == '__main__':
    unittest.main()
