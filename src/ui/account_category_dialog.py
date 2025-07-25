from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLineEdit,
    QInputDialog,
    QLabel,
    QComboBox,
    QTabWidget,
    QWidget,
    QDialogButtonBox,
    QMessageBox,
)
from copy import deepcopy
from src.utils.config import AppConfig, DEFAULT_SHEET_NAME


class FormulaLineEdit(QLineEdit):
    """QLineEdit that accepts drops of category names."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):  # type: ignore[override]
        """Accept drags that contain text or come from a list widget."""

        if event.mimeData().hasText() or isinstance(event.source(), QListWidget):

            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):  # type: ignore[override]
        """Insert dragged category name into the line edit."""

        if event.mimeData().hasText():
            self.insert(event.mimeData().text())

            event.acceptProposedAction()
        elif isinstance(event.source(), QListWidget) and event.source().currentItem():
            self.insert(event.source().currentItem().text())

            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class AccountCategoryDialog(QDialog):
    """Dialog for managing account categories and formulas."""

    def __init__(
        self,
        config: AppConfig,
        report_type: str,
        accounts=None,
        sheet_names=None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.report_type = report_type

        existing_cats = config.config.get("account_categories", {}).get(report_type, {})
        names = set(sheet_names or []) | set(existing_cats.keys())
        names = {n for n in names if n}
        if DEFAULT_SHEET_NAME in names and len(names) > 1:
            names.remove(DEFAULT_SHEET_NAME)
        if not names:
            names = {DEFAULT_SHEET_NAME}
        self.sheet_names = sorted(names)
        self.current_sheet = self.sheet_names[0]

        self.categories_by_sheet = {
            sheet: {
                name: list(accts)
                for name, accts in config.get_account_categories(report_type, sheet).items()
            }
            for sheet in self.sheet_names
        }
        self.categories = deepcopy(self.categories_by_sheet.get(self.current_sheet, {}))
        self.formulas = deepcopy(config.get_report_formulas(report_type))

        category_accounts = {acct for lst in self.categories.values() for acct in lst}
        self.all_accounts = sorted(set(accounts or []) | category_accounts)

        self._original_categories = deepcopy(self.categories_by_sheet)
        self._original_formulas = deepcopy(self.formulas)

        self._init_ui()

    def refresh_accounts(self, accounts) -> None:
        """Refresh available accounts using ``accounts`` and current categories."""
        category_accounts = {acct for lst in self.categories.values() for acct in lst}
        self.all_accounts = sorted(set(accounts or []) | category_accounts)
        current = self._current_accounts()
        self._populate_account_list(current)

    def _refresh_drag_categories(self) -> None:
        """Update the list of categories available for drag-and-drop."""
        if hasattr(self, "category_drag_list"):
            self.category_drag_list.clear()
            self.category_drag_list.addItems(sorted(self.categories.keys()))

    def _refresh_formula_list(self) -> None:
        if hasattr(self, "formula_list"):
            current = self.formula_list.currentItem().text() if self.formula_list.currentItem() else None
            self.formula_list.clear()
            self.formula_list.addItems(sorted(self.formulas.keys()))
            if current and current in self.formulas:
                items = [self.formula_list.item(i) for i in range(self.formula_list.count()) if self.formula_list.item(i).text() == current]
                if items:
                    self.formula_list.setCurrentItem(items[0])
            if self.formula_list.currentItem():
                self.formula_edit.setText(self.formulas[self.formula_list.currentItem().text()].get("expr", ""))
                self.display_edit.setText(self.formulas[self.formula_list.currentItem().text()].get("display_name", ""))
                self._populate_sheet_checks(self.formulas[self.formula_list.currentItem().text()].get("sheets", []))

    def _save_current_sheet(self) -> None:
        """Store current edits into the per-sheet mappings."""
        if hasattr(self, "category_list") and self.category_list.currentItem():
            self.categories[self.category_list.currentItem().text()] = self._current_accounts()
        self.categories_by_sheet[self.current_sheet] = deepcopy(self.categories)

    def _load_sheet(self, sheet: str) -> None:
        """Load categories and formulas for ``sheet`` into the UI."""
        self.current_sheet = sheet
        self.categories = deepcopy(self.categories_by_sheet.get(sheet, {}))

        cat_accounts = {a for lst in self.categories.values() for a in lst}
        self.all_accounts = sorted(set(self.all_accounts) | cat_accounts)

        if hasattr(self, "category_list"):
            self.category_list.clear()
            self.category_list.addItems(sorted(self.categories.keys()))
            if self.category_list.count() > 0:
                first = self.category_list.item(0)
                self.category_list.setCurrentItem(first)
                self._populate_account_list(self.categories.get(first.text(), []))
            else:
                self._populate_account_list([])

        if hasattr(self, "formula_list"):
            self._refresh_formula_list()

        self._refresh_drag_categories()

    def _on_sheet_changed(self, sheet: str) -> None:
        self._save_current_sheet()
        self._load_sheet(sheet)

    # UI setup
    def _init_ui(self) -> None:
        self.setWindowTitle("Account Categories")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Report type: {self.report_type}"))

        if len(self.sheet_names) > 1 or self.sheet_names != [DEFAULT_SHEET_NAME]:
            sheet_layout = QHBoxLayout()
            sheet_layout.addWidget(QLabel("Sheet:"))
            self.sheet_selector = QComboBox()
            self.sheet_selector.addItems(self.sheet_names)
            self.sheet_selector.currentTextChanged.connect(self._on_sheet_changed)
            sheet_layout.addWidget(self.sheet_selector)
            layout.addLayout(sheet_layout)

        self.tabs = QTabWidget()
        self._create_categories_tab()
        self._create_formulas_tab()
        layout.addWidget(self.tabs)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _create_categories_tab(self) -> None:
        tab = QWidget()
        layout = QHBoxLayout(tab)

        self.category_list = QListWidget()
        self.category_list.addItems(sorted(self.categories.keys()))
        self.category_list.currentItemChanged.connect(self._on_category_selected)
        layout.addWidget(self.category_list)

        right = QVBoxLayout()
        right.addWidget(QLabel("Accounts:"))
        self.account_list = QListWidget()
        self.account_list.itemChanged.connect(self._accounts_changed)
        right.addWidget(self.account_list)

        add_account_btn = QPushButton("Add Account")
        add_account_btn.clicked.connect(self._add_account)

        btns = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_category)
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self._delete_category)
        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self._rename_category)
        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        btns.addWidget(rename_btn)
        btns.addWidget(add_account_btn)
        right.addLayout(btns)

        layout.addLayout(right)
        self.tabs.addTab(tab, "Categories")

        if self.category_list.count() > 0:
            first = self.category_list.item(0)
            self.category_list.setCurrentItem(first)
            self._populate_account_list(self.categories.get(first.text(), []))
        else:
            self._populate_account_list([])
        # Sync formula tab category list if it exists
        if hasattr(self, "category_drag_list"):
            self._refresh_drag_categories()

    def _create_formulas_tab(self) -> None:
        tab = QWidget()
        layout = QHBoxLayout(tab)

        self.formula_list = QListWidget()
        self.formula_list.addItems(sorted(self.formulas.keys()))
        self.formula_list.currentItemChanged.connect(self._on_formula_selected)
        layout.addWidget(self.formula_list)

        right = QVBoxLayout()

        right.addWidget(QLabel("Categories:"))
        self.category_drag_list = QListWidget()
        self.category_drag_list.addItems(sorted(self.categories.keys()))
        self.category_drag_list.setDragEnabled(True)
        right.addWidget(self.category_drag_list)

        right.addWidget(QLabel("Formula expression (use category names or account numbers):"))
        self.formula_edit = FormulaLineEdit()
        self.formula_edit.textChanged.connect(self._formula_changed)
        right.addWidget(self.formula_edit)

        right.addWidget(QLabel("Display name:"))
        self.display_edit = QLineEdit()
        self.display_edit.textChanged.connect(self._display_changed)
        right.addWidget(self.display_edit)

        right.addWidget(QLabel("Sheets:"))
        self.sheet_check_list = QListWidget()
        right.addWidget(self.sheet_check_list)
        self.sheet_check_list.itemChanged.connect(self._sheets_changed)

        ops = QHBoxLayout()
        for label, text in [
            ("+", "+"),
            ("-", "-"),
            ("*", "*"),
            ("/", "/"),
            ("*-1", "*-1"),
            ("(", "("),
            (")", ")"),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _=False, t=text: self._insert_formula_text(t))
            ops.addWidget(btn)
        right.addLayout(ops)

        btns = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_formula)
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self._delete_formula)
        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self._rename_formula)
        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        btns.addWidget(rename_btn)
        right.addLayout(btns)

        layout.addLayout(right)
        self.tabs.addTab(tab, "Formulas")

        if self.formula_list.count() > 0:
            first = self.formula_list.item(0)
            self.formula_list.setCurrentItem(first)
            info = self.formulas.get(first.text(), {})
            self.formula_edit.setText(info.get("expr", ""))
            self.display_edit.setText(info.get("display_name", ""))
            self._populate_sheet_checks(info.get("sheets", []))
        else:
            self.formula_edit.clear()
            self.display_edit.clear()
            self._populate_sheet_checks([])

    # Category handlers
    def _on_category_selected(self, current, previous):
        if previous and previous.text() in self.categories:
            name = previous.text()
            self.categories[name] = self._current_accounts()
        if current:
            name = current.text()
            self._populate_account_list(self.categories.get(name, []))
        else:
            self.account_list.clear()

    def _accounts_changed(self, *args):
        item = self.category_list.currentItem()
        if item:
            self.categories[item.text()] = self._current_accounts()

    def _current_accounts(self):
        accounts = []
        for i in range(self.account_list.count()):
            item = self.account_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                accounts.append(item.text())
        return accounts

    def _populate_account_list(self, checked_accounts):
        self.account_list.blockSignals(True)
        self.account_list.clear()
        for acct in self.all_accounts:
            item = QListWidgetItem(acct)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if acct in checked_accounts:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.account_list.addItem(item)
        self.account_list.blockSignals(False)

    def _populate_sheet_checks(self, checked_sheets):
        if not hasattr(self, "sheet_check_list"):
            return
        self.sheet_check_list.blockSignals(True)
        self.sheet_check_list.clear()
        for name in self.sheet_names:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if name in checked_sheets:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.sheet_check_list.addItem(item)
        self.sheet_check_list.blockSignals(False)

    def _add_account(self):
        account, ok = QInputDialog.getText(self, "Add Account", "Account number:")
        if ok and account:
            checked = self._current_accounts()
            if account not in self.all_accounts:
                self.all_accounts.append(account)
                self.all_accounts.sort()
                checked.append(account)
                self._populate_account_list(checked)
            self._accounts_changed()

    def _add_category(self):
        name, ok = QInputDialog.getText(self, "Add Category", "Category name:")
        if ok and name:
            if name not in self.categories:
                self.categories[name] = []
                self.category_list.addItem(name)
                self.category_list.setCurrentRow(self.category_list.count() - 1)
                self._refresh_drag_categories()

    def _delete_category(self):
        item = self.category_list.currentItem()
        if not item:
            return
        name = item.text()
        if name in self.categories:
            del self.categories[name]
        row = self.category_list.row(item)
        self.category_list.takeItem(row)
        self.account_list.clear()
        self._refresh_drag_categories()

    def _rename_category(self):
        item = self.category_list.currentItem()
        if not item:
            return
        old_name = item.text()
        new_name, ok = QInputDialog.getText(
            self, "Rename Category", "New category name:", text=old_name
        )
        if ok and new_name and new_name not in self.categories:
            accounts = self.categories.pop(old_name, [])
            self.categories[new_name] = accounts
            item.setText(new_name)
            self.category_list.setCurrentItem(item)
            self._refresh_drag_categories()
            # update formulas referencing the old name
            for fname, expr in list(self.formulas.items()):
                if old_name in expr:
                    self.formulas[fname] = expr.replace(old_name, new_name)
                    if (
                        self.formula_list.currentItem()
                        and self.formula_list.currentItem().text() == fname
                    ):
                        self.formula_edit.setText(self.formulas[fname])

    # Formula handlers
    def _on_formula_selected(self, current, previous):
        if previous and previous.text() in self.formulas:
            name = previous.text()
            info = self.formulas.setdefault(name, {})
            info["expr"] = self.formula_edit.text()
            info["display_name"] = self.display_edit.text()
            info["sheets"] = self._current_sheets()
        if current:
            info = self.formulas.get(current.text(), {})
            self.formula_edit.setText(info.get("expr", ""))
            self.display_edit.setText(info.get("display_name", ""))
            self._populate_sheet_checks(info.get("sheets", []))
        else:
            self.formula_edit.clear()
            self.display_edit.clear()
            self._populate_sheet_checks([])

    def _formula_changed(self):
        item = self.formula_list.currentItem()
        if item:
            self.formulas.setdefault(item.text(), {})["expr"] = self.formula_edit.text()

    def _display_changed(self):
        item = self.formula_list.currentItem()
        if item:
            self.formulas.setdefault(item.text(), {})["display_name"] = self.display_edit.text()

    def _current_sheets(self):
        sheets = []
        if hasattr(self, "sheet_check_list"):
            for i in range(self.sheet_check_list.count()):
                it = self.sheet_check_list.item(i)
                if it.checkState() == Qt.CheckState.Checked:
                    sheets.append(it.text())
        return sheets

    def _sheets_changed(self, *args):
        item = self.formula_list.currentItem()
        if item:
            self.formulas.setdefault(item.text(), {})["sheets"] = self._current_sheets()

    def _insert_formula_text(self, text: str) -> None:
        """Insert ``text`` at the current cursor position in the formula field."""
        cursor = self.formula_edit.cursorPosition()
        current = self.formula_edit.text()
        self.formula_edit.setText(current[:cursor] + text + current[cursor:])
        self.formula_edit.setCursorPosition(cursor + len(text))
        self._formula_changed()

    def _add_formula(self):
        name, ok = QInputDialog.getText(self, "Add Formula", "Formula name:")
        if ok and name:
            if name not in self.formulas:
                self.formulas[name] = {"expr": "", "display_name": "", "sheets": []}
                self.formula_list.addItem(name)
                self.formula_list.setCurrentRow(self.formula_list.count() - 1)

    def _delete_formula(self):
        item = self.formula_list.currentItem()
        if not item:
            return
        name = item.text()
        if name in self.formulas:
            del self.formulas[name]
        row = self.formula_list.row(item)
        self.formula_list.takeItem(row)
        self.formula_edit.clear()

    def _rename_formula(self):
        item = self.formula_list.currentItem()
        if not item:
            return
        old_name = item.text()
        new_name, ok = QInputDialog.getText(
            self, "Rename Formula", "New formula name:", text=old_name
        )
        if ok and new_name and new_name not in self.formulas:
            info = self.formulas.pop(old_name, {})
            self.formulas[new_name] = info
            item.setText(new_name)
            self.formula_list.setCurrentItem(item)

    def save(self):
        # ensure current edits saved
        self._save_current_sheet()

        for sheet in self.categories_by_sheet.keys():
            cats = self.categories_by_sheet.get(sheet, {})
            self.config.set_account_categories(self.report_type, cats, sheet)

        self.config.set_report_formulas(self.report_type, self.formulas)

        self._original_categories = deepcopy(self.categories_by_sheet)
        self._original_formulas = deepcopy(self.formulas)
        self.accept()

    def reject(self):
        """Prompt to save changes when closing without pressing OK."""
        if self._is_modified():
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Save changes before closing?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if result == QMessageBox.StandardButton.Save:
                self.save()
            elif result == QMessageBox.StandardButton.Discard:
                super().reject()
            else:
                return
        else:
            super().reject()

    def closeEvent(self, event):  # type: ignore[override]
        """Handle window close button to check for unsaved changes."""
        if self._is_modified():
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Save changes before closing?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if result == QMessageBox.StandardButton.Save:
                self.save()
                event.accept()
            elif result == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def _is_modified(self) -> bool:
        if set(self.categories_by_sheet.keys()) != set(self._original_categories.keys()):
            return True
        for sheet, mapping in self.categories_by_sheet.items():
            orig = self._original_categories.get(sheet, {})
            if set(mapping.keys()) != set(orig.keys()):
                return True
            for key, accounts in mapping.items():
                if sorted(accounts) != sorted(orig.get(key, [])):
                    return True
        return self.formulas != self._original_formulas
