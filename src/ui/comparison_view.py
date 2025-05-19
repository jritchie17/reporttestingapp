from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QLabel, QPushButton, QTextEdit, QTabWidget,
                             QTableView, QHeaderView, QGridLayout, QToolBar,
                             QApplication)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt6.QtGui import QFont, QColor, QBrush, QTextCharFormat, QAction
import markdown
import qtawesome as qta


class MarkdownView(QTextEdit):
    """A widget for rendering Markdown content"""
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        
    def set_markdown(self, markdown_text):
        """Set Markdown content and render as HTML"""
        html = markdown.markdown(markdown_text)
        
        # Add custom styling
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 10px; }}
                h1 {{ color: #0066cc; font-size: 20px; }}
                h2 {{ color: #333366; font-size: 16px; margin-top: 20px; }}
                h3 {{ font-size: 14px; margin-top: 15px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; text-align: left; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        self.setHtml(styled_html)


class ComparisonView(QWidget):
    def __init__(self):
        super().__init__()
        self.report_content = ""
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        
        # Create toolbar area
        self.create_toolbar(main_layout)
        
        # Create tabbed view for different comparison visualizations
        self.tab_widget = QTabWidget()
        
        # Report tab (markdown view)
        self.report_view = MarkdownView()
        self.tab_widget.addTab(self.report_view, "Report")
        
        # Summary tab
        self.summary_tab = QWidget()
        summary_layout = QVBoxLayout(self.summary_tab)
        
        self.summary_header = QLabel("No comparison data available")
        self.summary_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        summary_layout.addWidget(self.summary_header)
        
        self.summary_content = QLabel()
        self.summary_content.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.summary_content.setWordWrap(True)
        summary_layout.addWidget(self.summary_content)
        
        self.tab_widget.addTab(self.summary_tab, "Summary")
        
        main_layout.addWidget(self.tab_widget)
        
    def create_toolbar(self, main_layout):
        """Create toolbar with analysis actions"""
        toolbar = QToolBar()
        
        # Export report action
        export_action = QAction(qta.icon('fa5s.file-export'), "Export Report", self)
        export_action.triggered.connect(self.export_report)
        toolbar.addAction(export_action)
        
        # Copy report action
        copy_action = QAction(qta.icon('fa5s.copy'), "Copy Report", self)
        copy_action.triggered.connect(self.copy_report)
        toolbar.addAction(copy_action)
        
        # Print report action
        print_action = QAction(qta.icon('fa5s.print'), "Print Report", self)
        print_action.triggered.connect(self.print_report)
        toolbar.addAction(print_action)
        
        main_layout.addWidget(toolbar)
        
    def set_report(self, report_content):
        """Set the report content and update views"""
        if not report_content:
            return
            
        self.report_content = report_content
        
        # Update markdown view
        self.report_view.set_markdown(report_content)
        
        # Update summary view
        self.update_summary_from_report(report_content)
        
        # Switch to first tab
        self.tab_widget.setCurrentIndex(0)
        
    def update_summary_from_report(self, report_content):
        """Parse report content to update summary view"""
        if not report_content:
            return
            
        # Extract simple summary from the report
        # This is a very basic version - in a real app, this would be more sophisticated
        
        # Extract report title
        title_lines = [line for line in report_content.split('\n') if line.startswith('# ')]
        title = title_lines[0].replace('# ', '') if title_lines else "Comparison Report"
        self.summary_header.setText(title)
        
        # Extract summary section
        summary_section = ""
        in_summary = False
        for line in report_content.split('\n'):
            if line.startswith('## Summary'):
                in_summary = True
                continue
                
            if in_summary and line.startswith('## '):
                break
                
            if in_summary and line.strip():
                summary_section += line + "\n"
                
        # Format summary content as rich text
        if summary_section:
            # Convert result to rich text format
            summary_rich = ""
            for line in summary_section.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    summary_rich += f"<b>{key}:</b> {value}<br>"
                else:
                    summary_rich += line + "<br>"
                    
            self.summary_content.setText(summary_rich)
        else:
            self.summary_content.setText("No summary information available.")
            
    def export_report(self):
        """Export report to a file (implemented in MainWindow)"""
        # This is a signal that will be connected in MainWindow
        pass
        
    def copy_report(self):
        """Copy report content to clipboard"""
        if self.report_content:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.report_content)
        
    def print_report(self):
        """Print the report"""
        if not self.report_content:
            return
            
        from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
        
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            # Use the current tab's widget for printing
            current_tab = self.tab_widget.currentIndex()
            
            if current_tab == 0:  # Report tab
                self.report_view.print_(printer)
            else:
                # For other tabs, print the report anyway
                self.report_view.print_(printer)
                
    def has_report(self):
        """Check if a report is loaded"""
        return bool(self.report_content)
        
    def clear_report(self):
        """Clear the current report content"""
        self.report_content = ""
        self.report_view.setHtml("")
        self.summary_header.setText("No comparison data available")
        self.summary_content.setText("")
        
    def get_report(self):
        """Get the current report content"""
        return self.report_content