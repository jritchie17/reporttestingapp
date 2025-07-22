from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QDialogButtonBox,
)
from copy import deepcopy

from src.utils.config import AppConfig, DEFAULT_SHEET_NAME


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

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Name", "Expression", "Display name", "Sheets"])
        layout.addWidget(self.table)

        btns = QHBoxLayout()
        add_btn = QPushButton("Add")
        del_btn = QPushButton("Delete")
        add_btn.clicked.connect(self._add_row)
        del_btn.clicked.connect(self._delete_row)
        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        layout.addLayout(btns)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate_table()

    def _populate_table(self) -> None:
        self.table.setRowCount(0)
        for name, info in self.formulas.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(info.get("expr", "")))
            self.table.setItem(row, 2, QTableWidgetItem(info.get("display_name", "")))
            sheets = ",".join(info.get("sheets") or [])
            self.table.setItem(row, 3, QTableWidgetItem(sheets))

    def _add_row(self) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col in range(4):
            self.table.setItem(row, col, QTableWidgetItem(""))

    def _delete_row(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def save(self) -> None:
        formulas: dict[str, dict] = {}
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            expr_item = self.table.item(row, 1)
            disp_item = self.table.item(row, 2)
            sheets_item = self.table.item(row, 3)
            if not name_item or not name_item.text():
                continue
            name = name_item.text()
            info = {
                "expr": expr_item.text() if expr_item else "",
                "display_name": disp_item.text() if disp_item else name,
            }
            sheets = [s.strip() for s in (sheets_item.text() if sheets_item else "").split(',') if s.strip()]
            if sheets:
                info["sheets"] = sheets
            formulas[name] = info

        self.config.set_report_formulas(self.report_type, formulas)
        self._original = deepcopy(formulas)
        self.accept()

