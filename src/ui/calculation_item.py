from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QListWidget,
    QPushButton,
    QInputDialog,
    QMessageBox,
)
from PyQt6.QtWidgets import QLabel, QLineEdit, QComboBox



class CalculationItem(QWidget):
    """A widget representing a single calculation item."""
    def __init__(self, name: str = "", expression: str = "", display_name: str = "",
                 sheets: list[str] = None, accounts: list[str] = None, parent=None) -> None:
        super().__init__(parent)
        self.name = name
        self.expression = expression
        self.display_name = display_name
        self.sheets = sheets or []

        self._init_ui()


    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))

        self.name_edit = QLineEdit(self.name)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Account List (Assuming a QListWidget for accounts)
        self.accounts_list = QListWidget()
        self.accounts_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)  # Allow multiple accounts

        # Placeholder: Replace with your actual account data
        self.accounts_list.addItems(["Account 1", "Account 2", "Account 3"])

        layout.addWidget(QLabel("Accounts:"))
        # Display Name
        display_name_layout = QHBoxLayout()
        display_name_layout.addWidget(QLabel("Display Name:"))
        self.display_name_edit = QLineEdit(self.display_name)
        display_name_layout.addWidget(self.display_name_edit)
        layout.addLayout(display_name_layout)

        layout.addWidget(self.accounts_list)
        # Sheets
        sheets_layout = QHBoxLayout()
        sheets_layout.addWidget(QLabel("Sheets:"))
        self.sheets_combo = QComboBox()
        self.sheets_combo.addItems(self.sheets)  # Initialize with available sheets
        self.sheets_combo.setEditable(True)  # Allow manual entry
        sheets_layout.addWidget(self.sheets_combo)


        sheets_btns = QHBoxLayout()
        add_sheet_btn = QPushButton("Add/Edit Sheet")
        del_sheet_btn = QPushButton("Delete Sheet")
        add_sheet_btn.clicked.connect(self._add_sheet)
        del_sheet_btn.clicked.connect(self._delete_sheet)
        sheets_btns.addWidget(add_sheet_btn)
        sheets_btns.addWidget(del_sheet_btn)
        sheets_layout.addLayout(sheets_btns)

        layout.addLayout(sheets_layout)

    def _add_sheet(self) -> None:
        """Add or edit a sheet in the combo box."""
        text, ok = QInputDialog.getText(self, "Add/Edit Sheet", "Enter sheet name:")
        if ok and text:
            if text not in [self.sheets_combo.itemText(i) for i in range(self.sheets_combo.count())]:
                self.sheets_combo.addItem(text)
                self.sheets.append(text)  # Update the internal list
            else:
                index = self.sheets_combo.findText(text)
                self.sheets_combo.setCurrentIndex(index)

    def _delete_sheet(self) -> None:
        """Delete the currently selected sheet."""
        current_text = self.sheets_combo.currentText()
        index = self.sheets_combo.currentIndex()
        if index >= 0:
            self.sheets_combo.removeItem(index)
            self.sheets.remove(current_text)  # Update the internal list

    def _delete_sheet_list(self) -> None:
        row = self.sheets_list.currentRow()
        if row >= 0:
            sheet = self.sheets_list.item(row).text()
            self.sheets.remove(sheet)
            self.sheets_list.takeItem(row)

    def get_data(self) -> dict:
        """Collect data from the UI."""
        return {
            "name": self.name_edit.text(),
            "expr": self.expression_edit.text(),
            "display_name": self.display_name_edit.text(),
            "sheets": [self.sheets_combo.itemText(i) for i in range(self.sheets_combo.count())],
        }

    def set_data(self, data: dict) -> None:
        """Set data to UI."""
        self.name_edit.setText(data.get("name", ""))
        self.expression_edit.setText(data.get("expr", ""))

        self.display_name_edit.setText(data.get("display_name", ""))

        self.sheets = data.get("sheets", [])
        self.sheets_combo.clear()
        self.sheets_combo.addItems(self.sheets)

    def _insert_operator(self, operator):
        """Insert an operator into the expression at the current cursor position."""
        cursor_pos = self.expression_edit.cursorPosition()
        current_text = self.expression_edit.text()
        new_text = current_text[:cursor_pos] + operator + current_text[cursor_pos:]
        self.expression_edit.setText(new_text)
        self.expression_edit.setCursorPosition(cursor_pos + len(operator))

    def clear_data(self) -> None:
        """Clear data in UI."""
        self.name_edit.clear()
        self.expression_edit.clear()

        self.display_name_edit.clear()
        self.sheets_list.clear()
