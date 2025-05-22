import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QApplication, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFileDialog, QMessageBox, QStatusBar, QMenuBar, 
                             QMenu, QToolBar, QSplitter, QComboBox, QLineEdit, 
                             QProgressDialog, QDialog, QListWidget, QDialogButtonBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QFont

from src.ui.hover_anim_filter import HoverAnimationFilter

# Import custom widgets
from src.ui.excel_viewer import ExcelViewer
from src.ui.sql_editor import SQLEditor
from src.ui.results_viewer import ResultsViewer
from src.ui.comparison_view import ComparisonView
from src.ui.settings_dialog import SettingsDialog
from src.ui.account_category_dialog import AccountCategoryDialog

# Import backend services
from src.database.db_connector import DatabaseConnector
from src.analyzer.excel_analyzer import ExcelAnalyzer
from src.analyzer.comparison_engine import ComparisonEngine
from src.utils.config import AppConfig

import qtawesome as qta
import pandas as pd
import re


class MainWindow(QMainWindow):
    def __init__(self):
        """Initialize the main window"""
        super().__init__()
        self.setWindowTitle("SOO PreClose Report Tester")
        self.setMinimumSize(1200, 800)
        
        # Load configuration
        self.config = AppConfig()
        
        # Set up logging
        from src.utils.logging_config import get_logger
        self.logger = get_logger(__name__)
        
        # Initialize components
        self.excel_analyzer = None
        self.db_connector = None
        self.comparison_engine = None
        
        # Initialize report configuration
        self.report_configs = self.initialize_report_configs()
        
        # Set up the UI
        self.hover_filter = HoverAnimationFilter()
        self.init_ui()
        # Apply theme after UI is created
        self.apply_theme()
        
        # Connect to database
        self.connect_to_database()
        
        # Set initial report type from config if available
        # Retrieve the last used report type from the config
        # AppConfig.get expects a section/key pair, not dotted notation
        initial_report_type = self.config.get("excel", "report_type")
        if initial_report_type:
            index = self.report_selector.findText(initial_report_type)
            if index >= 0:
                self.report_selector.setCurrentIndex(index)
        
        # Load last session if enabled
        # Likewise fetch the flag for restoring the last session
        load_last_session = self.config.get("ui", "load_last_session")
        if load_last_session:
            self.load_last_session()

    def _apply_hover_animation(self, widget):
        """Install hover animation filter on a widget."""
        if widget:
            widget.installEventFilter(self.hover_filter)
        
        
    def init_ui(self):
        """Initialize the user interface"""
        # Set up central widget with main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create header with main actions
        self.create_header()
        
        # Create main content area with splitter
        self.create_main_content()
        
        # Set up status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def create_menu_bar(self):
        """Create the application menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # Open Excel
        open_excel_action = QAction(qta.icon('fa5s.file-excel'), "Open Excel File", self)
        open_excel_action.setShortcut("Ctrl+O")
        open_excel_action.triggered.connect(self.open_excel_file)
        file_menu.addAction(open_excel_action)
        
        # Open SQL
        open_sql_action = QAction(qta.icon('fa5s.file-code'), "Open SQL File", self)
        open_sql_action.setShortcut("Ctrl+Shift+O")
        open_sql_action.triggered.connect(self.open_sql_file)
        file_menu.addAction(open_sql_action)
        
        file_menu.addSeparator()
        
        # Save SQL
        save_sql_action = QAction(qta.icon('fa5s.save'), "Save SQL", self)
        save_sql_action.setShortcut("Ctrl+S")
        save_sql_action.triggered.connect(self.save_sql)
        file_menu.addAction(save_sql_action)
        
        # Save Report
        save_report_action = QAction(qta.icon('fa5s.file-export'), "Export Comparison Report", self)
        save_report_action.setShortcut("Ctrl+E")
        save_report_action.triggered.connect(self.export_report)
        file_menu.addAction(save_report_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction(qta.icon('fa5s.sign-out-alt'), "Exit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Database menu
        db_menu = menu_bar.addMenu("&Database")
        
        # Connect
        connect_action = QAction(qta.icon('fa5s.database'), "Connect to Database", self)
        connect_action.triggered.connect(self.connect_to_database)
        db_menu.addAction(connect_action)
        
        # Disconnect
        disconnect_action = QAction(qta.icon('fa5s.unlink'), "Disconnect", self)
        disconnect_action.triggered.connect(self.disconnect_database)
        db_menu.addAction(disconnect_action)
        
        db_menu.addSeparator()
        
        # Execute SQL
        execute_action = QAction(qta.icon('fa5s.play'), "Execute SQL", self)
        execute_action.setShortcut("F5")
        execute_action.triggered.connect(self.execute_sql)
        db_menu.addAction(execute_action)
        
        # Tools menu
        tools_menu = menu_bar.addMenu("&Tools")
        
        # Compare
        compare_action = QAction(qta.icon('fa5s.exchange-alt'), "Compare Excel with SQL Results", self)
        compare_action.setShortcut("F9")
        compare_action.triggered.connect(self.compare_results)
        tools_menu.addAction(compare_action)
        
        # Generate SQL
        generate_action = QAction(qta.icon('fa5s.magic'), "Generate SQL from Excel", self)
        generate_action.setShortcut("F7")
        generate_action.triggered.connect(self.generate_sql)
        tools_menu.addAction(generate_action)
        
        # Reset Application
        reset_action = QAction(qta.icon('fa5s.sync'), "Reset Application", self)
        reset_action.setShortcut("Ctrl+R")
        reset_action.triggered.connect(self.reset_application)
        tools_menu.addAction(reset_action)
        
        tools_menu.addSeparator()

        manage_cats_action = QAction(qta.icon('fa5s.layer-group'), "Manage Account Categories...", self)
        manage_cats_action.triggered.connect(self.open_account_categories)
        tools_menu.addAction(manage_cats_action)

        # Settings
        settings_action = QAction(qta.icon('fa5s.cog'), "Settings", self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        # About
        about_action = QAction(qta.icon('fa5s.info-circle'), "About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create the application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Open Excel
        open_excel_action = QAction(qta.icon('fa5s.file-excel'), "Open Excel File", self)
        open_excel_action.triggered.connect(self.open_excel_file)
        toolbar.addAction(open_excel_action)
        self._apply_hover_animation(toolbar.widgetForAction(open_excel_action))
        
        # Execute SQL
        execute_action = QAction(qta.icon('fa5s.play'), "Execute SQL", self)
        execute_action.triggered.connect(self.execute_sql)
        toolbar.addAction(execute_action)
        self._apply_hover_animation(toolbar.widgetForAction(execute_action))
        
        # Compare
        compare_action = QAction(qta.icon('fa5s.exchange-alt'), "Compare", self)
        compare_action.triggered.connect(self.compare_results)
        toolbar.addAction(compare_action)
        self._apply_hover_animation(toolbar.widgetForAction(compare_action))
        
        # Generate SQL
        generate_action = QAction(qta.icon('fa5s.magic'), "Generate SQL", self)
        generate_action.triggered.connect(self.generate_sql)
        toolbar.addAction(generate_action)
        self._apply_hover_animation(toolbar.widgetForAction(generate_action))
        
        # Reset application
        reset_action = QAction(qta.icon('fa5s.sync'), "Reset", self)
        reset_action.setToolTip("Reset application to start a new test")
        reset_action.triggered.connect(self.reset_application)
        toolbar.addAction(reset_action)
        self._apply_hover_animation(toolbar.widgetForAction(reset_action))

        manage_cats_action = QAction(qta.icon('fa5s.layer-group'), "Manage Account Categories...", self)
        manage_cats_action.triggered.connect(self.open_account_categories)
        toolbar.addAction(manage_cats_action)
        self._apply_hover_animation(toolbar.widgetForAction(manage_cats_action))

        # Settings
        settings_action = QAction(qta.icon('fa5s.cog'), "Settings", self)
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)
        self._apply_hover_animation(toolbar.widgetForAction(settings_action))
    
    def create_header(self):
        """Create the application header with main actions"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Database connection status
        self.db_status_label = QLabel("Database: Not Connected")
        header_layout.addWidget(self.db_status_label)
        
        # Excel file status
        self.excel_status_label = QLabel("Excel: No file loaded")
        header_layout.addWidget(self.excel_status_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Report type selector
        header_layout.addWidget(QLabel("Report:"))
        self.report_selector = QComboBox()
        self.report_selector.setMinimumWidth(150)
        self.report_selector.addItems([
            "SOO PreClose",
            "SOO MFR",
            "Executive Book",
            "Statement of Operations",
            "Corp SOO",
            "AR Center"
        ])
        self.report_selector.currentIndexChanged.connect(self.report_type_changed)
        header_layout.addWidget(self.report_selector)
        
        # Sheet selector
        header_layout.addWidget(QLabel("Sheet:"))
        self.sheet_selector = QComboBox()
        self.sheet_selector.setMinimumWidth(200)
        self.sheet_selector.currentIndexChanged.connect(self.switch_sheet)
        header_layout.addWidget(self.sheet_selector)
        
        self.main_layout.addWidget(header_widget)
    
    def create_main_content(self):
        """Create the main content area with tabs"""
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Excel tab
        self.excel_tab = QWidget()
        excel_layout = QVBoxLayout(self.excel_tab)
        self.excel_viewer = ExcelViewer()
        excel_layout.addWidget(self.excel_viewer)
        self.tab_widget.addTab(self.excel_tab, "Excel Data")
        
        # SQL tab with editor and results
        self.sql_tab = QWidget()
        sql_layout = QVBoxLayout(self.sql_tab)
        
        sql_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # SQL editor area
        self.sql_editor = SQLEditor()
        sql_splitter.addWidget(self.sql_editor)
        
        # SQL results area
        self.results_viewer = ResultsViewer()
        sql_splitter.addWidget(self.results_viewer)
        
        # Set initial sizes for splitter
        sql_splitter.setSizes([400, 300])
        
        sql_layout.addWidget(sql_splitter)
        self.tab_widget.addTab(self.sql_tab, "SQL Query")
        
        # Comparison tab
        self.comparison_tab = QWidget()
        comparison_layout = QVBoxLayout(self.comparison_tab)
        self.comparison_view = ComparisonView()
        comparison_layout.addWidget(self.comparison_view)
        # Add Export Results button
        self.export_results_button = QPushButton("Export Results")
        self.export_results_button.clicked.connect(self.export_detailed_results)
        self._apply_hover_animation(self.export_results_button)
        comparison_layout.addWidget(self.export_results_button)
        # Add Export PDF button
        self.export_pdf_button = QPushButton("Export PDF")
        self.export_pdf_button.clicked.connect(self.export_pdf_report)
        self._apply_hover_animation(self.export_pdf_button)
        comparison_layout.addWidget(self.export_pdf_button)
        self.tab_widget.addTab(self.comparison_tab, "Comparison")

        # Apply hover animation to tab bar buttons
        tab_bar = self.tab_widget.tabBar()
        self._apply_hover_animation(tab_bar)
        for child in tab_bar.findChildren(QWidget):
            self._apply_hover_animation(child)

        self.main_layout.addWidget(self.tab_widget)
    
    def connect_to_database(self):
        """Connect to the SQL database"""
        try:
            # Get connection parameters from config
            db_params = self.config.get_db_connection_params()
            
            # Initialize database connector
            self.db_connector = DatabaseConnector(**db_params)
            
            # Connect to database
            if self.db_connector.connect():
                self.db_status_label.setText(f"Database: Connected to {db_params['database']}")
                self.status_bar.showMessage(f"Successfully connected to {db_params['database']} on {db_params['server']}")
                return True
            else:
                self.db_status_label.setText("Database: Connection Failed")
                self.status_bar.showMessage("Failed to connect to database")
                QMessageBox.warning(self, "Connection Failed", 
                                    f"Failed to connect to {db_params['database']} on {db_params['server']}. Please check your settings.")
                return False
                
        except Exception as e:
            self.db_status_label.setText("Database: Connection Failed")
            self.status_bar.showMessage(f"Error connecting to database: {str(e)}")
            QMessageBox.critical(self, "Connection Error", f"An error occurred when connecting to the database: {str(e)}")
            return False
    
    def disconnect_database(self):
        """Disconnect from the database"""
        if self.db_connector:
            self.db_connector.close()
            self.db_connector = None
            self.db_status_label.setText("Database: Not Connected")
            self.status_bar.showMessage("Disconnected from database")
    
    def open_excel_file(self):
        """Open an Excel file"""
        # Get the last directory used
        last_excel = self.config.get("paths", "last_excel_file")
        start_dir = os.path.dirname(last_excel) if last_excel else os.path.expanduser("~")
        
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Excel File", start_dir, "Excel Files (*.xlsx *.xls *.xlsm)"
        )
        
        if not file_path:
            return
            
        # Update config
        self.config.update_last_excel_file(file_path)
        
        # Load Excel file
        self.load_excel_file(file_path)
    
    def load_excel_file(self, file_path):
        """Load an Excel file into the analyzer and viewer"""
        try:
            # Initialize Excel analyzer
            self.excel_analyzer = ExcelAnalyzer(file_path)
            
            # Load Excel file
            if not self.excel_analyzer.load_excel():
                QMessageBox.warning(self, "Load Failed", f"Failed to load Excel file: {file_path}")
                return False
                
            # Initialize comparison engine
            self.comparison_engine = ComparisonEngine()
            tolerance = self.config.get("excel", "numerical_comparison_tolerance")
            self.comparison_engine.set_tolerance(tolerance)
            
            # Update sheet selector
            self.sheet_selector.clear()
            self.sheet_selector.addItems(self.excel_analyzer.sheet_names)
            
            # Update status
            file_name = os.path.basename(file_path)
            self.excel_status_label.setText(f"Excel: {file_name}")
            self.status_bar.showMessage(f"Loaded Excel file: {file_path}")
            
            # Load first sheet
            if self.sheet_selector.count() > 0:
                self.switch_sheet(0)
                
            return True
                
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"An error occurred when loading the Excel file: {str(e)}")
            return False
    
    def switch_sheet(self, index):
        """Switch to a different Excel sheet"""
        if index < 0 or not self.excel_analyzer:
            return
            
        sheet_name = self.sheet_selector.itemText(index)
        
        try:
            # Analyze sheet if not already analyzed
            if sheet_name not in self.excel_analyzer.sheet_data:
                self.excel_analyzer.analyze_sheet(sheet_name)
                
            # Load sheet into viewer
            df = self.excel_analyzer.sheet_data[sheet_name]["dataframe"]
            self.excel_viewer.load_dataframe(df, sheet_name)
            
            # Update SQL editor with suggested queries
            suggested_queries = self.excel_analyzer.get_smart_query_suggestions(sheet_name)
            if suggested_queries and self.config.get("testing", "show_suggestions"):
                self.sql_editor.set_suggestions(suggested_queries)
                
            # Update status
            self.status_bar.showMessage(f"Loaded sheet: {sheet_name}")
            
        except Exception as e:
            QMessageBox.warning(self, "Sheet Error", f"Error loading sheet {sheet_name}: {str(e)}")
    
    def open_sql_file(self):
        """Open a SQL file"""
        # Get the last directory used
        last_sql = self.config.get("paths", "last_sql_file")
        start_dir = os.path.dirname(last_sql) if last_sql else os.path.expanduser("~")
        
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open SQL File", start_dir, "SQL Files (*.sql);;All Files (*.*)"
        )
        
        if not file_path:
            return
            
        # Update config
        self.config.update_last_sql_file(file_path)
        
        # Load SQL file
        self.load_sql_file(file_path)
    
    def load_sql_file(self, file_path):
        """Load a SQL file into the editor"""
        try:
            with open(file_path, 'r') as f:
                sql_content = f.read()
                
            self.sql_editor.set_text(sql_content)
            self.status_bar.showMessage(f"Loaded SQL file: {file_path}")
            
            # Switch to SQL tab
            self.tab_widget.setCurrentIndex(1)
            
            return True
                
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"An error occurred when loading the SQL file: {str(e)}")
            return False
    
    def save_sql(self):
        """Save the current SQL query to a file"""
        # Get SQL content
        sql_content = self.sql_editor.get_text()
        
        if not sql_content.strip():
            QMessageBox.warning(self, "Empty SQL", "There is no SQL query to save.")
            return
            
        # Get the last directory used
        last_sql = self.config.get("paths", "last_sql_file")
        start_dir = os.path.dirname(last_sql) if last_sql else os.path.expanduser("~")
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save SQL File", start_dir, "SQL Files (*.sql)"
        )
        
        if not file_path:
            return
            
        # Add .sql extension if not present
        if not file_path.lower().endswith('.sql'):
            file_path += '.sql'
            
        try:
            with open(file_path, 'w') as f:
                f.write(sql_content)
                
            # Update config
            self.config.update_last_sql_file(file_path)
            
            self.status_bar.showMessage(f"Saved SQL file: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"An error occurred when saving the SQL file: {str(e)}")
    
    def execute_sql(self):
        """Execute the current SQL query"""
        if not self.db_connector:
            QMessageBox.warning(self, "Not Connected", "Please connect to a database first.")
            return
            
        # Get SQL content
        sql_content = self.sql_editor.get_text()
        
        if not sql_content.strip():
            QMessageBox.warning(self, "Empty SQL", "Please enter a SQL query to execute.")
            return
        
        # Show indeterminate progress dialog
        progress = QProgressDialog("Running SQL query...", None, 0, 0, self)
        progress.setWindowTitle("Executing SQL")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.setCancelButton(None)
        progress.show()
        QApplication.processEvents()
        
        try:
            # Execute query
            self.status_bar.showMessage("Executing SQL query...")
            
            # Check if query contains temp tables
            contains_temp_table = "#" in sql_content
            
            if contains_temp_table:
                # For temp tables, use pyodbc directly with autocommit
                self.logger.info("Query contains temp tables, using special temp table handler")
                
                # Import required modules
                import pyodbc
                import re
                
                # Connection parameters
                server = self.db_connector.server
                database = self.db_connector.database
                
                # Define a function to extract statements
                def extract_statements(sql):
                    # If there's a DROP TABLE statement right after GROUP BY, add a semicolon
                    pattern = r'(GROUP BY\s+[a-zA-Z0-9_.]+)(\s*DROP\s+TABLE)'
                    fixed_sql = re.sub(pattern, r'\1;\n\2', sql)
                    
                    # Split by semicolons
                    statements = [s.strip() for s in fixed_sql.split(';') if s.strip()]
                    return statements
                
                # Create connection with autocommit
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
                self.logger.info(f"Creating direct ODBC connection with autocommit")
                conn = pyodbc.connect(conn_str, autocommit=True)
                cursor = conn.cursor()
                
                # Extract and execute statements
                statements = extract_statements(sql_content)
                self.logger.info(f"Query split into {len(statements)} statements")
                
                rows = None
                columns = None
                
                # Execute each statement
                for i, stmt in enumerate(statements):
                    self.logger.info(f"Executing statement {i+1} of {len(statements)}")
                    cursor.execute(stmt)
                    
                    # If this statement has results, capture them
                    if cursor.description:
                        columns = [column[0] for column in cursor.description]
                        rows = cursor.fetchall()
                        self.logger.info(f"Statement {i+1} returned {len(rows)} rows")
                
                # Prepare result for the viewer
                if rows and columns:
                    # Convert rows to dictionaries
                    data = []
                    for row in rows:
                        row_dict = {}
                        for i, col_name in enumerate(columns):
                            row_dict[col_name] = row[i]
                        data.append(row_dict)
                    
                    result = {"columns": columns, "data": data}
                else:
                    result = {"message": "Query executed successfully (no data returned)"}
                
                # Clean up
                cursor.close()
                conn.close()
            else:
                # Use the regular method for standard queries
                result = self.db_connector.execute_query(sql_content)
            
            if "error" in result:
                QMessageBox.warning(self, "Query Error", f"Error executing query: {result['error']}")
                self.status_bar.showMessage(f"Query failed: {result['error']}")
                return
                
            # Load results into viewer
            if "data" in result:
                self.results_viewer.load_results(result["data"], result.get("columns", []))
                self.status_bar.showMessage(f"Query executed successfully. {len(result['data'])} rows returned.")
            else:
                self.status_bar.showMessage("Query executed successfully (no data returned).")
                
        except Exception as e:
            QMessageBox.critical(self, "Execute Error", f"An error occurred when executing the SQL query: {str(e)}")
        finally:
            progress.close()
    
    def generate_sql(self):
        """Generate SQL queries based on Excel data"""
        if not self.excel_analyzer:
            QMessageBox.warning(self, "No Excel Data", "Please load an Excel file first.")
            return
            
        current_sheet = self.sheet_selector.currentText()
        if not current_sheet:
            return
            
        try:
            # Analyze sheet if not already analyzed
            if current_sheet not in self.excel_analyzer.sheet_data:
                self.excel_analyzer.analyze_sheet(current_sheet)
                
            # Get dataframe
            df = self.excel_analyzer.sheet_data[current_sheet]["dataframe"]
            
            # Initialize query builder
            from src.utils.query_builder import QueryBuilder
            query_builder = QueryBuilder()
            
            # Generate queries
            suggested_queries = query_builder.analyze_excel_for_query(df, current_sheet)
            
            if suggested_queries:
                # Set suggestions in SQL editor
                self.sql_editor.set_suggestions(suggested_queries)
                
                # Switch to SQL tab
                self.tab_widget.setCurrentIndex(1)
                
                self.status_bar.showMessage(f"Generated {len(suggested_queries)} SQL queries from Excel data")
            else:
                QMessageBox.information(self, "No Queries", "Could not generate SQL queries from the current Excel data.")
                
        except Exception as e:
            QMessageBox.critical(self, "Generation Error", f"An error occurred when generating SQL queries: {str(e)}")
    
    def compare_results(self):
        """Compare Excel data with SQL results"""
        if not self.excel_analyzer:
            QMessageBox.warning(self, "No Excel Data", "Please load an Excel file first.")
            return
            
        if not self.results_viewer.has_results():
            QMessageBox.warning(self, "No SQL Results", "Please execute a SQL query first.")
            return
            
        # Get available sheets
        sheet_names = self.excel_analyzer.sheet_names
        if not sheet_names:
            QMessageBox.warning(self, "No Sheets", "No Excel sheets are available.")
            return
            
        # Let user select sheets to compare
        selected_sheets = self._select_sheets_for_comparison(sheet_names)
        if not selected_sheets:
            # User canceled or selected no sheets
            return
            
        sheets_to_compare = selected_sheets
            
        # Prepare for comparison
        sql_df = self.results_viewer.get_dataframe()
        if sql_df.empty:
            QMessageBox.warning(self, "Empty SQL Results", "SQL results are empty.")
            return
            
        # Store comparison results
        comparison_results_by_sheet = {}
        error_sheets = []
        success_sheets = []
        skipped_sheets = []
            
        # Progress dialog for multiple sheets
        if len(sheets_to_compare) > 1:
            progress = QProgressDialog("Comparing sheets...", "Cancel", 0, len(sheets_to_compare), self)
            progress.setWindowTitle("Compare Sheets")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setValue(0)
        else:
            progress = None
            
        try:
            # Compare each sheet
            for i, sheet_name in enumerate(sheets_to_compare):
                if progress and progress.wasCanceled():
                    break
                    
                if progress:
                    progress.setValue(i)
                    progress.setLabelText(f"Comparing sheet: {sheet_name}")
                
                # Get Excel dataframe for this sheet
                try:
                    # Analyze sheet if not already analyzed
                    if sheet_name not in self.excel_analyzer.sheet_data:
                        self.excel_analyzer.analyze_sheet(sheet_name)
                        
                    # Get dataframe
                    excel_df = self.excel_analyzer.sheet_data[sheet_name]["dataframe"]
                    
                    if excel_df.empty:
                        skipped_sheets.append(f"{sheet_name} (empty)")
                        continue
                        
                    # Check if columns are numeric (which would cause matching issues)
                    if all(str(col).isdigit() or (isinstance(col, int)) for col in excel_df.columns):
                        skipped_sheets.append(f"{sheet_name} (numeric columns)")
                        continue

                    # --- FILTER SQL DATAFRAME FOR THIS SHEET ---
                    # Try to find key columns (Center, CAReportName, etc.)
                    key_cols = []
                    for col in ["Center", "CAReportName", "Account", "Sheet_Name"]:
                        if col in excel_df.columns and col in sql_df.columns:
                            key_cols.append(col)
                    
                    filtered_sql_df = sql_df.copy()
                    if key_cols:
                        # Only keep SQL rows that match the unique values for this sheet's key columns
                        for col in key_cols:
                            excel_vals = excel_df[col].dropna().unique()
                            filtered_sql_df = filtered_sql_df[filtered_sql_df[col].isin(excel_vals)]
                    # If no key columns, fallback to all rows (legacy behavior)

                    # Perform comparison
                    sheet_result = self.comparison_engine.compare_dataframes(excel_df, filtered_sql_df)
                    
                    if "error" in sheet_result:
                        error_sheets.append(f"{sheet_name} ({sheet_result['error']})")
                    else:
                        comparison_results_by_sheet[sheet_name] = sheet_result
                        success_sheets.append(sheet_name)
                        
                except Exception as e:
                    self.logger.error(f"Error comparing sheet {sheet_name}: {str(e)}", exc_info=True)
                    error_sheets.append(f"{sheet_name} ({str(e)})")
                    
            # Close progress dialog if needed
            if progress:
                progress.setValue(len(sheets_to_compare))
            
            # Generate combined report
            if comparison_results_by_sheet:
                report, discrepancy_df = self._generate_combined_comparison_report(
                    comparison_results_by_sheet,
                    success_sheets,
                    error_sheets,
                    skipped_sheets,
                )

                # Load report into comparison view
                self.comparison_view.set_report(report)
                self.comparison_view.set_discrepancies(discrepancy_df)
                self.account_discrepancy_df = discrepancy_df

                # Switch to comparison tab
                self.tab_widget.setCurrentIndex(2)
                
                # Update status
                self.status_bar.showMessage(
                    f"Comparison complete. Compared {len(success_sheets)} sheets "
                    f"({len(error_sheets)} errors, {len(skipped_sheets)} skipped)."
                )
            else:
                QMessageBox.warning(self, "Comparison Failed", 
                    "No sheets could be successfully compared. Please check that the Excel data and SQL results have compatible columns.")
                self.status_bar.showMessage("Comparison failed - no sheets could be compared.")
                
        except Exception as e:
            self.logger.error(f"Comparison error: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Comparison Error", f"An error occurred during comparison: {str(e)}")
            
        finally:
            if progress:
                progress.close()
            
        # Store comparison results for export
        self.comparison_results_by_sheet = comparison_results_by_sheet
    
    def _select_sheets_for_comparison(self, available_sheets):
        """Show a dialog to select sheets for comparison"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QLabel, QAbstractItemView, QComboBox, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Sheets to Compare")
        dialog.setMinimumSize(400, 300)
        
        # Use application theme for styling
        
        layout = QVBoxLayout(dialog)
        
        # Add scope selector
        scope_layout = QHBoxLayout()
        scope_label = QLabel("Comparison Scope:")
        scope_selector = QComboBox()
        scope_selector.addItems(["Current Sheet", "All Sheets"])
        scope_layout.addWidget(scope_label)
        scope_layout.addWidget(scope_selector)
        layout.addLayout(scope_layout)
        
        # Add instruction label
        instruction = QLabel("Select one or more sheets to compare (Ctrl+click for multiple):")
        layout.addWidget(instruction)
        
        # Create list widget for sheet selection
        sheet_list = QListWidget()
        sheet_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        for sheet in available_sheets:
            sheet_list.addItem(sheet)
            
        # Pre-select the current sheet
        current_sheet = self.sheet_selector.currentText()
        for i in range(sheet_list.count()):
            if sheet_list.item(i).text() == current_sheet:
                sheet_list.item(i).setSelected(True)
                break
                
        layout.addWidget(sheet_list)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Function to handle scope selection changes
        def on_scope_changed(text):
            if text == "All Sheets":
                # Select all sheets
                for i in range(sheet_list.count()):
                    sheet_list.item(i).setSelected(True)
            else:
                # Select only current sheet
                for i in range(sheet_list.count()):
                    sheet_list.item(i).setSelected(sheet_list.item(i).text() == current_sheet)
            sheet_list.setEnabled(text == "All Sheets")

        # Connect scope selector signal
        scope_selector.currentTextChanged.connect(on_scope_changed)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return [item.text() for item in sheet_list.selectedItems()]
        return []
            
    def _generate_combined_comparison_report(self, comparison_results_by_sheet, success_sheets, error_sheets, skipped_sheets):
        """Generate a comprehensive executive-friendly report from multiple sheet comparisons"""
        # Calculate overall statistics
        total_cells = 0
        total_mismatches = 0
        mismatch_sheets = []
        match_sheets = []
        discrepancy_frames = []

        for sheet_name, results in comparison_results_by_sheet.items():
            summary = results.get("summary", {})
            total_cells += summary.get("total_cells", 0)
            total_mismatches += summary.get("mismatch_cells", 0)
            
            if summary.get("overall_match", False):
                match_sheets.append(sheet_name)
            else:
                mismatch_percentage = summary.get("mismatch_percentage", 0)
                mismatch_sheets.append((sheet_name, mismatch_percentage))

            df = results.get("account_discrepancies")
            if isinstance(df, pd.DataFrame) and not df.empty:
                explanations = self.comparison_engine.explain_variances(df)
                df = df.copy()
                df["Explanation"] = explanations
                tmp = df[["Center", "Account", "Variance", "Missing in Excel", "Missing in SQL", "Explanation"]].copy()
                tmp.insert(0, "Sheet", sheet_name)
                discrepancy_frames.append(tmp)
        
        # Sort mismatch sheets by percentage (highest first)
        mismatch_sheets.sort(key=lambda x: x[1], reverse=True)
        
        # Calculate overall mismatch percentage
        overall_mismatch_pct = (total_mismatches / total_cells) * 100 if total_cells > 0 else 0
        overall_match = overall_mismatch_pct < 1.0  # Using 1% as threshold for overall match
        
        # Start building the report
        report = []
        
        # Executive summary header with status indicator
        if overall_mismatch_pct == 0:
            status = "✅ PERFECT MATCH"
        elif overall_mismatch_pct < 1:
            status = "✅ GOOD MATCH"
        elif overall_mismatch_pct < 5:
            status = "⚠️ MODERATE MISMATCH"
        else:
            status = "❌ SIGNIFICANT MISMATCH"
        
        report.append("# SOO PreClose Comparison Report")
        report.append(f"\n## Executive Summary: {status}")
        
        # Key statistics in a clean format
        report.append("\n### Key Statistics")
        report.append(f"\n- **Match Rate:** {100 - overall_mismatch_pct:.2f}%")
        report.append(f"- **Sheets Compared:** {len(success_sheets)}")
        report.append(f"- **Matching Sheets:** {len(match_sheets)}")
        report.append(f"- **Mismatched Sheets:** {len(mismatch_sheets)}")
        report.append(f"- **Error Sheets:** {len(error_sheets)}")
        report.append(f"- **Skipped Sheets:** {len(skipped_sheets)}")
        report.append(f"- **Total Cells Compared:** {total_cells:,}")
        report.append(f"- **Total Mismatches:** {total_mismatches:,}")
        
        # Mismatch summary - list sheets from worst to best
        if mismatch_sheets:
            report.append("\n### Sheets with Mismatches")
            report.append("\n| Sheet | Mismatch % | Status |")
            report.append("| ----- | ---------- | ------ |")
            
            for sheet_name, mismatch_pct in mismatch_sheets:
                # Add status indicator for each sheet
                if mismatch_pct >= 5:
                    sheet_status = "❌ High"
                elif mismatch_pct >= 1:
                    sheet_status = "⚠️ Medium"
                else:
                    sheet_status = "✅ Low"
                    
                report.append(f"| {sheet_name} | {mismatch_pct:.2f}% | {sheet_status} |")
        
        # Add error sheet details
        if error_sheets:
            report.append("\n### Error Sheets")
            for sheet in error_sheets:
                report.append(f"- {sheet}")
                
        # Add skipped sheet details if any
        if skipped_sheets:
            report.append("\n### Skipped Sheets")
            for sheet in skipped_sheets:
                report.append(f"- {sheet}")

        discrepancy_df = pd.concat(discrepancy_frames, ignore_index=True) if discrepancy_frames else pd.DataFrame()
        if not discrepancy_df.empty:
            report.append("\n## Account Discrepancies")
            report.append("\n| Sheet | Center | Account | Variance | Missing in Excel | Missing in SQL | Explanation |")
            report.append("| ----- | ------ | ------- | -------- | --------------- | -------------- | ----------- |")
            for _, row in discrepancy_df.iterrows():
                report.append(
                    f"| {row['Sheet']} | {row['Center']} | {row['Account']} | {row['Variance']:.2f} | {row['Missing in Excel']} | {row['Missing in SQL']} | {row['Explanation']} |"
                )
        else:
            discrepancy_df = pd.DataFrame(columns=["Sheet", "Center", "Account", "Variance", "Missing in Excel", "Missing in SQL"])

        # Detailed sheet-by-sheet analysis
        report.append(f"\n## Sheet-by-Sheet Analysis")
        
        # Focus first on sheets with problems (from worst to best)
        for sheet_name, mismatch_pct in mismatch_sheets:
            results = comparison_results_by_sheet[sheet_name]
            summary = results["summary"]
            
            report.append(f"\n### {sheet_name} ({mismatch_pct:.2f}% mismatch)")
            
            # Data coverage
            excel_rows = results["row_counts"]["excel"]
            sql_rows = results["row_counts"]["sql"]
            matched_rows = results["row_counts"]["matched"]
            excel_only = excel_rows - matched_rows
            sql_only = sql_rows - matched_rows
            
            report.append("\n#### Data Coverage")
            report.append(f"- Excel records: {excel_rows}")
            report.append(f"- SQL records: {sql_rows}")
            report.append(f"- Matched records: {matched_rows}")

            if excel_only > 0 or sql_only > 0:
                if excel_only > 0:
                    report.append(f"- Excel-only records: {excel_only}")
                if sql_only > 0:
                    report.append(f"- SQL-only records: {sql_only}")

            # Suggested sign flip accounts for this sheet
            suggested = results.get("suggested_sign_flips")
            if suggested:
                report.append("\n#### Suggested Sign-Flip Accounts")
                for acct in sorted(suggested):
                    report.append(f"- {acct}")
            
            # Problem columns with highest mismatch rates
            column_stats = []
            for excel_col, col_results in results.get("column_comparisons", {}).items():
                # Skip columns with no mismatches
                if col_results.get("mismatch_count", 0) == 0:
                    continue
                
                total_col_cells = col_results.get("match_count", 0) + col_results.get("mismatch_count", 0)
                mismatch_pct = col_results.get("mismatch_count", 0) / total_col_cells * 100 if total_col_cells > 0 else 0
                
                column_stats.append({
                    "column": excel_col,
                    "mismatch_count": col_results.get("mismatch_count", 0),
                    "mismatch_percentage": mismatch_pct
                })
            
            # Sort columns by mismatch percentage
            column_stats.sort(key=lambda x: x["mismatch_percentage"], reverse=True)
            
            if column_stats:
                report.append("\n#### Problem Columns")
                report.append("\n| Column | Mismatch Count | Mismatch % |")
                report.append("| ------ | -------------- | ---------- |")
                
                # Show top 5 problem columns
                for stat in column_stats[:5]:
                    report.append(f"| {stat['column']} | {stat['mismatch_count']} | {stat['mismatch_percentage']:.2f}% |")
                
                if len(column_stats) > 5:
                    report.append(f"\n*...and {len(column_stats) - 5} more columns with mismatches.*")
            
            # Sample mismatches from this sheet
            all_mismatches = []
            for excel_col, col_results in results.get("column_comparisons", {}).items():
                for mismatch in col_results.get("mismatch_rows", []):
                    mismatch_with_col = mismatch.copy()
                    mismatch_with_col["column"] = excel_col
                    all_mismatches.append(mismatch_with_col)
            
            if all_mismatches:
                report.append("\n#### Sample Mismatches")
                report.append("\n| Row | Column | Excel Value | SQL Value | Difference |")
                report.append("| --- | ------ | ----------- | --------- | ---------- |")
                
                # Sort by row for consistent display
                all_mismatches.sort(key=lambda x: x["row"])
                
                # Show up to 10 mismatches per sheet
                for mismatch in all_mismatches[:10]:
                    excel_val = str(mismatch["excel_value"]).replace("|", "\\|")
                    sql_val = str(mismatch["sql_value"]).replace("|", "\\|")
                    diff = str(mismatch["difference"]).replace("|", "\\|")
                    report.append(f"| {mismatch['row']} | {mismatch['column']} | {excel_val} | {sql_val} | {diff} |")
                
                if len(all_mismatches) > 10:
                    report.append(f"\n*...and {len(all_mismatches) - 10} more mismatches in this sheet.*")

            # Add discrepancy explanations for this sheet
            disc_df = results.get("account_discrepancies")
            messages = self.comparison_engine.explain_variances(disc_df)
            if messages:
                report.append("\n#### Discrepancies")
                for msg in messages:
                    report.append(f"- {msg}")

        # Add matching sheets section (brief)
        if match_sheets:
            report.append("\n## Perfect Match Sheets")
            report.append("\nThe following sheets had perfect or near-perfect matches (< 1% mismatch):")
            report.append("\n| Sheet | Status |")
            report.append("| ----- | ------ |")
            
            for sheet in match_sheets:
                report.append(f"| {sheet} | ✅ Perfect Match |")
        
        return "\n".join(report), discrepancy_df
    
    def export_report(self):
        """Export the comparison report to a file"""
        if not self.comparison_view.has_report():
            QMessageBox.warning(self, "No Report", "Please generate a comparison report first.")
            return
            
        # Get the last directory used
        last_file = self.config.get("paths", "last_excel_file")
        start_dir = os.path.dirname(last_file) if last_file else os.path.expanduser("~")
        
        # Show file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Comparison Report", start_dir, 
            "Markdown Files (*.md);;HTML Files (*.html);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if not file_path:
            return
            
        try:
            # Get report content
            report_content = self.comparison_view.get_report()
            
            # Export according to chosen format
            if file_path.lower().endswith('.html'):
                # Convert markdown to HTML
                import markdown
                html_content = markdown.markdown(report_content)
                
                # Add basic styling
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Comparison Report</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; }}
                        th {{ background-color: #f2f2f2; }}
                        tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    </style>
                </head>
                <body>
                {html_content}
                </body>
                </html>
                """
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            else:
                # Plain text or markdown
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
            
            self.status_bar.showMessage(f"Exported report to: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred when exporting the report: {str(e)}")
    
    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            # Settings were updated, reconnect to database if needed
            if self.db_connector:
                self.disconnect_database()
                self.connect_to_database()
                
            # Update comparison tolerance if needed
            if self.comparison_engine:
                tolerance = self.config.get("excel", "numerical_comparison_tolerance")
                self.comparison_engine.set_tolerance(tolerance)
                
            # Apply updated theme
            self.apply_theme()
            self.status_bar.showMessage("Settings updated")

    def open_account_categories(self):
        """Open the account categories dialog for the current report."""
        report_type = self.report_selector.currentText()
        accounts = self._gather_accounts_from_excel()
        dialog = AccountCategoryDialog(self.config, report_type, accounts, self)
        if dialog.exec():
            self.status_bar.showMessage("Account categories updated")

    def _gather_accounts_from_excel(self):
        """Extract account numbers from loaded Excel sheets."""
        if not getattr(self, "excel_analyzer", None):
            return []

        patterns = [
            r"(\d{4}-?\d{4})",
            r"(\d{5}-?\d{3})",
            r"(\d{3}-?\d{5})",
            r"(\d{4}-?\d{5})",
            r"(\d{7,8})",
        ]
        accounts = set()
        try:
            for sheet in self.excel_analyzer.sheet_names:
                if sheet not in self.excel_analyzer.sheet_data:
                    self.excel_analyzer.analyze_sheet(sheet)

                sheet_info = self.excel_analyzer.sheet_data[sheet]
                df = sheet_info["dataframe"]

                # If the dataframe has numeric column names, rebuild headers
                cols_are_numeric = all(
                    isinstance(c, (int, float)) or str(c).isdigit() for c in df.columns
                )
                if cols_are_numeric:
                    headers = None
                    header_rows = sheet_info.get("header_indexes") or []
                    if header_rows:
                        header_row = max(header_rows)
                        headers = [str(v).strip() for v in df.iloc[header_row].tolist()]
                        df = df.iloc[header_row + 1 :].copy()
                    elif "cleaned_dataframe" in sheet_info:
                        df = sheet_info["cleaned_dataframe"].copy()
                        headers = list(df.columns)

                    if headers:
                        df.columns = headers

                for col in df.columns:
                    col_name = str(col).strip()
                    if (
                        "account" in col_name.lower()
                        or "careportname" in col_name.lower()
                    ):
                        col_data = df[col].astype(str)
                        for val in col_data:
                            for pat in patterns:
                                accounts.update(re.findall(pat, val))
        except Exception as e:
            self.logger.error(f"Failed to extract accounts: {e}")

        return sorted(accounts)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About SOO PreClose Report Tester",
            """<h1>SOO PreClose Report Tester</h1>
            <p>Version 1.0.0</p>
            <p>A high-quality application for testing Excel reports against SQL databases.</p>
            <p>Features:</p>
            <ul>
                <li>Smart Excel parsing and analysis</li>
                <li>SQL query generation and execution</li>
                <li>Detailed comparison between Excel and SQL data</li>
                <li>Support for all Excel sheets and formats</li>
                <li>Intelligent data matching algorithms</li>
            </ul>
            <p>&copy; 2023 Your Organization</p>
            """
        )
    
    def load_last_session(self):
        """Load the last session if enabled"""
        # Load last Excel file if exists
        last_excel = self.config.get("paths", "last_excel_file")
        if last_excel and os.path.exists(last_excel):
            self.load_excel_file(last_excel)
            
        # Load last SQL file if exists
        last_sql = self.config.get("paths", "last_sql_file")
        if last_sql and os.path.exists(last_sql):
            self.load_sql_file(last_sql)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Disconnect from database
        if self.db_connector:
            self.db_connector.close()
            
        # Save any pending settings
        self.config.save_config()
        
        event.accept()

    def report_type_changed(self, index):
        """Handle report type selection change"""
        if index < 0:
            return
            
        report_type = self.report_selector.currentText()
        self.logger.info(f"Selected report type: {report_type}")
        
        # Save the selected report type in config
        self.config.set("excel", "report_type", report_type)
        
        # Update the status bar
        self.status_bar.showMessage(f"Selected report type: {report_type}")
        
        # If we have an excel file loaded, notify the user about cleaning settings
        if self.excel_analyzer:
            QMessageBox.information(self, "Report Type Changed", 
                f"Report type changed to '{report_type}'. " 
                f"The sheet cleaning parameters will be adjusted for this report type.")
            
        # Update any components that need to know about the report type
        self.update_components_for_report_type(report_type)

    def initialize_report_configs(self):
        """Initialize configurations for different report types"""
        configs = {
            "SOO PreClose": {
                "header_rows": [5, 6],  # Rows 6 and 7 (0-indexed as 5 and 6)
                "skip_rows": 7,         # Skip rows 0-6 (header is at 5-6)
                "description": "SOO PreClose report with headers on rows 6 and 7"
            },
            "SOO MFR": {
                "header_rows": [3, 4],  # Rows 4 and 5 (0-indexed as 3 and 4)
                "skip_rows": 5,         # Skip rows 0-4
                "description": "SOO MFR report with headers on rows 4 and 5"
            },
            "Executive Book": {
                "header_rows": [2, 3],  # Rows 3 and 4 (0-indexed as 2 and 3)
                "skip_rows": 4,         # Skip rows 0-3
                "description": "Executive Book report with headers on rows 3 and 4"
            },
            "Statement of Operations": {
                "header_rows": [4, 5],  # Rows 5 and 6 (0-indexed as 4 and 5)
                "skip_rows": 6,         # Skip rows 0-5
                "description": "Statement of Operations report with headers on rows 5 and 6"
            },
            "Corp SOO": {
                "header_rows": [5, 6],  # Rows 6 and 7 (0-indexed as 5 and 6)
                "skip_rows": 7,         # Skip rows 0-6
                "description": "Corporate SOO report with headers on rows 6 and 7"
            },
            "AR Center": {
                "header_rows": [4, 5],  # Rows 5 and 6 (0-indexed as 4 and 5)
                "skip_rows": 6,         # Skip rows 0-5
                "description": "AR Center report with headers on rows 5 and 6"
            }
        }
        return configs
        
    def update_components_for_report_type(self, report_type):
        """Update application components based on the selected report type"""
        if report_type not in self.report_configs:
            self.logger.warning(f"Unknown report type: {report_type}")
            return
            
        # Get the report configuration
        report_config = self.report_configs[report_type]
        
        # Update Excel viewer with the report configuration
        if hasattr(self, 'excel_viewer'):
            self.excel_viewer.set_report_config(report_config)
            
        # If we have an Excel analyzer, update its configuration as well
        if self.excel_analyzer:
            # We will need to extend ExcelAnalyzer to handle report configurations
            # For now, log that we would need to update it
            self.logger.info(f"Would update ExcelAnalyzer with {report_type} configuration")
            
        # Log the configuration being used
        self.logger.info(f"Using report configuration for {report_type}: {report_config}")
        
        # Set this in the application-wide configuration
        self.config.set("excel", "current_report_config", report_config)

    def reset_application(self):
        """Reset the application state to start a new test:
        1. Clear Excel data and reset Excel viewer
        2. Clear SQL editor and results viewer 
        3. Clear comparison view
        4. Keep database connection and app settings
        """
        try:
            # Confirm with user before resetting
            from PyQt6.QtWidgets import QMessageBox
            response = QMessageBox.question(
                self, 
                "Reset Application", 
                "This will clear all loaded data. Do you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if response != QMessageBox.StandardButton.Yes:
                return
                
            # Reset Excel analyzer and viewer
            self.excel_analyzer = None
            self.excel_viewer.reset()
            self.excel_status_label.setText("Excel: No file loaded")
            
            # Reset sheet selector
            self.sheet_selector.clear()
            
            # Reset SQL editor
            self.sql_editor.clear_text()
            
            # Reset results viewer
            self.results_viewer.clear_results()
            
            # Reset comparison view
            self.comparison_view.clear_report()
            
            # Reset comparison engine
            self.comparison_engine = None
            
            # Switch to first tab
            self.tab_widget.setCurrentIndex(0)
            
            # Update status
            self.status_bar.showMessage("Application reset complete")
            
        except Exception as e:
            QMessageBox.critical(self, "Reset Error", f"An error occurred during reset: {str(e)}")
            self.logger.error(f"Reset error: {str(e)}", exc_info=True)

    def export_detailed_results(self):
        """Export detailed comparison results to Excel"""
        import pandas as pd
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import os
        # Check if comparison results exist
        if not hasattr(self, 'comparison_engine') or not hasattr(self, 'excel_analyzer'):
            QMessageBox.warning(self, "No Results", "Please run a comparison first.")
            return
        if not hasattr(self, 'comparison_results_by_sheet') or not self.comparison_results_by_sheet:
            QMessageBox.warning(self, "No Results", "Please run a comparison first.")
            return
        # Combine detailed results from all sheets
        all_dfs = []
        for sheet_name, result in self.comparison_results_by_sheet.items():
            # Get the original dataframes
            excel_df = self.excel_analyzer.sheet_data[sheet_name]["dataframe"]
            # For SQL, filter as in compare_results
            sql_df = self.results_viewer.get_dataframe()
            key_cols = []
            for col in ["Center", "CAReportName", "Account", "Sheet_Name"]:
                if col in excel_df.columns and col in sql_df.columns:
                    key_cols.append(col)
            filtered_sql_df = sql_df.copy()
            if key_cols:
                for col in key_cols:
                    excel_vals = excel_df[col].dropna().unique()
                    filtered_sql_df = filtered_sql_df[filtered_sql_df[col].isin(excel_vals)]

            # Apply account categories and formulas to SQL rows before comparison
            report_type = self.report_selector.currentText()
            categories = self.config.get_account_categories(report_type)
            formulas = self.config.get_account_formulas(report_type)
            if categories:
                from src.utils.account_categories import CategoryCalculator
                calc = CategoryCalculator(categories, formulas)
                sql_rows = filtered_sql_df.to_dict(orient="records")
                filtered_sql_df = pd.DataFrame(calc.compute(sql_rows))

            # Generate detailed DataFrame
            df = self.comparison_engine.generate_detailed_comparison_dataframe(sheet_name, excel_df, filtered_sql_df)
            all_dfs.append(df)
        if not all_dfs:
            QMessageBox.warning(self, "No Data", "No detailed results to export.")
            return
        combined_df = pd.concat(all_dfs, ignore_index=True)
        # Default filename
        excel_path = self.config.get("paths", "last_excel_file")
        if excel_path:
            base = os.path.splitext(os.path.basename(excel_path))[0]
            default_name = f"{base}_results.xlsx"
        else:
            default_name = "comparison_results.xlsx"
        # File dialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Results", default_name, "Excel Files (*.xlsx)")
        if not file_path:
            return
        try:
            combined_df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Export Successful", f"Results exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export results: {str(e)}")

    def export_pdf_report(self):
        """Export a high-quality PDF report of the comparison results"""
        import pandas as pd
        import subprocess
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import os
        import shutil

        # Gather results as in export_detailed_results
        if not hasattr(self, 'comparison_engine') or not hasattr(self, 'excel_analyzer'):
            QMessageBox.warning(self, "No Results", "Please run a comparison first.")
            return
        if not hasattr(self, 'comparison_results_by_sheet') or not self.comparison_results_by_sheet:
            QMessageBox.warning(self, "No Results", "Please run a comparison first.")
            return

        all_dfs = []
        for sheet_name, result in self.comparison_results_by_sheet.items():
            excel_df = self.excel_analyzer.sheet_data[sheet_name]["dataframe"]
            sql_df = self.results_viewer.get_dataframe()
            key_cols = []
            for col in ["Center", "CAReportName", "Account", "Sheet_Name"]:
                if col in excel_df.columns and col in sql_df.columns:
                    key_cols.append(col)
            filtered_sql_df = sql_df.copy()
            if key_cols:
                for col in key_cols:
                    excel_vals = excel_df[col].dropna().unique()
                    filtered_sql_df = filtered_sql_df[filtered_sql_df[col].isin(excel_vals)]
            df = self.comparison_engine.generate_detailed_comparison_dataframe(sheet_name, excel_df, filtered_sql_df)
            all_dfs.append(df)
        if not all_dfs:
            QMessageBox.warning(self, "No Data", "No detailed results to export.")
            return
        combined_df = pd.concat(all_dfs, ignore_index=True)

        # Save to results.csv in the reporting directory
        reporting_dir = os.path.join(os.path.dirname(__file__), '..', 'reporting')
        results_csv = os.path.join(reporting_dir, 'results.csv')
        combined_df.to_csv(results_csv, index=False)

        # Run the PDF report generator
        script_path = os.path.join(reporting_dir, 'generate_pdf_report.py')
        try:
            subprocess.run(['python', script_path], check=True)
            pdf_path = os.path.join(reporting_dir, 'SOO_Preclose_Report.pdf')
            # Ask user where to save the PDF
            file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "SOO_Preclose_Report.pdf", "PDF Files (*.pdf)")
            if file_path:
                shutil.copy(pdf_path, file_path)
                QMessageBox.information(self, "Export Successful", f"PDF report exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to generate PDF report: {str(e)}")

    def update_button_states(self, has_data):
        self.export_pdf_button.setEnabled(has_data)

    def apply_theme(self):
        """Apply application-wide stylesheet based on configuration"""
        theme = self.config.get("ui", "theme")
        if not theme or theme.lower() == "system":
            QApplication.instance().setStyleSheet("")
            theme = "system"

        themes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "themes")
        if theme.lower() == "brand":
            theme_file = os.path.join(themes_dir, "brand.qss")
        else:
            theme_file = os.path.join(themes_dir, f"{theme.lower()}.qss")
        if os.path.exists(theme_file):
            with open(theme_file, "r", encoding="utf-8") as f:
                QApplication.instance().setStyleSheet(f.read())
        else:
            QApplication.instance().setStyleSheet("")

        # Propagate theme to child widgets
        for widget in [getattr(self, attr, None) for attr in [
            "excel_viewer", "sql_editor", "results_viewer"]]:
            if widget and hasattr(widget, "apply_widget_theme"):
                widget.apply_widget_theme(theme)
