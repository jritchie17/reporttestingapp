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
    QTabWidget,
    QWidget,
    QDialogButtonBox,
    QMessageBox,
)
from copy import deepcopy
from src.utils.config import AppConfig


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

    def __init__(self, config: AppConfig, report_type: str, accounts=None, parent=None) -> None:
        super().__init__(parent)
        self.config = config
        self.report_type = report_type
        self.categories = {
            name: list(accounts)
            for name, accounts in config.get_account_categories(report_type).items()
        }
        self.formulas = dict(config.get_account_formulas(report_type))

        category_accounts = {acct for lst in self.categories.values() for acct in lst}
        self.all_accounts = sorted(set(accounts or []) | category_accounts)

        self._original_categories = deepcopy(self.categories)
        self._original_formulas = deepcopy(self.formulas)

        self._init_ui()

    def _refresh_drag_categories(self) -> None:
        """Update the list of categories available for drag-and-drop."""
        if hasattr(self, "category_drag_list"):
            self.category_drag_list.clear()
            self.category_drag_list.addItems(sorted(self.categories.keys()))

    # UI setup
    def _init_ui(self) -> None:
        self.setWindowTitle("Account Categories")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Report type: {self.report_type}"))

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
        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
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
        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        right.addLayout(btns)

        layout.addLayout(right)
        self.tabs.addTab(tab, "Formulas")

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

    # Formula handlers
    def _on_formula_selected(self, current, previous):
        if previous and previous.text() in self.formulas:
            self.formulas[previous.text()] = self.formula_edit.text()
        if current:
            self.formula_edit.setText(self.formulas.get(current.text(), ""))
        else:
            self.formula_edit.clear()

    def _formula_changed(self):
        item = self.formula_list.currentItem()
        if item:
            self.formulas[item.text()] = self.formula_edit.text()

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
                self.formulas[name] = ""
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

    def save(self):
        # ensure current edits saved
        if self.category_list.currentItem():
            self.categories[self.category_list.currentItem().text()] = self._current_accounts()
        if self.formula_list.currentItem():
            self.formulas[self.formula_list.currentItem().text()] = self.formula_edit.text()

        self.config.set_account_categories(self.report_type, self.categories)
        self.config.set_account_formulas(self.report_type, self.formulas)
        self._original_categories = deepcopy(self.categories)
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
        if set(self.categories.keys()) != set(self._original_categories.keys()):
            return True
        for key, accounts in self.categories.items():
            if sorted(accounts) != sorted(self._original_categories.get(key, [])):
                return True
        return self.formulas != self._original_formulas
