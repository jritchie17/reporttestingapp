import os
import sys
import types
import tempfile
import unittest


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


class ReportConfigTests(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()

    def test_config_save_and_load(self):
        from src.utils.config import AppConfig

        with tempfile.TemporaryDirectory() as tmp:
            old_home = os.environ.get('HOME')
            os.environ['HOME'] = tmp

            cfg = AppConfig()
            rc = cfg.get_report_config('SOO PreClose')
            rc['skip_rows'] = 99
            cfg.set_report_config('SOO PreClose', rc)

            cfg2 = AppConfig()
            self.assertEqual(cfg2.get_report_config('SOO PreClose')['skip_rows'], 99)

            if old_home is not None:
                os.environ['HOME'] = old_home
            else:
                del os.environ['HOME']

    def test_clean_dataframe_uses_first_column(self):
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 1,
            'description': ''
        }

        import pandas as pd
        df = pd.DataFrame([
            ['H1', 'H2', 'H3'],
            ['skip1', 'skip2', 'skip3'],
            ['desc', '1', '2'],
            ['desc2', '3', '4']
        ])

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertEqual(cleaned.iloc[0, 1], 1)
        self.assertEqual(cleaned.iloc[1, 1], 3)


if __name__ == '__main__':
    unittest.main()

