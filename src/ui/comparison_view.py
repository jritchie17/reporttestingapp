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
        """Parse report content and update the summary view."""
        if not report_content:
            return

        lines = report_content.splitlines()

        # --- Extract title ---
        title = next((ln[2:] for ln in lines if ln.startswith('# ')), "Comparison Report")

        # --- Extract status from the executive summary header ---
        status_line = next((ln for ln in lines if ln.startswith('## Executive Summary')), None)
        status = ""
        if status_line and ':' in status_line:
            status = status_line.split(':', 1)[1].strip()

        header_text = title if not status else f"{title} - {status}"
        self.summary_header.setText(header_text)

        # --- Extract key statistics list ---
        summary_items = []
        try:
            stats_index = lines.index('### Key Statistics')
            for ln in lines[stats_index + 1:]:
                if ln.startswith('### ') or ln.startswith('## '):
                    break
                if ln.startswith('- '):
                    item = ln[2:].strip().replace('**', '')
                    summary_items.append(item)
        except ValueError:
            pass

        # --- Extract suggested sign flip accounts ---
        suggested_accounts = []
        for idx, ln in enumerate(lines):
            if ln.startswith('**Suggested Sign Flip Accounts:**'):
                acct_str = ln.split(':', 1)[1].strip()
                suggested_accounts = [a.strip() for a in acct_str.split(',') if a.strip()]
                break
            if ln.strip() == '#### Suggested Sign-Flip Accounts':
                for sub in lines[idx + 1:]:
                    if not sub.startswith('- '):
                        break
                    suggested_accounts.append(sub[2:].strip())
                break

        parts = []
        if summary_items:
            parts.append('<ul>' + ''.join(f'<li>{item}</li>' for item in summary_items) + '</ul>')
        if suggested_accounts:
            parts.append('<p><b>Suggested Sign-Flip Accounts:</b> ' + ', '.join(suggested_accounts) + '</p>')

        if parts:
            self.summary_content.setText(''.join(parts))
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
