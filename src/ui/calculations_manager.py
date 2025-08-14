from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QWidget,
    QPushButton,
    QDialogButtonBox,
    QMessageBox,
)
from copy import deepcopy

from src.utils.config import AppConfig, DEFAULT_SHEET_NAME
from src.ui.calculation_item import CalculationItem


# noinspection DuplicatedCode
class CalculationsManager(QDialog):
    """Dialog for editing report formulas."""

    def __init__(self, config: AppConfig, report_type: str, sheet_names=None, parent=None) -> None:
        super().__init__(parent)
        self.config = config
        self.report_type = report_type
        self.sheet_names = sheet_names or [DEFAULT_SHEET_NAME]
        if DEFAULT_SHEET_NAME in self.sheet_names and len(self.sheet_names) > 1:
            self.sheet_names.remove(DEFAULT_SHEET_NAME)
        if not self.sheet_names:
            self.sheet_names = [DEFAULT_SHEET_NAME]

        self.formulas = deepcopy(config.get_report_formulas(report_type))
        self._original = deepcopy(self.formulas)

        self._init_ui()

    # ------------------------------------------------------------------
    def _init_ui(self) -> None:
        self.setWindowTitle("Calculations Manager")
        layout = QVBoxLayout(self)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_widget_contents = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget_contents)
        self.scroll_area_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        layout.addWidget(self.scroll_area)

        # Add and Delete buttons
        btns = QHBoxLayout()
        add_btn = QPushButton("Add")
        del_btn = QPushButton("Delete")
        add_btn.clicked.connect(self._add_row)
        del_btn.clicked.connect(self._delete_row)

        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        layout.addLayout(btns)

        # Ok and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate_table()

    def _populate_table(self) -> None:
        """Populate the layout with existing formulas."""
        # Clear existing widgets
        for i in reversed(range(self.scroll_area_layout.count())):
            widget = self.scroll_area_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        for name, info in self.formulas.items():
            item = CalculationItem()
            item.set_data({
                "name": name,
                "expr": info.get("expr", ""),
                "display_name": info.get("display_name", ""),
                "sheets": info.get("sheets", []),
            })
            self.scroll_area_layout.addWidget(item)

    def _add_row(self) -> None:
        """Add a new calculation item."""
        item = CalculationItem()
        self.scroll_area_layout.addWidget(item)

    def _delete_row(self) -> None:
        """Delete the selected calculation item."""
        item = self.scroll_area_layout.itemAt(self.scroll_area_layout.count() - 1).widget()
        if item is not None:
            reply = QMessageBox.question(self, "Delete Item",
                                         "Are you sure you want to delete this item?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                item.deleteLater()

    def save(self) -> None:
        """Save the data from the UI to the config."""
        formulas: dict[str, dict] = {}
        for i in range(self.scroll_area_layout.count()):
            item = self.scroll_area_layout.itemAt(i).widget()
            if isinstance(item, CalculationItem):
                data = item.get_data()
                name = data.get("name")
                if name:
                    formulas[name] = {
                        "expr": data.get("expr", ""),
                        "display_name": data.get("display_name", ""),
                        "sheets": data.get("sheets", []),
                    }

        self.config.set_report_formulas(self.report_type, formulas)
        self._original = deepcopy(formulas)
        self.accept()

from PyQt6.QtCore import Qt
