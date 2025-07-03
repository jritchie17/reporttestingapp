import pandas as pd
import os
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QHeaderView,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QToolBar,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt6.QtGui import QFont, QColor, QBrush, QAction

from src.utils.account_categories import CategoryCalculator
import numpy as np
import qtawesome as qta


class ResultsTableModel(QAbstractTableModel):
    def __init__(self, data, columns):
        super().__init__()
        self._data = data
        self._columns = columns

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()

        row, col = index.row(), index.column()

        try:
            # Try to get column name from columns
            if hasattr(self._columns, "__getitem__"):
                try:
                    col_name = self._columns[col]
                except (TypeError, IndexError):
                    # If columns is not subscriptable or col is out of range
                    if hasattr(self._columns, "keys"):
                        keys = list(self._columns.keys())
                        if 0 <= col < len(keys):
                            col_name = keys[col]
                        else:
                            col_name = f"Column_{col+1}"
                    else:
                        col_name = f"Column_{col+1}"
            else:
                col_name = f"Column_{col+1}"

            if role == Qt.ItemDataRole.DisplayRole:
                # Try to get value from data using column name
                try:
                    value = self._data[row].get(col_name)
                except (TypeError, IndexError, KeyError, AttributeError):
                    # If data access fails, try alternative approaches
                    try:
                        # Try accessing by index if not by name
                        value = (
                            list(self._data[row].values())[col]
                            if col < len(self._data[row])
                            else None
                        )
                    except (TypeError, IndexError, AttributeError):
                        value = None

                # Format the value for display
                if value is None:
                    return "NULL"
                elif isinstance(value, float):
                    # Format floats to avoid scientific notation and limit decimal places
                    return f"{value:.6f}".rstrip("0").rstrip(".")
                else:
                    return str(value)

        except Exception as e:
            # Fall back to a safe display value on any error
            if role == Qt.ItemDataRole.DisplayRole:
                return f"Error: {str(e)}"

        if role == Qt.ItemDataRole.BackgroundRole:
            # Alternate row colors for readability
            if row % 2 == 0:
                return QBrush(QColor(240, 240, 240))  # Slightly darker background
            else:
                return QBrush(QColor(255, 255, 255))  # White background for odd rows

        elif role == Qt.ItemDataRole.ForegroundRole:
            # Ensure text is always dark for good contrast
            return QBrush(QColor(0, 0, 0))

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            try:
                if hasattr(self._columns, "__getitem__"):
                    try:
                        col_name = self._columns[col]
                    except (TypeError, IndexError):
                        col_name = f"Column_{col+1}"
                else:
                    col_name = f"Column_{col+1}"

                value = self._data[row].get(col_name)
                if isinstance(value, (int, float)) and value is not None:
                    return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            except Exception:
                pass

            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        return QVariant()

    def flags(self, index):
        """Return item flags with editing enabled for the Issue column."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        base_flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

        try:
            col_name = self._columns[index.column()]
        except Exception:
            col_name = None

        if col_name == "Issue":
            return base_flags | Qt.ItemFlag.ItemIsEditable
        return base_flags

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """Update the underlying data and notify views."""
        if (
            not index.isValid()
            or role != Qt.ItemDataRole.EditRole
            or index.row() >= len(self._data)
        ):
            return False

        try:
            column_name = self._columns[index.column()]
        except Exception:
            return False

        self._data[index.row()][column_name] = value
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
        return True
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                try:
                    return str(self._columns[section])
                except (TypeError, IndexError):
                    # Handle case when _columns is not subscriptable or section is out of range
                    if hasattr(self._columns, "keys") and isinstance(
                        self._columns, dict
                    ):
                        # If it's a dict-like object, try to get keys
                        keys = list(self._columns.keys())
                        if 0 <= section < len(keys):
                            return str(keys[section])
                    # Default fallback
                    return f"Column {section+1}"
            else:
                return str(section + 1)  # 1-based row indexing

        elif role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setBold(True)
            return font

        return QVariant()


class ResultsViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.results_data = []
        self.original_data = []
        self.columns = []
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)

        # Create toolbar area
        self.create_toolbar(main_layout)

        # Create results table
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.SelectedClicked
        )
        self.table_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        self.table_view.horizontalHeader().setStretchLastSection(True)

        # Let the global theme handle table styling
        self.table_view.setStyleSheet("")

        main_layout.addWidget(self.table_view)

        # Add status area
        self.status_label = QLabel("No results to display")
        main_layout.addWidget(self.status_label)

    def create_toolbar(self, main_layout):
        """Create toolbar with data manipulation options"""
        toolbar = QToolBar()

        # Export results action
        export_action = QAction(qta.icon("fa5s.file-export"), "Export Results", self)
        export_action.triggered.connect(self.export_results)
        toolbar.addAction(export_action)

        # Copy to clipboard action
        copy_action = QAction(qta.icon("fa5s.copy"), "Copy to Clipboard", self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        toolbar.addAction(copy_action)

        # Clear results action
        clear_action = QAction(qta.icon("fa5s.trash-alt"), "Clear Results", self)
        clear_action.triggered.connect(self.clear_results)
        toolbar.addAction(clear_action)

        # Apply calculations action
        calc_action = QAction(qta.icon("fa5s.calculator"), "Apply Calculations", self)
        calc_action.triggered.connect(self.apply_calculations)
        toolbar.addAction(calc_action)

        # Add filter controls
        toolbar.addSeparator()

        self.filter_field = QLineEdit()
        self.filter_field.setPlaceholderText("Filter results...")
        self.filter_field.textChanged.connect(self.apply_filter)
        toolbar.addWidget(self.filter_field)

        main_layout.addWidget(toolbar)

    def load_results(self, data, columns=None):
        """Load results data into the viewer"""
        if not data:
            self.status_label.setText("No results to display")
            return

        # Store the raw results so calculations can be applied later
        self.results_data = list(data)
        self.original_data = list(data)

        # If columns not provided, try to get them from the first row
        if not columns and data:
            # Try to get keys from the first row dictionary
            try:
                self.columns = list(data[0].keys())
            except (AttributeError, IndexError, TypeError):
                # Fallback: create default column names
                self.columns = [
                    f"Column_{i+1}"
                    for i in range(
                        len(data[0]) if data and hasattr(data[0], "__len__") else 0
                    )
                ]
        else:
            # Ensure columns are strings to avoid any hashability issues
            self.columns = [str(col) for col in columns] if columns else []

        # Debug information
        print(f"Loading results with {len(data)} rows and {len(self.columns)} columns")
        if data and self.columns:
            # Debug: print first row data structure
            first_row = data[0]
            print(f"First row type: {type(first_row).__name__}")
            print(f"First row data: {first_row}")
            print(f"Columns: {self.columns}")

        # Create model and set it on table view
        self.model = ResultsTableModel(self.results_data, self.columns)
        self.table_view.setModel(self.model)

        # Auto-resize columns to contents
        self.table_view.resizeColumnsToContents()

        # Update status
        self.status_label.setText(
            f"{len(data)} rows, {len(self.columns)} columns returned"
        )

    def apply_calculations(self):
        """Append category totals and formulas to the current results."""
        if not self.results_data:
            return

        if not self.original_data:
            self.original_data = list(self.results_data)

        parent = self.window()
        try:
            from src.ui.main_window import MainWindow  # avoid circular import
        except Exception:
            MainWindow = None

        if (
            parent
            and MainWindow
            and isinstance(parent, MainWindow)
            and hasattr(parent, "config")
        ):
            report_type = parent.config.get("excel", "report_type")
            if report_type:
                categories = parent.config.get_account_categories(report_type)
                formulas = parent.config.get_account_formulas(report_type)
                if categories:
                    sheet_col = None
                    sheet_val = ""
                    if parent and hasattr(parent, "sheet_selector"):
                        try:
                            sheet_val = parent.sheet_selector.currentText()
                        except Exception:
                            sheet_val = ""
                    if not sheet_val and hasattr(parent, "config"):
                        sheet_val = parent.config.get("excel", "sheet_name") or ""

                    if self.results_data and isinstance(self.results_data[0], dict):
                        first_row = self.results_data[0]
                        lower_map = {k.lower(): k for k in first_row}
                        for cand in ["sheet", "sheet name", "sheet_name"]:
                            if cand.lower() in lower_map:
                                sheet_col = lower_map[cand.lower()]
                                break

                        if sheet_col:
                            for row in self.results_data:
                                if not row.get(sheet_col):
                                    row[sheet_col] = sheet_val

                    if sheet_col is None:
                        sheet_col = "Sheet"
                        if sheet_col not in self.columns:
                            self.columns.append(sheet_col)

                    group_col = sheet_col
                    if group_col is None and self.results_data and isinstance(self.results_data[0], dict):
                        first_row = self.results_data[0]
                        if "Center" in first_row:
                            group_col = "Center"

                    sign_flip = []
                    if parent and hasattr(parent, "comparison_engine"):
                        sign_flip = list(
                            getattr(parent.comparison_engine, "sign_flip_accounts", [])
                        )
                    calc = CategoryCalculator(
                        categories,
                        formulas,
                        group_column=group_col,
                        sign_flip_accounts=sign_flip,
                    )
                    default_group = None
                    if sheet_col and sheet_col not in self.results_data[0]:
                        default_group = sheet_val
                    base_data = self.original_data or self.results_data
                    self.results_data = calc.compute(list(base_data), default_group=default_group)

        # Refresh the table model with new rows
        self.model = ResultsTableModel(self.results_data, self.columns)
        self.table_view.setModel(self.model)
        self.table_view.resizeColumnsToContents()

        # Update status
        self.status_label.setText(
            f"{len(self.results_data)} rows, {len(self.columns)} columns returned"
        )

    def apply_filter(self, filter_text):
        """Apply a simple filter to the results"""
        if not self.results_data:
            return

        filter_text = filter_text.strip().lower()

        if not filter_text:
            # If filter is empty, restore original data
            filtered_data = self.results_data
        else:
            # Simple string matching filter across all columns
            filtered_data = []
            for row in self.results_data:
                row_values = [str(val).lower() for val in row.values()]
                if any(filter_text in val for val in row_values):
                    filtered_data.append(row)

        # Update model with filtered data
        self.model = ResultsTableModel(filtered_data, self.columns)
        self.table_view.setModel(self.model)

        # Update status
        self.status_label.setText(
            f"{len(filtered_data)} of {len(self.results_data)} rows displayed"
        )

    def export_results(self):
        """Export results to a file"""
        if not hasattr(self, "model") or not self.model or not self.model._data:
            QMessageBox.warning(self, "No Data", "There are no results to export.")
            return

        # Create a dataframe from the results
        df = pd.DataFrame(self.model._data)

        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json);;Text Files (*.txt)",
        )

        if not file_path:
            return

        try:
            # Export according to chosen format
            if file_path.lower().endswith(".csv"):
                df.to_csv(file_path, index=False)
            elif file_path.lower().endswith(".xlsx"):
                df.to_excel(file_path, index=False)
            elif file_path.lower().endswith(".json"):
                df.to_json(file_path, orient="records")
            elif file_path.lower().endswith(".txt"):
                with open(file_path, "w") as f:
                    # Create a simple tabular text format
                    f.write("\t".join(self.columns) + "\n")
                    for row in self.model._data:
                        f.write(
                            "\t".join(str(row.get(col, "")) for col in self.columns)
                            + "\n"
                        )
            else:
                # Default to CSV if no extension recognized
                if not any(
                    file_path.lower().endswith(ext)
                    for ext in [".csv", ".xlsx", ".json", ".txt"]
                ):
                    file_path += ".csv"
                df.to_csv(file_path, index=False)

            QMessageBox.information(
                self, "Export Successful", f"Results exported to {file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", f"Failed to export results: {str(e)}"
            )

    def copy_to_clipboard(self):
        """Copy results to clipboard"""
        if not hasattr(self, "model") or not self.model or not self.model._data:
            QMessageBox.warning(self, "No Data", "There are no results to copy.")
            return

        # Create a dataframe from the results
        df = pd.DataFrame(self.model._data)

        # Copy to clipboard
        df.to_clipboard(index=False)

        # Show success message
        QMessageBox.information(self, "Copy Successful", "Results copied to clipboard")

    def clear_results(self):
        """Clear all results data"""
        self.results_data = []
        self.original_data = []
        self.columns = []

        # Create empty model
        self.model = ResultsTableModel([], [])
        self.table_view.setModel(self.model)

        # Clear filter
        self.filter_field.clear()

        # Update status
        self.status_label.setText("No results to display")

    def has_results(self):
        """Check if there are any results loaded"""
        return bool(self.results_data)

    def get_dataframe(self):
        """Get the results as a pandas DataFrame"""
        if not hasattr(self, "model") or not self.model:
            return pd.DataFrame()

        return pd.DataFrame(self.model._data)

    def apply_widget_theme(self, theme: str):
        """Apply base style and theme colors to the results viewer."""
        themes_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "themes"
        )

        def load_qss(name: str) -> str:
            path = os.path.join(themes_dir, name)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            return ""

        qss = load_qss("base.qss")
        theme_lower = (theme or "").lower()
        if theme_lower and theme_lower != "system":
            qss += load_qss(f"{theme_lower}.qss")

        self.table_view.setStyleSheet(qss)
