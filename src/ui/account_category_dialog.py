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
)
from src.utils.config import AppConfig


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

        self.all_accounts = sorted(set(accounts or []))
        for acct_list in self.categories.values():
            for acct in acct_list:
                if acct not in self.all_accounts:
                    self.all_accounts.append(acct)

        self._init_ui()

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

    def _create_formulas_tab(self) -> None:
        tab = QWidget()
        layout = QHBoxLayout(tab)

        self.formula_list = QListWidget()
        self.formula_list.addItems(sorted(self.formulas.keys()))
        self.formula_list.currentItemChanged.connect(self._on_formula_selected)
        layout.addWidget(self.formula_list)

        right = QVBoxLayout()
        right.addWidget(QLabel("Formula expression (use category names):"))
        self.formula_edit = QLineEdit()
        self.formula_edit.textChanged.connect(self._formula_changed)
        right.addWidget(self.formula_edit)

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
        if previous:
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

    # Formula handlers
    def _on_formula_selected(self, current, previous):
        if previous:
            self.formulas[previous.text()] = self.formula_edit.text()
        if current:
            self.formula_edit.setText(self.formulas.get(current.text(), ""))
        else:
            self.formula_edit.clear()

    def _formula_changed(self):
        item = self.formula_list.currentItem()
        if item:
            self.formulas[item.text()] = self.formula_edit.text()

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
        self.accept()
