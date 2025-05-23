from PyQt6.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QLabel


class WorkflowWizard(QWizard):
    """Wizard to run the full data comparison workflow."""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.setWindowTitle("Workflow Wizard")

        # Define steps as (title, callable)
        self.steps = [
            ("Load Excel", self.main_window.open_excel_file),
            ("Clean Sheets", self._clean_sheets),
            ("Load SQL", self.main_window.open_sql_file),
            ("Extract SQL Codes", self._extract_sql_codes),
            ("Execute SQL", self.main_window.execute_sql),
            ("Import SQL Headers", self._import_headers),
            ("Compare Data", self.main_window.compare_results),
        ]

        for title, _ in self.steps:
            page = QWizardPage()
            page.setTitle(title)
            layout = QVBoxLayout()
            layout.addWidget(QLabel(title))
            page.setLayout(layout)
            self.addPage(page)

    # Helper actions that reference the excel viewer
    def _clean_sheets(self):
        viewer = getattr(self.main_window, "excel_viewer", None)
        if viewer and hasattr(viewer, "clean_data"):
            viewer.clean_data()

    def _extract_sql_codes(self):
        viewer = getattr(self.main_window, "excel_viewer", None)
        if viewer and hasattr(viewer, "extract_sql_codes"):
            viewer.extract_sql_codes()

    def _import_headers(self):
        viewer = getattr(self.main_window, "excel_viewer", None)
        if viewer and hasattr(viewer, "import_column_headers"):
            viewer.import_column_headers()

    def start(self):
        """Execute all steps sequentially."""
        for _, action in self.steps:
            try:
                if callable(action):
                    action()
            except Exception:
                pass

        # Show comparison results
        if hasattr(self.main_window, "tab_widget"):
            self.main_window.tab_widget.setCurrentIndex(2)

        self.finished.emit(0)


