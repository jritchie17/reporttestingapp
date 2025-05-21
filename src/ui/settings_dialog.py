from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QComboBox, QSpinBox,
                             QDoubleSpinBox, QCheckBox, QTabWidget, QWidget,
                             QFormLayout, QDialogButtonBox, QGroupBox, QFrame,
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont
import os
import re


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.parent_window = parent
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        main_layout = QVBoxLayout(self)
        
        # Create tabbed interface for settings categories
        self.tab_widget = QTabWidget()
        
        # Database tab
        self.create_database_tab()
        
        # Excel tab
        self.create_excel_tab()
        
        # UI tab
        self.create_ui_tab()
        
        # Testing tab
        self.create_testing_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
    def create_database_tab(self):
        """Create database settings tab"""
        db_tab = QWidget()
        layout = QFormLayout(db_tab)
        
        # Database server
        self.db_server = QLineEdit()
        layout.addRow("Server:", self.db_server)
        
        # Database name
        self.db_name = QLineEdit()
        layout.addRow("Database:", self.db_name)
        
        # Authentication mode group
        auth_group = QGroupBox("Authentication")
        auth_layout = QVBoxLayout(auth_group)
        
        self.use_trusted_auth = QCheckBox("Use Windows Authentication")
        self.use_trusted_auth.setChecked(True)
        auth_layout.addWidget(self.use_trusted_auth)
        
        # Credentials group (disabled when using Windows auth)
        credentials_frame = QFrame()
        credentials_layout = QFormLayout(credentials_frame)
        
        self.db_username = QLineEdit()
        self.db_password = QLineEdit()
        self.db_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        credentials_layout.addRow("Username:", self.db_username)
        credentials_layout.addRow("Password:", self.db_password)
        
        auth_layout.addWidget(credentials_frame)
        
        # Connect checkbox to enable/disable credentials
        self.use_trusted_auth.toggled.connect(lambda checked: credentials_frame.setDisabled(checked))
        
        layout.addRow(auth_group)
        
        # Connection test button
        self.test_connection_button = QPushButton("Test Connection")
        self.test_connection_button.clicked.connect(self.test_database_connection)
        layout.addRow("", self.test_connection_button)
        
        self.tab_widget.addTab(db_tab, "Database")
        
    def create_excel_tab(self):
        """Create Excel settings tab"""
        excel_tab = QWidget()
        layout = QFormLayout(excel_tab)
        
        # Default header rows
        self.header_rows = QSpinBox()
        self.header_rows.setRange(0, 20)
        layout.addRow("Default header rows:", self.header_rows)
        
        # Numerical comparison tolerance
        self.num_tolerance = QDoubleSpinBox()
        self.num_tolerance.setRange(0.0000001, 1.0)
        self.num_tolerance.setDecimals(7)
        self.num_tolerance.setSingleStep(0.001)
        layout.addRow("Numerical comparison tolerance:", self.num_tolerance)
        
        # Skip empty rows
        self.skip_empty_rows = QCheckBox("Skip empty rows")
        layout.addRow("", self.skip_empty_rows)
        
        # Skip empty columns
        self.skip_empty_cols = QCheckBox("Skip empty columns")
        layout.addRow("", self.skip_empty_cols)
        
        self.tab_widget.addTab(excel_tab, "Excel")
        
    def create_ui_tab(self):
        """Create UI settings tab"""
        ui_tab = QWidget()
        layout = QFormLayout(ui_tab)
        
        # Theme selection
        self.theme = QComboBox()
        self.theme.addItems(["Light", "Dark", "System", "Brand"])
        layout.addRow("Theme:", self.theme)
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 18)
        layout.addRow("Font size:", self.font_size)
        
        # Show line numbers
        self.show_line_numbers = QCheckBox("Show line numbers in SQL editor")
        layout.addRow("", self.show_line_numbers)
        
        # Auto-save queries
        self.auto_save_queries = QCheckBox("Auto-save queries")
        layout.addRow("", self.auto_save_queries)
        
        self.tab_widget.addTab(ui_tab, "User Interface")
        
    def create_testing_tab(self):
        """Create testing settings tab"""
        testing_tab = QWidget()
        layout = QFormLayout(testing_tab)
        
        # Auto-generate queries
        self.auto_generate = QCheckBox("Auto-generate SQL queries from Excel")
        layout.addRow("", self.auto_generate)
        
        # Show suggestions
        self.show_suggestions = QCheckBox("Show query suggestions")
        layout.addRow("", self.show_suggestions)
        
        # Comparison threshold
        self.comparison_threshold = QDoubleSpinBox()
        self.comparison_threshold.setRange(0.0, 100.0)
        self.comparison_threshold.setDecimals(1)
        self.comparison_threshold.setSuffix("%")
        layout.addRow("Comparison threshold:", self.comparison_threshold)
        layout.addRow("", QLabel("Maximum percentage difference allowed for a test to pass"))
        
        self.tab_widget.addTab(testing_tab, "Testing")
        
    def load_settings(self):
        """Load settings from configuration"""
        # Database settings
        self.db_server.setText(self.config.get("database", "server"))
        self.db_name.setText(self.config.get("database", "database"))
        self.use_trusted_auth.setChecked(self.config.get("database", "trusted_connection"))
        
        # Excel settings
        self.header_rows.setValue(self.config.get("excel", "default_header_rows"))
        self.num_tolerance.setValue(self.config.get("excel", "numerical_comparison_tolerance"))
        self.skip_empty_rows.setChecked(self.config.get("excel", "skip_empty_rows"))
        self.skip_empty_cols.setChecked(self.config.get("excel", "skip_empty_columns"))
        
        # UI settings
        theme_map = {"light": 0, "dark": 1, "system": 2, "brand": 3}
        theme = self.config.get("ui", "theme")
        self.theme.setCurrentIndex(theme_map.get(theme.lower(), 0))
        # Connect after setting initial value to avoid unnecessary update
        self.theme.currentIndexChanged.connect(self._on_theme_changed)
        
        self.font_size.setValue(self.config.get("ui", "font_size"))
        self.show_line_numbers.setChecked(self.config.get("ui", "show_line_numbers"))
        self.auto_save_queries.setChecked(self.config.get("ui", "auto_save_queries"))
        
        # Testing settings
        self.auto_generate.setChecked(self.config.get("testing", "auto_generate_queries"))
        self.show_suggestions.setChecked(self.config.get("testing", "show_suggestions"))
        self.comparison_threshold.setValue(self.config.get("testing", "comparison_threshold") * 100)  # Convert to percentage

    def _on_theme_changed(self, index):
        """Apply theme immediately when the user selects a new option"""
        theme_options = ["light", "dark", "system", "brand"]
        self.config.set("ui", "theme", theme_options[index])
        if self.parent_window and hasattr(self.parent_window, "apply_theme"):
            self.parent_window.apply_theme()
    
    def save_settings(self):
        """Save settings to configuration"""
        # Database settings
        self.config.set("database", "server", self.db_server.text())
        self.config.set("database", "database", self.db_name.text())
        self.config.set("database", "trusted_connection", self.use_trusted_auth.isChecked())
        
        # Excel settings
        self.config.set("excel", "default_header_rows", self.header_rows.value())
        self.config.set("excel", "numerical_comparison_tolerance", self.num_tolerance.value())
        self.config.set("excel", "skip_empty_rows", self.skip_empty_rows.isChecked())
        self.config.set("excel", "skip_empty_columns", self.skip_empty_cols.isChecked())
        
        # UI settings
        theme_options = ["light", "dark", "system", "brand"]
        self.config.set("ui", "theme", theme_options[self.theme.currentIndex()])
        
        self.config.set("ui", "font_size", self.font_size.value())
        self.config.set("ui", "show_line_numbers", self.show_line_numbers.isChecked())
        self.config.set("ui", "auto_save_queries", self.auto_save_queries.isChecked())
        
        # Testing settings
        self.config.set("testing", "auto_generate_queries", self.auto_generate.isChecked())
        self.config.set("testing", "show_suggestions", self.show_suggestions.isChecked())
        self.config.set("testing", "comparison_threshold", self.comparison_threshold.value() / 100.0)  # Convert from percentage
        
        # Save configuration to file
        self.config.save_config()
        
        self.accept()
        
    def test_database_connection(self):
        """Test database connection with current settings"""
        from src.database.db_connector import DatabaseConnector
        
        server = self.db_server.text()
        database = self.db_name.text()
        trusted_connection = self.use_trusted_auth.isChecked()
        
        if not server or not database:
            QMessageBox.warning(self, "Missing Information", "Please enter server and database names.")
            return
            
        try:
            # Create test connector
            db_connector = DatabaseConnector(
                server=server,
                database=database,
                trusted_connection=trusted_connection
            )
            
            # Try to connect
            if db_connector.connect():
                QMessageBox.information(self, "Connection Successful", 
                                       f"Successfully connected to {database} on {server}.")
                
                # Close connection
                db_connector.close()
            else:
                QMessageBox.warning(self, "Connection Failed", 
                                  f"Failed to connect to {database} on {server}.\nPlease check your settings.")
                
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", 
                               f"An error occurred when connecting to the database:\n{str(e)}")
