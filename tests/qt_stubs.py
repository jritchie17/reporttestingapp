import sys
import types


def patch_qt_modules():
    """Patch PyQt6 and supporting UI modules with simple stubs."""
    if "PyQt6.QtWidgets" in sys.modules:
        return

    widgets = types.ModuleType("PyQt6.QtWidgets")
    core = types.ModuleType("PyQt6.QtCore")
    gui = types.ModuleType("PyQt6.QtGui")

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
            NoItemFlags = 0
            ItemIsUserCheckable = 1
            ItemIsSelectable = 2
            ItemIsEnabled = 4
            ItemIsEditable = 8

        class CheckState:
            Unchecked = 0
            Checked = 2

        class ItemDataRole:
            DisplayRole = 0
            BackgroundRole = 1
            ForegroundRole = 2
            TextAlignmentRole = 3
            FontRole = 4
            EditRole = 5

        class AlignmentFlag:
            AlignRight = 0x0002
            AlignVCenter = 0x0080
            AlignLeft = 0x0001

        class Orientation:
            Horizontal = 0
            Vertical = 1

    class QListWidgetItem:
        def __init__(self, text=""):
            self._text = text
            self._flags = 0
            self._check_state = Qt.CheckState.Unchecked

        def text(self):
            return self._text

        def setText(self, text):
             self._text = text

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

        def setCurrentRow(self, row):
            if 0 <= row < len(self.items):
                self.setCurrentItem(self.items[row])
            else:
                self.setCurrentItem(None)

        def row(self, item):
            try:
                return self.items.index(item)
            except ValueError:
                return -1

        def takeItem(self, row):
            if 0 <= row < len(self.items):
                return self.items.pop(row)

    class QWidget:
        def __init__(self, *args, **kwargs):
            pass

        def addWidget(self, *args, **kwargs):
            pass

        def addLayout(self, *args, **kwargs):
            pass

    class QDialog(QWidget):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self._title = ""

        def accept(self):
            pass

        def reject(self):
            pass

        def setWindowTitle(self, title):
            self._title = title

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

        def clear(self):
            self.setText("")

    class QLabel(QWidget):
        pass

    class QComboBox(QWidget):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.items = []
            self.currentTextChanged = Signal()
            self._current = ""

        def addItems(self, items):
            self.items.extend(items)
            if items:
                self._current = items[0]

        def currentText(self):
            return self._current

        def clear(self):
            self.items.clear()
            self._current = ""

    class QTabWidget(QWidget):
        def addTab(self, *args, **kwargs):
            pass

    class QDialogButtonBox(QWidget):
        class StandardButton:
            Ok = 1
            Cancel = 2
            Save = 1
            Discard = 2

        def __init__(self, *args, **kwargs):
            super().__init__()
            self.accepted = Signal()
            self.rejected = Signal()

    class QMessageBox:
        class StandardButton:
            Save = 1
            Discard = 2
            Cancel = 3

        next_result = StandardButton.Save

        @staticmethod
        def question(*args, **kwargs):
            return QMessageBox.next_result

        @staticmethod
        def warning(*args, **kwargs):
            pass

        @staticmethod
        def critical(*args, **kwargs):
            pass

    class QInputDialog:
        @staticmethod
        def getText(*args, **kwargs):
            return "", False

        @staticmethod
        def getItem(*args, **kwargs):
            return "", False

    # Add complex widget classes
    for name, obj in {
        "QDialog": QDialog,
        "QVBoxLayout": QVBoxLayout,
        "QHBoxLayout": QHBoxLayout,
        "QListWidget": QListWidget,
        "QListWidgetItem": QListWidgetItem,
        "QPushButton": QPushButton,
        "QLineEdit": QLineEdit,
        "QComboBox": QComboBox,
        "QInputDialog": QInputDialog,
        "QMessageBox": QMessageBox,
        "QLabel": QLabel,
        "QTabWidget": QTabWidget,
        "QWidget": QWidget,
        "QDialogButtonBox": QDialogButtonBox,
    }.items():
        setattr(widgets, name, obj)

    # Simple stub classes for remaining widgets
    simple_widgets = [
        "QMainWindow",
        "QTabWidget",  # already defined but harmless
        "QApplication",
        "QMenuBar",
        "QMenu",
        "QToolBar",
        "QStatusBar",
        "QSplitter",
        "QComboBox",
        "QProgressDialog",
        "QFileDialog",
        "QTableView",
        "QHeaderView",
        "QCheckBox",
        "QGroupBox",
        "QFormLayout",
        "QSpinBox",
        "QStyledItemDelegate",
        "QDialog",
        "QListWidget",
        "QTextEdit",
        "QRadioButton",
        "QButtonGroup",
        "QWizard",
        "QWizardPage",
    ]

    for name in simple_widgets:
        if not hasattr(widgets, name):
            setattr(widgets, name, type(name, (), {}))

    core.Qt = Qt
    core.QSize = type("QSize", (), {})
    core.QAbstractTableModel = type("QAbstractTableModel", (), {})
    core.QModelIndex = type("QModelIndex", (), {})
    core.QVariant = type("QVariant", (), {})
    core.QUrl = type("QUrl", (), {"fromLocalFile": staticmethod(lambda *a, **k: None)})
    core.pyqtSignal = Signal
    core.QEvent = type("QEvent", (), {})

    for attr in ["QIcon", "QAction", "QFont", "QColor", "QBrush", "QGuiApplication", "QCursor", "QDesktopServices"]:
        setattr(gui, attr, type(attr, (), {"openUrl": staticmethod(lambda *a, **k: None)}) if attr == "QDesktopServices" else type(attr, (), {}))

    sys.modules.setdefault("PyQt6", types.ModuleType("PyQt6"))
    sys.modules["PyQt6.QtWidgets"] = widgets
    sys.modules["PyQt6.QtCore"] = core
    sys.modules["PyQt6.QtGui"] = gui

    qta = types.ModuleType("qtawesome")
    qta.icon = lambda *args, **kwargs: None
    sys.modules["qtawesome"] = qta

    for name in [
        "src.ui.excel_viewer",
        "src.ui.sql_editor",
        "src.ui.results_viewer",
        "src.ui.comparison_view",
        "src.ui.settings_dialog",
        "src.ui.account_category_dialog",
        "src.ui.report_config_dialog",
        "src.ui.hover_anim_filter",
        "src.ui.workflow_wizard",
    ]:
        sys.modules.setdefault(name, types.ModuleType(name))

    # Provide minimal HoverAnimationFilter stub
    sys.modules["src.ui.hover_anim_filter"].HoverAnimationFilter = type(
        "HoverAnimationFilter", (), {}
    )
    # Provide minimal ExcelViewer stub
    sys.modules["src.ui.excel_viewer"].ExcelViewer = type(
        "ExcelViewer", (), {}
    )
    # Provide minimal stubs for other UI components
    sys.modules["src.ui.sql_editor"].SQLEditor = type("SQLEditor", (), {})
    sys.modules["src.ui.comparison_view"].ComparisonView = type(
        "ComparisonView", (), {}
    )
    sys.modules["src.ui.settings_dialog"].SettingsDialog = type(
        "SettingsDialog", (), {}
    )
    sys.modules["src.ui.account_category_dialog"].AccountCategoryDialog = type(
        "AccountCategoryDialog", (), {}
    )
    sys.modules["src.ui.report_config_dialog"].ReportConfigDialog = type(
        "ReportConfigDialog", (), {}
    )
    sys.modules["src.ui.workflow_wizard"].WorkflowWizard = type(
        "WorkflowWizard", (), {}
    )
    sys.modules["src.ui.results_viewer"].ResultsViewer = type(
        "ResultsViewer", (), {}
    )

