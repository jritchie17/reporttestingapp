import pandas as pd
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView, 
                             QLabel, QPushButton, QComboBox, QLineEdit, 
                             QHeaderView, QSplitter, QCheckBox, QGroupBox,
                             QFormLayout, QSpinBox, QTabWidget, QStyledItemDelegate,
                             QInputDialog, QListWidget, QDialog, QTextEdit,
                             QDialogButtonBox, QRadioButton, QButtonGroup, QListWidgetItem)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, pyqtSignal, QEvent, QSize
from PyQt6.QtGui import QFont, QColor, QBrush, QIcon, QGuiApplication, QCursor
import numpy as np
import re  # For regex pattern matching


def _dedupe_columns(cols):
    """Remove numeric suffixes and reapply them only where needed."""
    # Strip any trailing ``_<number>`` pattern(s)
    stripped = [re.sub(r"(_\d+)+$", "", c) for c in cols]

    counts = {}
    deduped = []
    for col in stripped:
        count = counts.get(col, 0)
        if count:
            deduped.append(f"{col}_{count}")
        else:
            deduped.append(col)
        counts[col] = count + 1

    return deduped

class EditableHeaderView(QHeaderView):
    """Custom header view that allows editing headers with double click"""
    headerDataChanged = pyqtSignal(int, Qt.Orientation, object)
    
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        self.sectionDoubleClicked.connect(self.editHeader)
    
    def editHeader(self, section):
        """Show dialog to edit the header text"""
        current_text = self.model().headerData(section, self.orientation())
        from PyQt6.QtWidgets import QInputDialog
        
        new_text, ok = QInputDialog.getText(
            self, 
            "Edit Header", 
            "Enter new header text:",
            text=current_text
        )
        
        if ok and new_text:
            # Emit signal to update the header data
            self.headerDataChanged.emit(section, self.orientation(), new_text)

class PandasTableModel(QAbstractTableModel):
    def __init__(self, data, dark_theme=False):
        super().__init__()
        self._data = data
        self.highlight_cols = set()
        self.highlight_rows = set()
        self._headers = list(data.columns)
        self.dark_theme = dark_theme

    def set_dark_theme(self, dark_theme: bool):
        """Update the theme flag and refresh the view."""
        self.dark_theme = dark_theme
        self.layoutChanged.emit()
        
    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]
        
    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]
        
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()
            
        row, col = index.row(), index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[row, col]
            
            # Format the value for display
            if pd.isna(value):
                return "NULL"
            elif isinstance(value, float):
                # Format floats to avoid scientific notation and limit decimal places
                return f"{value:.6f}".rstrip('0').rstrip('.')
            else:
                return str(value)
                
        elif role == Qt.ItemDataRole.BackgroundRole and self.dark_theme:
            # Highlight specific rows or columns
            if row in self.highlight_rows or col in self.highlight_cols:
                return QBrush(QColor(60, 90, 120))  # Darker blue highlight

            # Alternate row colors for readability
            if row % 2 == 0:
                return QBrush(QColor(45, 45, 45))  # Darker background
            else:
                return QBrush(QColor(51, 51, 51))  # Dark background for odd rows

        elif role == Qt.ItemDataRole.ForegroundRole and self.dark_theme:
            value = self._data.iloc[row, col]

            # Special color for NULL values
            if pd.isna(value):
                return QBrush(QColor(150, 150, 150))

            # Numeric values in a light blue color
            if isinstance(value, (int, float)) and not pd.isna(value):
                return QBrush(QColor(110, 200, 250))

            # Default text color for dark theme
            return QBrush(QColor(224, 224, 224))
                
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            value = self._data.iloc[row, col]
            if isinstance(value, (int, float)) and not pd.isna(value):
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            else:
                return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                
        return QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # Gracefully handle invalid section indices which can occur if
                # the view requests a header after the underlying model has
                # changed (e.g. when switching sheets). Returning an empty
                # string avoids an IndexError that would otherwise crash the
                # application.
                if 0 <= section < len(self._headers):
                    return str(self._headers[section])
                return ""
            else:
                return str(section + 1)  # 1-based row indexing
                
        elif role == Qt.ItemDataRole.FontRole:
            font = QFont()
            font.setBold(True)
            return font
            
        elif role == Qt.ItemDataRole.ForegroundRole and self.dark_theme:
            # Header text color for dark theme
            return QBrush(QColor(224, 224, 224))
            
        return QVariant()
    
    def setHeaderData(self, section, orientation, value, role=Qt.ItemDataRole.EditRole):
        """Set the header data when edited"""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.EditRole:
            if 0 <= section < len(self._headers):
                self._headers[section] = value
                # Also update the actual DataFrame column name
                self._data.columns = self._headers
                self.headerDataChanged.emit(orientation, section, section)
                return True
        return False
        
    def set_highlight_columns(self, columns):
        """Set which columns should be highlighted"""
        self.highlight_cols = set(columns)
        self.layoutChanged.emit()
        
    def set_highlight_rows(self, rows):
        """Set which rows should be highlighted"""
        self.highlight_rows = set(rows)
        self.layoutChanged.emit()


class ExcelViewer(QWidget):
    dataLoaded = pyqtSignal(pd.DataFrame, str)  # Signal emitted when data is loaded
    
    def __init__(self):
        super().__init__()
        self.df = None
        self.sheet_name = None
        self.filtered_df = None

        # Store widgets that may need theme specific styling
        self.toolbar = None

        # Track the current theme so the model can adjust colors
        self.current_theme = "light"
        
        # Default report configuration (SOO PreClose)
        self.report_config = {
            "header_rows": [5, 6],  # Rows 6 and 7 (0-indexed as 5 and 6)
            "skip_rows": 7,         # Skip rows 0-6 (header is at 5-6)
            "description": "SOO PreClose report with headers on rows 6 and 7"
        }
        # Current report type associated with the configuration
        self.report_type = None

        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        
        # Create toolbar area
        self.create_toolbar(main_layout)
        
        # Create table view
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        
        # Create custom header view that allows editing
        self.horizontal_header = EditableHeaderView(Qt.Orientation.Horizontal, self.table_view)
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontal_header.setStretchLastSection(True)
        self.horizontal_header.headerDataChanged.connect(self.on_header_changed)
        
        self.table_view.setHorizontalHeader(self.horizontal_header)
        
        # Clear table view stylesheet to inherit from application theme
        self.table_view.setStyleSheet("")
        
        # Add table to main layout
        main_layout.addWidget(self.table_view)
        
        # Add status area
        self.status_label = QLabel("No data loaded")
        main_layout.addWidget(self.status_label)
        
    def create_toolbar(self, main_layout):
        """Create toolbar with data manipulation options"""
        self.toolbar = QWidget()
        # Clear toolbar stylesheet so global theme can be applied
        self.toolbar.setStyleSheet("")
        
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 5)
        
        # Sheet operations
        operations_group = QGroupBox("Operations")
        operations_layout = QVBoxLayout(operations_group)  # Changed to vertical layout
        
        # Add sheet scope selection
        scope_layout = QHBoxLayout()
        scope_layout.addWidget(QLabel("Apply to:"))
        self.scope_selector = QComboBox()
        self.scope_selector.addItems(["Current Sheet", "All Sheets"])
        self.scope_selector.setToolTip("Choose whether to apply operations to the current sheet or all sheets")
        scope_layout.addWidget(self.scope_selector)
        operations_layout.addLayout(scope_layout)
        
        # Operations buttons in a grid layout (2 rows, 3 columns)
        buttons_layout = QHBoxLayout()
        
        # Clean button
        self.clean_button = QPushButton("Clean Data")
        header_rows_str = " and ".join([str(r+1) for r in self.report_config["header_rows"]])
        self.clean_button.setToolTip(
            f"Concatenate headers from rows {header_rows_str}, "
            f"remove rows above, remove blank rows and completely empty columns, "
            f"add sheet name column"
        )
        self.clean_button.clicked.connect(self.clean_data)
        
        # Export button
        self.export_button = QPushButton("Export")
        self.export_button.setToolTip("Export current dataframe to a file")
        self.export_button.clicked.connect(self.export_dataframe)
        
        # Rename columns button
        self.rename_columns_button = QPushButton("Import Headers")
        self.rename_columns_button.setToolTip("Import column headers from SQL query results")
        self.rename_columns_button.clicked.connect(self.import_column_headers)
        
        # Remove empty rows button
        self.remove_empty_rows_button = QPushButton("Remove Empty Rows")
        self.remove_empty_rows_button.setToolTip("Remove rows that have no data values (preserves first 2 columns)")
        self.remove_empty_rows_button.clicked.connect(self.remove_empty_data_rows)
        
        # Extract SQL button
        self.extract_sql_button = QPushButton("Extract SQL")
        self.extract_sql_button.setToolTip("Extract center codes and account numbers for SQL IN clauses")
        self.extract_sql_button.clicked.connect(self.extract_sql_codes)
        
        # Add buttons to layout
        buttons_layout.addWidget(self.clean_button)
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addWidget(self.rename_columns_button)
        buttons_layout.addWidget(self.remove_empty_rows_button)
        buttons_layout.addWidget(self.extract_sql_button)
        
        operations_layout.addLayout(buttons_layout)
        
        # Filter controls
        filter_group = QGroupBox("Filter")
        filter_layout = QHBoxLayout(filter_group)
        
        self.filter_column = QComboBox()
        self.filter_text = QLineEdit()
        self.filter_text.setPlaceholderText("Enter filter text...")
        self.filter_button = QPushButton("Apply Filter")
        self.filter_button.clicked.connect(self.apply_filter)
        self.clear_filter_button = QPushButton("Clear")
        self.clear_filter_button.clicked.connect(self.clear_filter)
        
        filter_layout.addWidget(QLabel("Column:"))
        filter_layout.addWidget(self.filter_column)
        filter_layout.addWidget(QLabel("Value:"))
        filter_layout.addWidget(self.filter_text)
        filter_layout.addWidget(self.filter_button)
        filter_layout.addWidget(self.clear_filter_button)
        
        # View controls
        view_group = QGroupBox("View Options")
        view_layout = QHBoxLayout(view_group)
        
        self.show_nulls = QCheckBox("Highlight NULLs")
        self.show_nulls.setChecked(True)
        self.show_nulls.stateChanged.connect(self.update_view)
        
        self.limit_rows = QSpinBox()
        self.limit_rows.setRange(0, 10000)
        self.limit_rows.setValue(1000)
        self.limit_rows.setSpecialValueText("All")
        self.limit_rows.valueChanged.connect(self.update_view)
        
        view_layout.addWidget(self.show_nulls)
        view_layout.addWidget(QLabel("Limit rows:"))
        view_layout.addWidget(self.limit_rows)
        
        # Add toolbar components to main layout
        toolbar_layout.addWidget(operations_group)
        toolbar_layout.addWidget(filter_group)
        toolbar_layout.addWidget(view_group)

        main_layout.addWidget(self.toolbar)
        
    def load_dataframe(self, df, sheet_name=None):
        """Load a dataframe into the viewer"""
        if df is None or df.empty:
            self.status_label.setText("No data loaded")
            # Disable all buttons when no data is loaded
            self.update_button_states(False) 
            return
            
        # Ensure all columns have valid names (handle unnamed columns)
        if df.columns.isnull().any() or df.columns.duplicated().any():
            new_cols = []
            for i, col in enumerate(df.columns):
                if pd.isna(col) or col == '':
                    new_cols.append(f"Column_{i+1}")
                else:
                    # If duplicate, append a number
                    if col in new_cols:
                        j = 1
                        while f"{col}_{j}" in new_cols:
                            j += 1
                        new_cols.append(f"{col}_{j}")
                    else:
                        new_cols.append(str(col))
            df.columns = new_cols
            
        self.df = df
        self.sheet_name = sheet_name
        self.filtered_df = df.copy()
        
        # Update column filter dropdown
        self.filter_column.clear()
        self.filter_column.addItems([str(col) for col in df.columns])
        
        # Create model and set it on table view
        self.model = PandasTableModel(
            self.filtered_df, self.current_theme.lower() == "dark")
        self.table_view.setModel(self.model)
        
        # Auto-resize columns to contents
        self.table_view.resizeColumnsToContents()
        
        # Update button states - enable all data manipulation buttons if data is loaded
        self.update_button_states(True)
        
        # Update clean button state based on whether the sheet is already cleaned
        already_cleaned = self.is_sheet_already_cleaned()
        self.clean_button.setEnabled(not already_cleaned)
        
        if already_cleaned:
            self.clean_button.setToolTip("Sheet has already been cleaned")
        else:
            header_rows_str = " and ".join([str(r+1) for r in self.report_config["header_rows"]])
            self.clean_button.setToolTip(
                f"Concatenate headers from rows {header_rows_str}, "
                f"remove rows above, remove blank rows and completely empty columns, "
                f"add sheet name column"
            )
        
        # Update status
        if sheet_name:
            rows, cols = df.shape
            self.status_label.setText(f"Sheet: {sheet_name} | {rows} rows, {cols} columns")
        else:
            rows, cols = df.shape
            self.status_label.setText(f"{rows} rows, {cols} columns")
            
        # Emit signal that data was loaded
        self.dataLoaded.emit(df, sheet_name if sheet_name else "")
        
        # Update view
        self.update_view()
        
    def update_button_states(self, has_data):
        """Update button states based on whether data is loaded"""
        # Export, Import Headers, and Remove Empty Data Rows should be enabled if data is present
        self.export_button.setEnabled(has_data)
        self.rename_columns_button.setEnabled(has_data)
        self.remove_empty_rows_button.setEnabled(has_data)
        
        # Filter buttons should be enabled if data is present
        self.filter_button.setEnabled(has_data)
        self.clear_filter_button.setEnabled(has_data)
        
        # Clean button and Extract SQL button should also be enabled if data is present
        self.clean_button.setEnabled(has_data)
        self.extract_sql_button.setEnabled(has_data)
        
    def apply_filter(self):
        """Apply filter to the dataframe"""
        if self.df is None or self.df.empty:
            return
            
        filter_col = self.filter_column.currentText()
        filter_text = self.filter_text.text().strip()
        
        if not filter_text:
            self.filtered_df = self.df.copy()
        else:
            # Try to convert filter text to numeric if the column is numeric
            if pd.api.types.is_numeric_dtype(self.df[filter_col]):
                try:
                    filter_value = float(filter_text)
                    self.filtered_df = self.df[self.df[filter_col] == filter_value]
                except ValueError:
                    # If not a valid number, use string-based filtering
                    self.filtered_df = self.df[self.df[filter_col].astype(str).str.contains(filter_text, case=False, na=False)]
            else:
                # String-based filtering
                self.filtered_df = self.df[self.df[filter_col].astype(str).str.contains(filter_text, case=False, na=False)]
                
        # Update model and view
        self.model = PandasTableModel(
            self.filtered_df, self.current_theme.lower() == "dark")
        self.table_view.setModel(self.model)
        
        # Update status
        rows = len(self.filtered_df)
        cols = len(self.filtered_df.columns)
        filter_info = f" (filtered by {filter_col}: '{filter_text}')" if filter_text else ""
        
        if self.sheet_name:
            self.status_label.setText(f"Sheet: {self.sheet_name} | {rows} rows, {cols} columns{filter_info}")
        else:
            self.status_label.setText(f"{rows} rows, {cols} columns{filter_info}")
            
        # Update view options
        self.update_view()
        
    def clear_filter(self):
        """Clear the current filter"""
        self.filter_text.clear()
        self.filtered_df = self.df.copy() if self.df is not None else None
        
        if self.filtered_df is not None:
            # Update model and view
            self.model = PandasTableModel(
                self.filtered_df, self.current_theme.lower() == "dark")
            self.table_view.setModel(self.model)
            
            # Update status
            rows, cols = self.filtered_df.shape
            if self.sheet_name:
                self.status_label.setText(f"Sheet: {self.sheet_name} | {rows} rows, {cols} columns")
            else:
                self.status_label.setText(f"{rows} rows, {cols} columns")
                
            # Update view options
            self.update_view()
            
    def update_view(self):
        """Update the view based on current settings"""
        if self.filtered_df is None or self.model is None:
            return
            
        # Apply row limit if set
        limit = self.limit_rows.value()
        if limit > 0 and limit < len(self.filtered_df):
            display_df = self.filtered_df.head(limit)
            self.model = PandasTableModel(
                display_df, self.current_theme.lower() == "dark")
            self.table_view.setModel(self.model)
            
        # Highlight NULL values if option is checked
        if self.show_nulls.isChecked():
            # Find columns with NULLs
            null_cols = []
            for i, col in enumerate(self.filtered_df.columns):
                if self.filtered_df[col].isna().any():
                    null_cols.append(i)
                    
            # Set highlights
            self.model.set_highlight_columns(null_cols)
            
        else:
            self.model.set_highlight_columns([])
            
        # Update layout
        self.model.layoutChanged.emit()
            
    def get_dataframe(self):
        """Get the current dataframe"""
        return self.df
        
    def get_filtered_dataframe(self):
        """Get the filtered dataframe"""
        return self.filtered_df
        
    def is_sheet_already_cleaned(self):
        """Check if the current sheet has already been cleaned"""
        if self.df is None or self.df.empty:
            return False
            
        # Check if sheet has already been cleaned by looking for these indicators:
        # 1. First column is named "Sheet_Name"
        # 2. Fewer than required rows to contain the original headers
        
        # Get the minimum number of rows needed based on the report configuration
        min_required_rows = max(self.report_config["header_rows"]) + 1
        
        if len(self.df) < min_required_rows:  # Not enough rows to contain the original headers
            return True
            
        # Check if the first column is "Sheet_Name"
        if "Sheet_Name" in self.df.columns and self.df.columns[0] == "Sheet_Name":
            return True
            
        return False
        
    def set_report_config(self, config, report_type=None):
        """Set the report configuration and associated report type."""
        self.report_config = config
        self.report_type = report_type
        
        # Update the clean button tooltip to reflect the new configuration
        if hasattr(self, 'clean_button'):
            header_rows_str = " and ".join([str(r+1) for r in self.report_config["header_rows"]])
            self.clean_button.setToolTip(
                f"Concatenate headers from rows {header_rows_str}, "
                f"remove rows above, remove blank rows and completely empty columns, "
                f"add sheet name column"
            )
            
        print(f"ExcelViewer: Set report config to {config}")
        
    def clean_data(self):
        """Clean data based on selected scope - current sheet or all sheets"""
        # Check if applying to current sheet or all sheets
        if self.scope_selector.currentText() == "Current Sheet":
            self.clean_sheet()
        else:
            self.clean_all_sheets()
    
    def export_dataframe(self):
        """Export the current dataframe to a file"""
        if self.df is None or self.df.empty:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Data", "There is no data to export.")
            return
        
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Dataframe", "", 
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # Export according to chosen format
            if file_path.lower().endswith('.csv'):
                self.df.to_csv(file_path, index=False)
            elif file_path.lower().endswith('.xlsx'):
                self.df.to_excel(file_path, index=False)
            elif file_path.lower().endswith('.json'):
                self.df.to_json(file_path, orient='records')
            else:
                # Default to CSV if no extension recognized
                if not any(file_path.lower().endswith(ext) for ext in ['.csv', '.xlsx', '.json']):
                    file_path += '.csv'
                self.df.to_csv(file_path, index=False)
            
            QMessageBox.information(self, "Export Successful", f"Data exported to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")

    def on_header_changed(self, section, orientation, value):
        """Handle header change events from the EditableHeaderView"""
        if self.model and orientation == Qt.Orientation.Horizontal:
            # Update the model with the new header value
            self.model.setHeaderData(section, orientation, value)
            
            # Update the dataframe columns
            if self.df is not None and section < len(self.df.columns):
                # Store the current columns
                cols = list(self.df.columns)
                # Update the column at the specific section
                cols[section] = value
                # Apply the updated columns to both dataframes
                self.df.columns = cols
                self.filtered_df.columns = cols
                
                # Update filter dropdown
                current_text = self.filter_column.currentText()
                self.filter_column.clear()
                self.filter_column.addItems([str(col) for col in self.df.columns])
                
                # Try to restore the previous selection
                index = self.filter_column.findText(current_text)
                if index >= 0:
                    self.filter_column.setCurrentIndex(index)

    def import_column_headers(self):
        """Import column headers based on the selected scope - current sheet or all sheets"""
        # Check if applying to current sheet or all sheets
        if self.scope_selector.currentText() == "Current Sheet":
            self._import_column_headers_to_sheet()
        else:
            self._import_column_headers_to_all_sheets()
    
    def _import_column_headers_to_sheet(self):
        """Import column headers from SQL query results to the current sheet"""
        if self.df is None or self.df.empty:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Data", "Please load an Excel sheet first.")
            return
            
        # Request SQL column headers from the parent window
        from src.ui.main_window import MainWindow
        parent = self.window()
        if parent and isinstance(parent, MainWindow) and hasattr(parent, 'results_viewer'):
            sql_df = parent.results_viewer.get_dataframe()
            if sql_df is None or sql_df.empty:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "No SQL Data", "Please run a SQL query first to get column headers.")
                return
                
            # Get SQL column names
            sql_columns = list(sql_df.columns)
            
            # Create a mapping dialog to let the user map SQL columns to Excel columns
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QHBoxLayout, QLabel
            mapping_dialog = QDialog(self)
            mapping_dialog.setWindowTitle("Map SQL Columns to Excel Columns")
            mapping_dialog.setMinimumWidth(500)
            
            layout = QVBoxLayout(mapping_dialog)
            layout.addWidget(QLabel("Select SQL columns to import as headers:"))
            
            # Create a list widget to show SQL columns
            column_list = QListWidget()
            for col in sql_columns:
                column_list.addItem(str(col))
            column_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
            layout.addWidget(column_list)
            
            # Add instruction
            layout.addWidget(QLabel("Select how to apply headers:"))
            
            # Create buttons
            button_layout = QHBoxLayout()
            apply_all_button = QPushButton("Apply All")
            apply_selected_button = QPushButton("Apply Selected")
            cancel_button = QPushButton("Cancel")
            
            button_layout.addWidget(apply_all_button)
            button_layout.addWidget(apply_selected_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            # Connect button actions
            apply_all_button.clicked.connect(lambda: self._apply_sql_headers(sql_columns, mapping_dialog))
            apply_selected_button.clicked.connect(lambda: self._apply_sql_headers(
                [str(column_list.item(idx).text()) for idx in range(column_list.count()) 
                 if column_list.item(idx).isSelected()],
                mapping_dialog
            ))
            cancel_button.clicked.connect(mapping_dialog.reject)
            
            # Select all items by default
            for i in range(column_list.count()):
                column_list.item(i).setSelected(True)
            
            # Show dialog
            mapping_dialog.exec()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Cannot Access SQL Results",
                                "Unable to access SQL query results. Please run a SQL query first.")

    def _apply_sql_headers(self, selected_columns, dialog=None):
        """Apply SQL column headers to the current sheet."""
        if self.df is None or self.df.empty:
            return

        try:
            new_columns = list(self.df.columns)

            # Skip the Sheet_Name column if present
            start_idx = 1 if new_columns and new_columns[0] == "Sheet_Name" else 0

            for i, col_name in enumerate(selected_columns):
                if i + start_idx < len(new_columns):
                    new_columns[i + start_idx] = col_name

            # Ensure uniqueness of column names
            new_columns = _dedupe_columns(new_columns)

            # Apply updated columns to both dataframes
            self.df.columns = new_columns
            self.filtered_df.columns = new_columns

            # Propagate updated columns back to the analyzer if possible
            from src.ui.main_window import MainWindow
            parent = self.window()
            if (
                parent
                and isinstance(parent, MainWindow)
                and hasattr(parent, "excel_analyzer")
                and self.sheet_name
                and self.sheet_name in parent.excel_analyzer.sheet_data
            ):
                analyzer_df = parent.excel_analyzer.sheet_data[self.sheet_name][
                    "dataframe"
                ]
                # Copy to avoid accidental sharing of stale references
                updated_df = analyzer_df.copy()
                updated_df.columns = new_columns
                parent.excel_analyzer.sheet_data[self.sheet_name][
                    "dataframe"
                ] = updated_df

            # Update filter dropdown preserving selection
            current_text = self.filter_column.currentText()
            self.filter_column.clear()
            self.filter_column.addItems([str(col) for col in self.df.columns])
            index = self.filter_column.findText(current_text)
            if index >= 0:
                self.filter_column.setCurrentIndex(index)

            # Refresh model and view
            self.model = PandasTableModel(
                self.filtered_df, self.current_theme.lower() == "dark"
            )
            self.table_view.setModel(self.model)
            self.table_view.resizeColumnsToContents()
            self.update_view()

            if dialog is not None:
                dialog.accept()

        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.critical(
                self,
                "Error Applying Headers",
                f"An error occurred while applying headers: {str(e)}",
            )
    
    def _import_column_headers_to_all_sheets(self):
        """Import column headers from SQL query results to all sheets"""
        # Confirm before proceeding
        from PyQt6.QtWidgets import QMessageBox
        response = QMessageBox.question(
            self,
            "Import Headers to All Sheets",
            "This will apply SQL column headers to ALL sheets in the workbook. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if response != QMessageBox.StandardButton.Yes:
            return
        
        # Request SQL column headers from the parent window
        from src.ui.main_window import MainWindow
        parent = self.window()
        if not parent or not isinstance(parent, MainWindow):
            QMessageBox.warning(self, "Error", "Could not access the main application.")
            return
            
        if not hasattr(parent, 'results_viewer') or not hasattr(parent, 'excel_analyzer'):
            QMessageBox.warning(self, "Error", "Could not access the SQL results or Excel analyzer.")
            return
        
        # Get SQL column names
        sql_df = parent.results_viewer.get_dataframe()
        if sql_df is None or sql_df.empty:
            QMessageBox.warning(self, "No SQL Data", "Please run a SQL query first to get column headers.")
            return
            
        sql_columns = list(sql_df.columns)
        
        # Get the Excel analyzer and sheet names
        excel_analyzer = parent.excel_analyzer
        sheet_names = excel_analyzer.sheet_names
        
        if not sheet_names:
            QMessageBox.warning(self, "No Sheets", "No Excel sheets are available.")
            return
        
        # Create a mapping dialog to let the user map SQL columns to Excel columns
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QHBoxLayout, QLabel
        from PyQt6.QtWidgets import QRadioButton, QButtonGroup
        
        # First, select which columns to import
        column_selection_dialog = QDialog(self)
        column_selection_dialog.setWindowTitle("Select SQL Columns to Import")
        column_selection_dialog.setMinimumWidth(500)
        
        cs_layout = QVBoxLayout(column_selection_dialog)
        cs_layout.addWidget(QLabel("Select SQL columns to import as headers to all sheets:"))
        
        # Create a list widget to show SQL columns
        column_list = QListWidget()
        for col in sql_columns:
            column_list.addItem(str(col))
        column_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        cs_layout.addWidget(column_list)
        
        # Add buttons
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Next")
        cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        cs_layout.addLayout(button_layout)
        
        # Connect button actions
        selected_columns = []
        
        def on_apply():
            nonlocal selected_columns
            selected_columns = [str(column_list.item(idx).text()) for idx in range(column_list.count()) 
                                if column_list.item(idx).isSelected()]
            if not selected_columns:
                QMessageBox.warning(column_selection_dialog, "No Columns Selected", "Please select at least one column.")
                return
            column_selection_dialog.accept()
            
        apply_button.clicked.connect(on_apply)
        cancel_button.clicked.connect(column_selection_dialog.reject)
        
        # Select all items by default
        for i in range(column_list.count()):
            column_list.item(i).setSelected(True)
        
        # Show dialog and continue if accepted
        if column_selection_dialog.exec() != QDialog.DialogCode.Accepted or not selected_columns:
            return
            
        # Now, choose the mapping method
        mapping_dialog = QDialog(self)
        mapping_dialog.setWindowTitle("Header Mapping Method")
        mapping_dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(mapping_dialog)
        layout.addWidget(QLabel("How would you like to apply the SQL headers to all sheets?"))
        
        # Create radio button options
        btn_group = QButtonGroup(mapping_dialog)
        
        # Option 1: Simple positional mapping
        position_btn = QRadioButton("Map by position (SQL column 1 → Excel column 1, etc.)")
        position_btn.setChecked(True)  # Default option
        btn_group.addButton(position_btn, 1)
        layout.addWidget(position_btn)
        
        # Option 2: Preserve Sheet_Name if it exists
        preserve_btn = QRadioButton("Preserve Sheet_Name column if present (SQL column 1 → Excel column 2, etc.)")
        btn_group.addButton(preserve_btn, 2)
        layout.addWidget(preserve_btn)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(mapping_dialog.accept)
        button_box.rejected.connect(mapping_dialog.reject)
        layout.addWidget(button_box)
        
        # Show dialog and get mapping method
        if mapping_dialog.exec() != QDialog.DialogCode.Accepted:
            return
            
        mapping_method = btn_group.checkedId()
            
        # Now process all sheets with the selected columns and mapping method
        processed_sheets = []
        skipped_sheets = []
        
        # Remember the current sheet name
        current_sheet_name = self.sheet_name
        
        # Progress dialog
        from PyQt6.QtWidgets import QProgressDialog
        progress = QProgressDialog("Importing headers...", "Cancel", 0, len(sheet_names), self)
        progress.setWindowTitle("Import Headers to All Sheets")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)  # Show immediately
        
        try:
            # Process each sheet
            for i, sheet_name in enumerate(sheet_names):
                if progress.wasCanceled():
                    break
                    
                progress.setValue(i)
                progress.setLabelText(f"Processing sheet: {sheet_name}")
                
                # Load the sheet if not already analyzed
                if sheet_name not in excel_analyzer.sheet_data:
                    excel_analyzer.analyze_sheet(sheet_name)
                    
                # Get the dataframe for this sheet
                df = excel_analyzer.sheet_data[sheet_name]["dataframe"]
                
                if df is None or df.empty:
                    skipped_sheets.append(f"{sheet_name} (empty)")
                    continue
                
                # Apply column headers based on the selected mapping method
                new_columns = list(df.columns)
                
                if mapping_method == 1:  # Position mapping
                    # Simple position mapping
                    for i, sql_col in enumerate(selected_columns):
                        if i < len(new_columns):
                            new_columns[i] = sql_col
                else:  # Preserve Sheet_Name
                    # Skip Sheet_Name column if it exists
                    has_sheet_name = "Sheet_Name" in new_columns and new_columns[0] == "Sheet_Name"
                    
                    if has_sheet_name:
                        # Skip first column
                        for i, sql_col in enumerate(selected_columns):
                            if i + 1 < len(new_columns):  # +1 to skip Sheet_Name
                                new_columns[i + 1] = sql_col
                    else:
                        # No Sheet_Name column, apply normally
                        for i, sql_col in enumerate(selected_columns):
                            if i < len(new_columns):
                                new_columns[i] = sql_col
                
                # Update column names
                df.columns = new_columns
                
                # Update the dataframe in the analyzer
                excel_analyzer.sheet_data[sheet_name]["dataframe"] = df
                processed_sheets.append(sheet_name)
            
            # Complete progress
            progress.setValue(len(sheet_names))
            
            # If the current sheet was processed, reload it in the viewer
            if current_sheet_name in processed_sheets:
                df = excel_analyzer.sheet_data[current_sheet_name]["dataframe"]
                self.load_dataframe(df, current_sheet_name)
                
            # Show summary message
            summary_message = f"Headers imported to {len(processed_sheets)} sheets:\n"
            if processed_sheets:
                summary_message += f"({', '.join(processed_sheets[:5])}{'...' if len(processed_sheets) > 5 else ''})\n\n"
                
            if skipped_sheets:
                summary_message += f"Skipped {len(skipped_sheets)} sheets:\n"
                summary_message += f"({', '.join(skipped_sheets[:5])}{'...' if len(skipped_sheets) > 5 else ''})"
                
            QMessageBox.information(self, "Import Headers Completed", summary_message)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        finally:
            progress.close()

    def _base_clean_dataframe(self, df, sheet_name):
        """Base implementation for cleaning a dataframe."""
        try:
            # Get the header rows based on the report configuration
            header_row_indices = self.report_config["header_rows"]
            skip_rows = self.report_config["skip_rows"]

            # Make sure we have enough rows
            if len(df) <= max(header_row_indices):
                print(f"Sheet {sheet_name} doesn't have enough rows for cleaning")
                return None

            # Get header rows from the configuration
            header_rows = []
            for idx in header_row_indices:
                row = df.iloc[idx].copy()
                # Excel exports often use merged cells for headings. When these
                # are read via ``pandas.read_excel`` the value only appears in
                # the top-left cell of the merge while the remaining cells are
                # ``NaN``.  Forward filling ensures that each column inherits the
                # merged value so the header does not look empty in later
                # processing.
                row = row.ffill()
                header_rows.append(row)

            # Check if there are any non-empty values in the header rows
            header_has_values = []
            for row in header_rows:
                has_values = sum(1 for x in row if pd.notna(x) and str(x).strip()) > 0
                header_has_values.append(has_values)

            # Create a copy of the data portion of the dataframe (after headers)
            data_df = df.iloc[skip_rows:].copy()

            # Detect completely empty columns in the DATA ONLY
            empty_cols = []
            for i in range(data_df.shape[1]):
                col_data = data_df.iloc[:, i]
                is_empty = col_data.isna().all() or (col_data.astype(str).str.strip() == '').all()
                if self.report_type == "Corp SOO":
                    numeric_series = pd.to_numeric(col_data, errors="coerce")
                    if numeric_series.notna().any():
                        is_empty = is_empty or numeric_series.fillna(0).eq(0).all()
                if is_empty:
                    empty_cols.append(i)

            # Create a list of columns to keep
            columns_to_keep = [i for i in range(data_df.shape[1]) if i not in empty_cols]

            # Concatenate headers, handling NaN values
            new_headers = []
            for i in columns_to_keep:
                header_values = []
                for idx, header_row in enumerate(header_rows):
                    if i < len(header_row):
                        value = header_row.iloc[i]
                        if not pd.isna(value) and str(value).strip():
                            header_values.append(str(value).strip())

                # Join all non-empty header values or use a default column name
                if header_values:
                    new_header = " ".join(header_values)
                else:
                    new_header = f"Column_{i+1}"

                # Replace any newlines or excessive whitespace
                new_header = new_header.replace('\n', ' ').replace('\r', ' ')
                new_header = ' '.join(new_header.split())

                new_headers.append(new_header)

            # Create a new dataframe with only non-empty columns
            clean_df = data_df.iloc[:, columns_to_keep].copy()

            # Set the new headers
            if len(new_headers) == len(clean_df.columns):
                clean_df.columns = new_headers
            else:
                # If there's a mismatch, just create default headers
                clean_df.columns = [f"Column_{i+1}" for i in range(len(clean_df.columns))]
                print(
                    f"Warning: Header count mismatch for {sheet_name}: {len(new_headers)} headers for {len(clean_df.columns)} columns"
                )

            # Ensure column names are unique to avoid pandas returning DataFrame slices
            # when referencing by name which can break numeric conversion
            seen = {}
            unique_cols = []
            for col in clean_df.columns:
                if col in seen:
                    seen[col] += 1
                    new_col = f"{col}_{seen[col]}"
                    while new_col in seen:
                        seen[new_col] = seen.get(new_col, 0) + 1
                        new_col = f"{new_col}_{seen[new_col]}"
                    unique_cols.append(new_col)
                    seen[new_col] = 0
                else:
                    seen[col] = 0
                    unique_cols.append(col)
            clean_df.columns = unique_cols

            # Remove blank rows
            if self.report_type == "Corp SOO":
                data_part = clean_df.iloc[:, 1:]

                numeric_part = data_part.apply(pd.to_numeric, errors="coerce")

                blank_mask = data_part.isna() | (
                    data_part.astype(str).apply(lambda x: x.str.strip() == "")
                )
                numeric_zero_mask = (numeric_part == 0) & numeric_part.notna()

                first_col = clean_df.iloc[:, 0]
                first_col_blank = first_col.isna() | (
                    first_col.astype(str).str.strip() == ""
                )

                all_numeric_blank = blank_mask.all(axis=1)
                all_numeric_blank_or_zero = (blank_mask | numeric_zero_mask).all(
                    axis=1
                )

                remove_rows = (first_col_blank & all_numeric_blank_or_zero) | (
                    (~first_col_blank) & all_numeric_blank
                )
                clean_df = clean_df.loc[~remove_rows]
            else:
                clean_df = clean_df.loc[~((clean_df.isna().all(axis=1)) |
                                    (clean_df.astype(str).apply(lambda x: x.str.strip() == '').all(axis=1)))]

            # Convert all columns to numeric starting from first_data_column
            first_col = self.report_config.get("first_data_column", 2)
            for idx in range(first_col, len(clean_df.columns)):
                col_name = clean_df.columns[idx]
                clean_df.iloc[:, idx] = pd.to_numeric(
                    clean_df.iloc[:, idx], errors="coerce"
                ).round(2)

            # Add a new column with the sheet name at the beginning. Most
            # reports use ``Sheet_Name`` but AR Center now relies on a ``Sheet``
            # column for comparisons.
            if self.report_type not in ("SOO MFR", "Corp SOO"):
                col_name = "Sheet_Name"
                if self.report_type == "AR Center":
                    col_name = "Sheet"
                clean_df.insert(0, col_name, sheet_name)

            return clean_df

        except Exception as e:
            print(f"Error cleaning sheet {sheet_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def remove_empty_data_rows(self):
        """Remove empty data rows based on the selected scope - current sheet or all sheets"""
        # Check if applying to current sheet or all sheets
        if self.scope_selector.currentText() == "Current Sheet":
            self._remove_empty_data_rows_from_sheet()
        else:
            self._remove_empty_data_rows_from_all_sheets()
    
    def _remove_empty_data_rows_from_sheet(self):
        """Remove rows where all data columns (column 3 and onwards) contain only NULL values in current sheet."""
        if self.df is None or self.df.empty:
            return
        
        try:
            # Consider only data columns starting at configured index
            first_col = self.report_config.get("first_data_column", 2)
            data_columns = self.df.columns[first_col:]
            if len(data_columns) == 0:
                # No data columns to check
                return
                
            # Find rows where all data columns are NULL/NaN or empty string
            empty_condition = self.df[data_columns].isna().all(axis=1) | (self.df[data_columns] == '').all(axis=1)
            rows_to_keep = ~empty_condition
            
            # Only proceed if we found some rows to remove
            if not all(rows_to_keep):
                # Count rows that will be removed
                rows_to_remove = (~rows_to_keep).sum()
                
                # Confirmation dialog
                from PyQt6.QtWidgets import QMessageBox
                result = QMessageBox.question(
                    self,
                    "Remove Empty Rows",
                    f"This will remove {rows_to_remove} rows where all data columns contain only NULL values. Continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if result == QMessageBox.StandardButton.Yes:
                    # Keep only non-empty rows
                    self.df = self.df[rows_to_keep].reset_index(drop=True)
                    self.filtered_df = self.df.copy()
                    
                    # Update the model
                    self.model = PandasTableModel(
                        self.filtered_df, self.current_theme.lower() == "dark")
                    self.table_view.setModel(self.model)
                    
                    # Update status
                    rows, cols = self.df.shape
                    if self.sheet_name:
                        self.status_label.setText(f"Sheet: {self.sheet_name} | {rows} rows, {cols} columns | Removed {rows_to_remove} empty rows")
                    else:
                        self.status_label.setText(f"{rows} rows, {cols} columns | Removed {rows_to_remove} empty rows")
                        
                    # Update view
                    self.update_view()
            else:
                # No empty rows found
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self, 
                    "No Empty Rows", 
                    "No rows with all NULL data columns were found."
                )
                
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self, 
                "Error Removing Empty Rows", 
                f"An error occurred: {str(e)}"
            )
    
    def _remove_empty_data_rows_from_all_sheets(self):
        """Remove empty data rows from all sheets in the workbook"""
        # Confirm before proceeding
        from PyQt6.QtWidgets import QMessageBox
        response = QMessageBox.question(
            self,
            "Remove Empty Rows from All Sheets",
            "This will remove empty data rows from ALL sheets in the workbook. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if response != QMessageBox.StandardButton.Yes:
            return
            
        # Get the parent window to access Excel analyzer
        from src.ui.main_window import MainWindow
        parent = self.window()
        if not parent or not isinstance(parent, MainWindow) or not hasattr(parent, 'excel_analyzer'):
            QMessageBox.warning(self, "Error", "Could not access the main application or Excel analyzer.")
            return
            
        # Get the Excel analyzer and sheet names
        excel_analyzer = parent.excel_analyzer
        sheet_names = excel_analyzer.sheet_names
        
        if not sheet_names:
            QMessageBox.warning(self, "No Sheets", "No Excel sheets are available.")
            return
            
        # Track results
        processed_sheets = []
        skipped_sheets = []
        rows_removed_count = 0
        
        # Remember the current sheet name
        current_sheet_name = self.sheet_name
        
        # Progress dialog
        from PyQt6.QtWidgets import QProgressDialog
        progress = QProgressDialog("Removing empty rows...", "Cancel", 0, len(sheet_names), self)
        progress.setWindowTitle("Process All Sheets")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)  # Show immediately
        
        try:
            # Process each sheet
            for i, sheet_name in enumerate(sheet_names):
                if progress.wasCanceled():
                    break
                    
                progress.setValue(i)
                progress.setLabelText(f"Processing sheet: {sheet_name}")
                
                # Load the sheet if not already analyzed
                if sheet_name not in excel_analyzer.sheet_data:
                    excel_analyzer.analyze_sheet(sheet_name)
                    
                # Get the dataframe for this sheet
                df = excel_analyzer.sheet_data[sheet_name]["dataframe"]
                
                if df is None or df.empty:
                    skipped_sheets.append(f"{sheet_name} (empty)")
                    continue
                    
                # Skip if sheet doesn't have enough data columns
                if df.shape[1] <= 2:
                    skipped_sheets.append(f"{sheet_name} (not enough columns)")
                    continue
                
                # Consider only data columns starting at configured index
                first_col = self.report_config.get("first_data_column", 2)
                data_columns = df.columns[first_col:]
                
                # Find rows where all data columns are NULL/NaN or empty string
                empty_condition = df[data_columns].isna().all(axis=1) | (df[data_columns] == '').all(axis=1)
                rows_to_keep = ~empty_condition
                
                # Skip if no empty rows found
                if all(rows_to_keep):
                    processed_sheets.append(f"{sheet_name} (no empty rows)")
                    continue
                
                # Count rows that will be removed
                rows_to_remove = (~rows_to_keep).sum()
                
                # Keep only non-empty rows and update the sheet data
                cleaned_df = df[rows_to_keep].reset_index(drop=True)
                excel_analyzer.sheet_data[sheet_name]["dataframe"] = cleaned_df
                
                processed_sheets.append(sheet_name)
                rows_removed_count += rows_to_remove
            
            # Complete progress
            progress.setValue(len(sheet_names))
            
            # If the current sheet was processed, reload it in the viewer
            if current_sheet_name in [s.split(" ")[0] for s in processed_sheets]:
                df = excel_analyzer.sheet_data[current_sheet_name]["dataframe"]
                self.load_dataframe(df, current_sheet_name)
                
            # Show summary message
            if rows_removed_count > 0:
                summary_message = f"Empty rows removal completed:\n\n"
                summary_message += f"- Removed {rows_removed_count} empty rows across {len(processed_sheets)} sheets\n"
                
                if skipped_sheets:
                    summary_message += f"\nSkipped {len(skipped_sheets)} sheets:\n"
                    summary_message += f"({', '.join(skipped_sheets[:5])}{'...' if len(skipped_sheets) > 5 else ''})\n"
                    
                QMessageBox.information(self, "Process Completed", summary_message)
            else:
                QMessageBox.information(self, "Process Completed", 
                    "No empty rows found in any sheet.")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        finally:
            progress.close()
    
    def extract_sql_codes(self):
        """Extract center codes from sheet names and account codes from a selected column to generate SQL IN clauses"""
        if self.df is None or not self.sheet_name:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Data", "Please load an Excel sheet first.")
            return
        
        try:
            # Step 1: Get parent window to access all sheet names
            from src.ui.main_window import MainWindow
            parent = self.window()
            if not parent or not isinstance(parent, MainWindow):
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", "Could not access the main application window.")
                return
            
            # Step 2: Get all available sheet names from the parent window
            available_sheets = []
            if hasattr(parent, 'sheet_selector'):
                for i in range(parent.sheet_selector.count()):
                    available_sheets.append(parent.sheet_selector.itemText(i))
                    
            if not available_sheets:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "No Sheets", "No Excel sheets are available.")
                return
                
            # Step 3: Let user select which sheets to analyze
            selected_sheets = self.select_sheets_dialog(available_sheets)
            if not selected_sheets:
                return  # User cancelled
                
            # Step 4: Extract center codes from selected sheet names
            # Support multiple center code formats
            center_patterns = [
                r'^(\d{4}-\d{3})',  # Standard format (e.g., "1234-567")
                r'^(\d{4}-\d{2})',   # Alternative format (e.g., "1234-56")
                r'^(\d{4}-\d{1})',   # Short format (e.g., "1234-5")
                r'^(\d{3}-\d{3})'    # Another possible format (e.g., "123-456")
            ]
            center_codes = set()
            
            for sheet in selected_sheets:
                for pattern in center_patterns:
                    match = re.match(pattern, sheet)
                    if match:
                        center_codes.add(match.group(1))
                        break  # Stop checking patterns once a match is found
            
            # Step 5: Ask user to select a column to extract account codes from
            column_names = list(self.df.columns)
            from PyQt6.QtWidgets import QInputDialog
            selected_column, ok = QInputDialog.getItem(
                self, 
                "Select Column", 
                "Select column containing account numbers:",
                column_names,
                0,
                False
            )
            
            if not ok or not selected_column:
                return
            
            # Step 6: Extract account codes from the selected column across all selected sheets
            from src.utils.account_patterns import ACCOUNT_PATTERNS
            account_patterns = ACCOUNT_PATTERNS
            account_codes = set()
            missing_column_sheets = []

            is_name_column = selected_column.strip().lower() in (
                "careportname",
                "ca report name",
                "ca reportname",
            )
            if not is_name_column and self.report_type in ("SOO MFR", "MFR PreClose", "Corp SOO"):
                if self.df.columns.get_loc(selected_column) == 0:
                    # CAReportName becomes column A after cleaning
                    is_name_column = True
            
            # First get account codes from the current sheet
            if self.df is not None and selected_column in self.df.columns:
                column_data = self.df[selected_column].astype(str)
                if is_name_column:
                    for value in column_data:
                        val = value.strip()
                        if val:
                            account_codes.add(val)
                else:
                    for value in column_data:
                        for pattern in account_patterns:
                            matches = re.findall(pattern, value)
                            for match in matches:
                                account_codes.add(match)
            else:
                missing_column_sheets.append(self.sheet_name)
            
            # If there are other sheets to analyze, get data from them too
            if len(selected_sheets) > 1 and hasattr(parent, 'excel_analyzer'):
                excel_analyzer = parent.excel_analyzer
                
                for sheet_name in selected_sheets:
                    # Skip the current sheet as we've already processed it
                    if sheet_name == self.sheet_name:
                        continue
                        
                    try:
                        # Analyze sheet if not already analyzed
                        if sheet_name not in excel_analyzer.sheet_data:
                            excel_analyzer.analyze_sheet(sheet_name)
                            
                        # Get dataframe for this sheet
                        sheet_df = excel_analyzer.sheet_data[sheet_name]["dataframe"]
                        
                        # Check if the selected column exists in this sheet
                        if selected_column in sheet_df.columns:
                            column_data = sheet_df[selected_column].astype(str)
                            if is_name_column:
                                for value in column_data:
                                    val = value.strip()
                                    if val:
                                        account_codes.add(val)
                            else:
                                for value in column_data:
                                    for pattern in account_patterns:
                                        matches = re.findall(pattern, value)
                                        for match in matches:
                                            account_codes.add(match)
                        else:
                            missing_column_sheets.append(sheet_name)
                    except Exception as e:
                        print(f"Error processing sheet {sheet_name}: {str(e)}")
                        missing_column_sheets.append(sheet_name)
            
            # Step 7: Generate SQL IN clauses and display
            if not center_codes and not account_codes:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "No Codes Found", 
                    "No center or account codes were found in the selected sheets and column.")
                return
                
            center_sql = "IN (" + ", ".join([f"'{code}'" for code in sorted(center_codes)]) + ")"
            account_sql = "IN (" + ", ".join([f"'{code}'" for code in sorted(account_codes)]) + ")"
            
            # Create and show the result dialog
            self.show_extracted_sql(center_sql, account_sql, center_codes, 
                               account_codes, selected_sheets, missing_column_sheets)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            
    def select_sheets_dialog(self, available_sheets):
        """Show a dialog to select multiple sheets to analyze"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Sheets")
        dialog.setMinimumSize(400, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Add select all button
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(lambda: self._select_all_sheets(sheet_list))
        layout.addWidget(select_all_btn)
        
        # Create list widget
        sheet_list = QListWidget()
        sheet_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        
        for sheet in available_sheets:
            item = QListWidgetItem(sheet)
            sheet_list.addItem(item)
            
        layout.addWidget(sheet_list)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Show dialog and return selected sheets if accepted
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return [item.text() for item in sheet_list.selectedItems()]
        else:
            return []
            
    def _select_all_sheets(self, list_widget):
        """Select all items in the list widget"""
        for i in range(list_widget.count()):
            list_widget.item(i).setSelected(True)
    
    def show_extracted_sql(self, center_sql, account_sql, center_codes, 
                           account_codes, analyzed_sheets=None, missing_column_sheets=None):
        """Show the extracted SQL IN clauses in a dialog"""
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("SQL IN Clauses")
        dialog.setMinimumSize(600, 500)
        
        # Use application theme for styling
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Create summary labels
        sheets_info = f"Analyzed {len(analyzed_sheets)} sheet(s): {', '.join(analyzed_sheets) if analyzed_sheets else 'Current sheet'}"
        layout.addWidget(QLabel(sheets_info))
        
        # Display warning if some sheets didn't have the selected column
        if missing_column_sheets and len(missing_column_sheets) > 0:
            warning_label = QLabel(f"Warning: The following sheets did not have the selected column: {', '.join(missing_column_sheets)}")
            warning_label.setStyleSheet("color: #ffaa00;")
            warning_label.setWordWrap(True)
            layout.addWidget(warning_label)
        
        # Add center and account count summary
        summary = QLabel(f"Found {len(center_codes)} center codes and {len(account_codes)} account codes")
        layout.addWidget(summary)
        
        # Create center SQL display
        layout.addWidget(QLabel("Centers SQL IN Clause:"))
        center_text = QTextEdit()
        center_text.setPlainText(center_sql)
        center_text.setReadOnly(True)
        layout.addWidget(center_text)


        # Center list label removed per user request to avoid duplicate display

        # Create account SQL display with list of extracted accounts
        layout.addWidget(QLabel("Accounts SQL IN Clause:"))
        account_text = QTextEdit()
        account_text.setPlainText(account_sql)
        account_text.setReadOnly(True)
        layout.addWidget(account_text)

        if account_codes:
            # Add sign flip section
            sign_flip_group = QGroupBox("Sign Flip Selection")
            sign_flip_layout = QVBoxLayout(sign_flip_group)
            
            # Add explanation
            explanation = QLabel("Select accounts that should have their signs flipped during comparison (negative numbers become positive, positive numbers become negative):")
            explanation.setWordWrap(True)
            sign_flip_layout.addWidget(explanation)
            
            # Create list widget for account selection
            account_list = QListWidget()
            account_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
            for account in sorted(account_codes):
                item = QListWidgetItem(account)
                account_list.addItem(item)
            
            sign_flip_layout.addWidget(account_list)
            
            # Add Select All button
            select_all_btn = QPushButton("Select All")
            select_all_btn.clicked.connect(lambda: self._select_all_accounts(account_list))
            sign_flip_layout.addWidget(select_all_btn)
            
            layout.addWidget(sign_flip_group)

            # Accounts list label removed per user request to avoid duplicate display
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        
        # Add custom copy buttons
        copy_centers_btn = QPushButton("Copy Centers")
        copy_centers_btn.setIcon(QIcon.fromTheme("edit-copy"))
        copy_centers_btn.clicked.connect(lambda: self.copy_to_clipboard(center_sql))
        
        copy_accounts_btn = QPushButton("Copy Accounts")
        copy_accounts_btn.setIcon(QIcon.fromTheme("edit-copy"))
        copy_accounts_btn.clicked.connect(lambda: self.copy_to_clipboard(account_sql))
        
        # Add Insert SQL button
        insert_sql_btn = QPushButton("Insert SQL")
        insert_sql_btn.setIcon(QIcon.fromTheme("edit-paste"))
        insert_sql_btn.clicked.connect(lambda: self.insert_sql_to_editor(center_sql, account_sql, 
                                                                       [item.text() for item in account_list.selectedItems()]))
        
        button_box.addButton(copy_centers_btn, QDialogButtonBox.ButtonRole.ActionRole)
        button_box.addButton(copy_accounts_btn, QDialogButtonBox.ButtonRole.ActionRole)
        button_box.addButton(insert_sql_btn, QDialogButtonBox.ButtonRole.ActionRole)
        
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # Show dialog
        dialog.exec()
        
    def _select_all_accounts(self, list_widget):
        """Select all items in the account list"""
        for i in range(list_widget.count()):
            list_widget.item(i).setSelected(True)
            
    def insert_sql_to_editor(self, center_sql, account_sql, sign_flip_accounts=None):
        """Insert the SQL clauses into the SQL editor"""
        # Get the main window
        main_window = self.window()
        if not main_window:
            return
            
        # Get the SQL editor
        sql_editor = main_window.sql_editor
        if not sql_editor:
            return
            
        # Get current SQL text
        current_sql = sql_editor.get_text()
        
        # Replace placeholders if they exist
        if "{center_sql}" in current_sql:
            current_sql = current_sql.replace("{center_sql}", center_sql)
        if "{account_sql}" in current_sql:
            current_sql = current_sql.replace("{account_sql}", account_sql)
            
        # Add sign flip accounts as a comment if any are selected
        if sign_flip_accounts:
            sign_flip_comment = "\n-- Sign flip accounts: " + ", ".join(sign_flip_accounts)
            current_sql += sign_flip_comment
            
        # Update the SQL editor
        sql_editor.set_text(current_sql)
        
        # Switch to SQL tab
        main_window.tab_widget.setCurrentIndex(1)  # Assuming SQL tab is index 1
        
        # Store sign flip accounts in the main window for later use in comparison
        if hasattr(main_window, 'comparison_engine'):
            main_window.comparison_engine.set_sign_flip_accounts(sign_flip_accounts)
        
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        
        # Optional: Show a brief notification
        from PyQt6.QtWidgets import QToolTip
        QToolTip.showText(QCursor.pos(), "Copied to clipboard", self)

    def clean_all_sheets(self):
        """Clean all sheets in the Excel file using the current report configuration"""
        # Confirm before proceeding
        from PyQt6.QtWidgets import QMessageBox
        response = QMessageBox.question(
            self,
            "Clean All Sheets",
            "This will clean ALL sheets in the workbook using the current report type configuration. "
            "This operation cannot be undone. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if response != QMessageBox.StandardButton.Yes:
            return
            
        # Get the parent window to access Excel analyzer
        from src.ui.main_window import MainWindow
        parent = self.window()
        if not parent or not isinstance(parent, MainWindow) or not hasattr(parent, 'excel_analyzer'):
            QMessageBox.warning(self, "Error", "Could not access the main application or Excel analyzer.")
            return
            
        # Get the Excel analyzer and sheet names
        excel_analyzer = parent.excel_analyzer
        sheet_names = excel_analyzer.sheet_names
        
        if not sheet_names:
            QMessageBox.warning(self, "No Sheets", "No Excel sheets are available to clean.")
            return
            
        # Track results
        cleaned_sheets = []
        skipped_sheets = []
        failed_sheets = []
        
        # Remember the current sheet name
        current_sheet_name = self.sheet_name
        
        # Progress dialog
        from PyQt6.QtWidgets import QProgressDialog
        progress = QProgressDialog("Cleaning sheets...", "Cancel", 0, len(sheet_names), self)
        progress.setWindowTitle("Clean All Sheets")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)  # Show immediately
        
        try:
            # Process each sheet
            for i, sheet_name in enumerate(sheet_names):
                if progress.wasCanceled():
                    break
                    
                progress.setValue(i)
                progress.setLabelText(f"Cleaning sheet: {sheet_name}")
                
                # Load the sheet if not already analyzed
                if sheet_name not in excel_analyzer.sheet_data:
                    excel_analyzer.analyze_sheet(sheet_name)
                    
                # Get the dataframe for this sheet
                df = excel_analyzer.sheet_data[sheet_name]["dataframe"]
                
                # Check if sheet has enough rows
                if len(df) <= max(self.report_config["header_rows"]):
                    skipped_sheets.append(f"{sheet_name} (not enough rows)")
                    continue
                    
                # Check if sheet is already cleaned
                if "Sheet_Name" in df.columns and df.columns[0] == "Sheet_Name":
                    skipped_sheets.append(f"{sheet_name} (already cleaned)")
                    continue
                
                # Create temporary copy of dataframe for cleaning
                temp_df = df.copy()
                cleaned_df = self._clean_dataframe(temp_df, sheet_name)
                
                if cleaned_df is not None:
                    # Update the dataframe in the analyzer
                    excel_analyzer.sheet_data[sheet_name]["dataframe"] = cleaned_df
                    cleaned_sheets.append(sheet_name)
                else:
                    failed_sheets.append(sheet_name)
            
            # Complete progress
            progress.setValue(len(sheet_names))
            
            # If the current sheet was processed, reload it in the viewer
            if current_sheet_name in cleaned_sheets:
                df = excel_analyzer.sheet_data[current_sheet_name]["dataframe"]
                self.load_dataframe(df, current_sheet_name)
                
            # Show summary message
            summary_message = f"Cleaning completed:\n\n"
            summary_message += f"- {len(cleaned_sheets)} sheets cleaned\n"
            if cleaned_sheets:
                summary_message += f"  ({', '.join(cleaned_sheets[:5])}{'...' if len(cleaned_sheets) > 5 else ''})\n\n"
                
            summary_message += f"- {len(skipped_sheets)} sheets skipped\n"
            if skipped_sheets:
                summary_message += f"  ({', '.join(skipped_sheets[:5])}{'...' if len(skipped_sheets) > 5 else ''})\n\n"
                
            if failed_sheets:
                summary_message += f"- {len(failed_sheets)} sheets failed\n"
                summary_message += f"  ({', '.join(failed_sheets)})\n"
                
            QMessageBox.information(self, "Clean All Sheets Completed", summary_message)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"An error occurred while cleaning sheets: {str(e)}")
        finally:
            progress.close()
    
    def _clean_dataframe(self, df, sheet_name):
        """Clean a dataframe using the report configuration."""
        clean_df = self._base_clean_dataframe(df, sheet_name)
        if clean_df is None:
            return None

        # Remove original row indices left from the source file
        clean_df = clean_df.reset_index(drop=True)

        # If the first row appears to repeat the column headers (which can occur
        # when export utilities duplicate the header row), drop it so that the
        # actual data starts immediately after the configured ``skip_rows``
        if not clean_df.empty:
            header_vals = [str(c).strip().lower() for c in clean_df.columns]
            row_vals = [str(v).strip().lower() for v in clean_df.iloc[0].tolist()]

            # Ignore the sheet name column when comparing
            if header_vals and header_vals[0] == "sheet_name":
                header_vals = header_vals[1:]
                row_vals = row_vals[1:]

            if row_vals == header_vals:
                clean_df = clean_df.iloc[1:].reset_index(drop=True)

        if self.report_type in ("SOO MFR", "MFR PreClose"):
            from PyQt6.QtWidgets import QInputDialog

            if not hasattr(self, "_mfr_month_year"):
                months = [
                    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
                ]
                mon, ok1 = QInputDialog.getItem(self, "Month", "Select Month", months, 0, False)
                years = [str(y) for y in range(2000, 2101)]
                yr_text, ok2 = QInputDialog.getItem(self, "Year", "Select Year", years, 0, False)
                if not (ok1 and ok2):
                    return clean_df
                try:
                    yr = int(yr_text)
                except ValueError:
                    return clean_df
                self._mfr_month_year = (mon, yr)
            else:
                mon, yr = self._mfr_month_year

            # Determine where the actual numeric data starts. The base cleaning
            # routine normally inserts a ``Sheet_Name`` column at position 0.
            # For SOO MFR that column is omitted, so only offset when it is
            # present.
            data_start = self.report_config.get("first_data_column", 2)
            if self.report_type != "SOO MFR":
                data_start += 1

            # Build the prefix ranges relative to ``data_start`` so that the
            # correct columns are renamed even when ``first_data_column`` is
            # customised by different report configurations.
            prefixes = (
                (range(data_start, data_start + 6), f"{mon} {yr} "),
                (range(data_start + 6, data_start + 9), f"{mon} {yr - 1} "),
                (range(data_start + 9, data_start + 13), f"YTD {mon} {yr} "),
                (range(data_start + 13, data_start + 16), f"YTD {mon} {yr - 1} "),
            )

            for cols, prefix in prefixes:
                for i in cols:
                    if i < len(clean_df.columns):
                        clean_df.rename(
                            columns={clean_df.columns[i]: prefix + clean_df.columns[i]},
                            inplace=True,
                        )

            # Remove leftover numeric suffixes when prefixes make names unique
            clean_df.columns = _dedupe_columns(list(clean_df.columns))

            return clean_df


        # No additional processing is needed for AR Center. Historically the
        # CAReportName values were prefixed with the sheet name here, but the
        # comparison logic now uses a dedicated ``Sheet`` column instead.
        if self.report_type == "AR Center":
            pass

        return clean_df

    def clean_sheet(self):
        """Clean the current sheet based on the report configuration"""
        if self.df is None or self.df.empty or self.sheet_name is None:
            return
            
        # Check if sheet has already been cleaned
        if self.is_sheet_already_cleaned():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Already Cleaned", 
                "This sheet appears to have already been cleaned.")
            
            # Disable the clean button
            self.clean_button.setEnabled(False)
            self.clean_button.setToolTip("Sheet has already been cleaned")
            return False
            
        try:
            # Get a clean copy of the dataframe
            cleaned_df = self._clean_dataframe(self.df.copy(), self.sheet_name)
            
            if cleaned_df is None:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Cannot Clean", 
                    f"Unable to clean sheet {self.sheet_name}. See console for details.")
                return False
            
            # Update the dataframe
            self.df = cleaned_df
            self.filtered_df = cleaned_df.copy()

            # Propagate cleaned dataframe back to the analyzer
            from src.ui.main_window import MainWindow
            parent = self.window()
            if (
                parent
                and isinstance(parent, MainWindow)
                and hasattr(parent, "excel_analyzer")
                and self.sheet_name in parent.excel_analyzer.sheet_data
            ):
                parent.excel_analyzer.sheet_data[self.sheet_name][
                    "dataframe"
                ] = cleaned_df.copy()
            
            # Reload the dataframe to update the view
            self.load_dataframe(self.df, self.sheet_name)
            
            # Disable the clean button - sheet is now cleaned
            self.clean_button.setEnabled(False)
            self.clean_button.setToolTip("Sheet has already been cleaned")
            
            # Make sure other buttons are still enabled since we have data
            self.update_button_states(True)
            
            # Get human-readable row descriptions (converting from 0-indexed to 1-indexed)
            header_rows_text = ", ".join([str(idx + 1) for idx in self.report_config["header_rows"]])

            # Build message elements based on report configuration
            if len(self.report_config["header_rows"]) > 1:
                header_note = f"- Headers from rows {header_rows_text} have been concatenated\n"
            else:
                header_note = f"- Header from row {header_rows_text} has been applied\n"

            skip_note = (
                f"- {self.report_config['skip_rows']} rows above the header have been removed\n"
            )

            sheet_col_note = ""
            if self.report_type not in ("SOO MFR", "Corp SOO"):
                sheet_col_note = "- A new column with the sheet name has been added\n"

            # Show a status message
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Sheet Cleaned",
                f"The sheet has been cleaned successfully using {self.report_config['description']}:\n"
                f"{header_note}"
                f"{skip_note}"
                f"- Blank rows have been removed\n"
                f"- Completely empty columns have been removed\n"
                f"{sheet_col_note}\n"
                f"You can now double-click on column headers to edit them."
            )
            
            return True
            
        except Exception as e:
            print(f"Error cleaning sheet: {str(e)}")
            import traceback
            traceback.print_exc()
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to clean sheet: {str(e)}")
            return False
    
    def reset(self):
        """Reset the Excel viewer, clearing all data"""
        # Clear dataframes
        self.df = None
        self.filtered_df = None
        self.sheet_name = None
        
        # Clear column filter dropdown
        self.filter_column.clear()
        self.filter_text.clear()
        
        # Create an empty model
        import pandas as pd
        empty_df = pd.DataFrame()
        self.model = PandasTableModel(
            empty_df, self.current_theme.lower() == "dark")
        self.table_view.setModel(self.model)
        
        # Update status
        self.status_label.setText("No data loaded")
        
        # Disable all buttons
        self.update_button_states(False)
        self.clean_button.setEnabled(False)

    def apply_widget_theme(self, theme: str):
        """Apply base style and theme colors to the Excel viewer."""
        self.current_theme = theme or "system"

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

        # Clear per-widget styles so the loaded QSS can apply globally
        self.setStyleSheet(qss)
        self.table_view.setStyleSheet(qss)
        if self.toolbar:
            self.toolbar.setStyleSheet(qss)

        # Update the table model with the new theme
        if hasattr(self, "model") and self.model:
            self.model.set_dark_theme(theme_lower == "dark")
