from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLineEdit,
    QLabel,
    QSpinBox,
    QDialogButtonBox,
    QInputDialog,
)
from PyQt6.QtCore import Qt
from copy import deepcopy
from src.utils.config import AppConfig


class ReportConfigDialog(QDialog):
    """Dialog for creating and editing report configurations."""

    def __init__(self, config: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self.config = config
        self.configs = deepcopy(config.get("report_configs") or {})
        self._original_configs = deepcopy(self.configs)
        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle("Report Configurations")
        layout = QVBoxLayout(self)

        body = QHBoxLayout()
        self.config_list = QListWidget()
        self.config_list.addItems(sorted(self.configs.keys()))
        self.config_list.currentItemChanged.connect(self._on_selected)
        body.addWidget(self.config_list)

        right = QVBoxLayout()
        right.addWidget(QLabel("Header rows (comma separated, 1-indexed):"))
        self.header_edit = QLineEdit()
        right.addWidget(self.header_edit)

        right.addWidget(QLabel("Rows to skip:"))
        self.skip_spin = QSpinBox()
        self.skip_spin.setMinimum(0)
        right.addWidget(self.skip_spin)

        right.addWidget(QLabel("First data column index:"))
        self.first_col_spin = QSpinBox()
        self.first_col_spin.setMinimum(0)
        self.first_col_spin.setValue(2)
        right.addWidget(self.first_col_spin)

        right.addWidget(QLabel("Center cell (optional):"))
        self.center_cell_edit = QLineEdit()
        right.addWidget(self.center_cell_edit)

        right.addWidget(QLabel("Description:"))
        self.desc_edit = QLineEdit()
        right.addWidget(self.desc_edit)

        btns = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_config)
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self._delete_config)
        btns.addWidget(add_btn)
        btns.addWidget(del_btn)
        right.addLayout(btns)

        body.addLayout(right)
        layout.addLayout(body)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if self.config_list.count() > 0:
            self.config_list.setCurrentRow(0)
        else:
            self._clear_fields()

    def _clear_fields(self) -> None:
        self.header_edit.clear()
        self.skip_spin.setValue(0)
        self.first_col_spin.setValue(2)
        self.center_cell_edit.clear()
        self.desc_edit.clear()

    def _on_selected(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        if previous:
            self._save_config(previous.text())
        if current:
            cfg = self.configs.get(current.text(), {})
            self.header_edit.setText(
                ", ".join(str(i + 1) for i in cfg.get("header_rows", []))
            )
            self.skip_spin.setValue(cfg.get("skip_rows", 0))
            self.first_col_spin.setValue(cfg.get("first_data_column", 2))
            self.center_cell_edit.setText(str(cfg.get("center_cell", "") or ""))
            self.desc_edit.setText(cfg.get("description", ""))
        else:
            self._clear_fields()

    def _save_config(self, name: str) -> None:
        rows = [
            int(v.strip()) - 1 for v in self.header_edit.text().split(",") if v.strip()
        ]
        self.configs[name] = {
            "header_rows": rows,
            "skip_rows": self.skip_spin.value(),
            "first_data_column": self.first_col_spin.value(),
            "center_cell": self.center_cell_edit.text().strip() or None,
            "description": self.desc_edit.text(),
        }

    def _add_config(self) -> None:
        name, ok = QInputDialog.getText(self, "Add Report Type", "Name:")
        if ok and name and name not in self.configs:
            self.configs[name] = {
                "header_rows": [],
                "skip_rows": 0,
                "first_data_column": 2,
                "center_cell": None,
                "description": "",
            }
            self.config_list.addItem(name)
            self.config_list.setCurrentRow(self.config_list.count() - 1)

    def _delete_config(self) -> None:
        item = self.config_list.currentItem()
        if not item:
            return
        name = item.text()
        if name in self.configs:
            del self.configs[name]
        row = self.config_list.row(item)
        self.config_list.takeItem(row)
        self._clear_fields()

    def save(self) -> None:
        if self.config_list.currentItem():
            self._save_config(self.config_list.currentItem().text())
        self.config.config["report_configs"] = self.configs
        self.config.save_config()
        self.accept()
