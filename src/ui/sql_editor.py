from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QToolBar,
    QMenu,
    QSplitter,
    QToolButton,
    QFrame,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QFormLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QTextCharFormat, QBrush, QSyntaxHighlighter, QTextCursor, QAction, QIcon
import re
import qtawesome as qta
from src.ui.hover_anim_filter import HoverAnimationFilter

class SQLSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for SQL code"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # SQL keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QBrush(QColor("#0000FF")))
        keyword_format.setFontWeight(700)
        
        keywords = [
            "\\bSELECT\\b", "\\bFROM\\b", "\\bWHERE\\b", "\\bAND\\b", "\\bOR\\b",
            "\\bINNER\\b", "\\bOUTER\\b", "\\bLEFT\\b", "\\bRIGHT\\b", "\\bJOIN\\b",
            "\\bON\\b", "\\bGROUP\\b", "\\bBY\\b", "\\bORDER\\b", "\\bHAVING\\b",
            "\\bDISTINCT\\b", "\\bUNION\\b", "\\bINSERT\\b", "\\bUPDATE\\b", "\\bDELETE\\b",
            "\\bINTO\\b", "\\bVALUES\\b", "\\bSET\\b", "\\bCREATE\\b", "\\bALTER\\b",
            "\\bDROP\\b", "\\bTABLE\\b", "\\bINDEX\\b", "\\bVIEW\\b", "\\bPROCEDURE\\b",
            "\\bFUNCTION\\b", "\\bTRIGGER\\b", "\\bIS\\b", "\\bNULL\\b", "\\bNOT\\b",
            "\\bPRIMARY\\b", "\\bKEY\\b", "\\bFOREIGN\\b", "\\bREFERENCES\\b", "\\bCONSTRAINT\\b",
            "\\bDEFAULT\\b", "\\bCASCADE\\b", "\\bAUTO_INCREMENT\\b", "\\bUNIQUE\\b", "\\bINDEX\\b",
            "\\bCHECK\\b", "\\bTEMP\\b", "\\bTEMPORARY\\b", "\\bIF\\b", "\\bEXISTS\\b",
            "\\bCASE\\b", "\\bWHEN\\b", "\\bTHEN\\b", "\\bELSE\\b", "\\bEND\\b", 
            "\\bLIKE\\b", "\\bIN\\b", "\\bBETWEEN\\b", "\\bIS\\b", "\\bANY\\b", "\\bALL\\b",
            "\\bLIMIT\\b", "\\bOFFSET\\b", "\\bTOP\\b", "\\bAS\\b", "\\bWITH\\b"
        ]
        
        for pattern in keywords:
            rule = (re.compile(pattern, re.IGNORECASE), keyword_format)
            self.highlighting_rules.append(rule)
            
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QBrush(QColor("#FF00FF")))
        self.highlighting_rules.append((re.compile("\\b[0-9]+\\b"), number_format))
        
        # String literals
        string_format = QTextCharFormat()
        string_format.setForeground(QBrush(QColor("#008000")))
        self.highlighting_rules.append((re.compile("'[^']*'"), string_format))
        self.highlighting_rules.append((re.compile("\"[^\"]*\""), string_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QBrush(QColor("#808080")))
        self.highlighting_rules.append((re.compile("--[^\n]*"), comment_format))
        self.multiline_comment_start = re.compile("/\\*")
        self.multiline_comment_end = re.compile("\\*/")
        self.comment_format = comment_format
        
    def highlightBlock(self, text):
        # Apply regular expression highlighting rules
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)
                
        # Handle multi-line comments
        self.setCurrentBlockState(0)
        
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.multiline_comment_start.search(text)
            start_index = start_index.start() if start_index else -1
            
        while start_index >= 0:
            end_match = self.multiline_comment_end.search(text, start_index)
            
            if end_match:
                # End of comment found in this block
                comment_length = end_match.end() - start_index
                self.setFormat(start_index, comment_length, self.comment_format)
                start_index = self.multiline_comment_start.search(text, start_index + comment_length)
                start_index = start_index.start() if start_index else -1
            else:
                # Comment continues to next block
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
                self.setFormat(start_index, comment_length, self.comment_format)
                break


class SQLEditor(QWidget):
    executeRequested = pyqtSignal(str)  # Signal emitted when execution is requested
    
    def __init__(self):
        super().__init__()
        self.suggestions = []
        self.hover_filter = HoverAnimationFilter()
        self.init_ui()

    def _apply_hover_animation(self, widget):
        if widget:
            widget.installEventFilter(self.hover_filter)
        
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create toolbar area
        self.create_toolbar(main_layout)
        
        # Create main editor area
        self.editor_area = QSplitter(Qt.Orientation.Horizontal)
        
        # SQL editor
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Set up syntax highlighting
        self.highlighter = SQLSyntaxHighlighter(self.editor.document())
        
        # Add placeholder text
        self.editor.setPlaceholderText("Enter your SQL query here...")
        
        # Let the global theme handle widget styling
        self.setStyleSheet("")
        
        # Add editor to splitter
        self.editor_area.addWidget(self.editor)

        # Set initial size
        self.editor_area.setSizes([1])
        
        main_layout.addWidget(self.editor_area)
        
    def create_toolbar(self, main_layout):
        """Create toolbar with SQL editor actions"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        
        # Run SQL action
        run_action = QAction(qta.icon('fa5s.play'), "Execute SQL", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.execute_sql)
        toolbar.addAction(run_action)
        self._apply_hover_animation(toolbar.widgetForAction(run_action))
        
        # Format SQL action
        format_action = QAction(qta.icon('fa5s.align-left'), "Format SQL", self)
        format_action.triggered.connect(self.format_sql)
        toolbar.addAction(format_action)
        self._apply_hover_animation(toolbar.widgetForAction(format_action))
        
        # Clear action
        clear_action = QAction(qta.icon('fa5s.eraser'), "Clear Editor", self)
        clear_action.triggered.connect(self.clear_editor)
        toolbar.addAction(clear_action)
        self._apply_hover_animation(toolbar.widgetForAction(clear_action))
        
        # Add separator
        toolbar.addSeparator()
        
        # Common SQL snippets
        snippets_button = QToolButton()
        snippets_button.setText("Snippets")
        snippets_button.setIcon(qta.icon('fa5s.code'))
        snippets_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        snippets_menu = QMenu(self)
        
        # Add common SQL snippets
        select_action = QAction("SELECT * FROM", self)
        select_action.triggered.connect(lambda: self.insert_snippet("SELECT * FROM table_name"))
        snippets_menu.addAction(select_action)
        
        where_action = QAction("WHERE Clause", self)
        where_action.triggered.connect(lambda: self.insert_snippet("WHERE column_name = value"))
        snippets_menu.addAction(where_action)
        
        join_action = QAction("JOIN Clause", self)
        join_action.triggered.connect(lambda: self.insert_snippet("JOIN table_name ON table1.column = table2.column"))
        snippets_menu.addAction(join_action)
        
        group_action = QAction("GROUP BY Clause", self)
        group_action.triggered.connect(lambda: self.insert_snippet("GROUP BY column_name"))
        snippets_menu.addAction(group_action)
        
        snippets_button.setMenu(snippets_menu)
        toolbar.addWidget(snippets_button)
        self._apply_hover_animation(snippets_button)
        
        main_layout.addWidget(toolbar)
        
    def set_text(self, text):
        """Set the text in the editor"""
        self.editor.setPlainText(text)
        
    def get_text(self):
        """Get the text from the editor"""
        return self.editor.toPlainText()
        
    def execute_sql(self):
        """Execute the current SQL query"""
        sql_text = self.get_text()
        if sql_text.strip():
            self.executeRequested.emit(sql_text)
            
    def format_sql(self):
        """Format the SQL query for better readability"""
        sql_text = self.get_text()
        if not sql_text.strip():
            return
            
        # Very basic SQL formatting - in a real app, use a proper SQL formatter
        keywords = [
            "SELECT", "FROM", "WHERE", "AND", "OR", "JOIN", "LEFT JOIN", "RIGHT JOIN",
            "INNER JOIN", "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "OFFSET"
        ]
        
        # Capitalize keywords
        formatted_sql = sql_text
        for keyword in keywords:
            pattern = re.compile(r'\b' + keyword + r'\b', re.IGNORECASE)
            formatted_sql = pattern.sub(keyword, formatted_sql)
            
        # Add newlines after major clauses
        for keyword in ["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING"]:
            pattern = re.compile(r'\b' + keyword + r'\b', re.IGNORECASE)
            formatted_sql = pattern.sub('\n' + keyword, formatted_sql)
            
        # Add newlines and indentation for AND, OR
        for keyword in ["AND", "OR"]:
            pattern = re.compile(r'\b' + keyword + r'\b', re.IGNORECASE)
            formatted_sql = pattern.sub('\n    ' + keyword, formatted_sql)
            
        # Add newlines and indentation for JOINs
        for keyword in ["JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN"]:
            pattern = re.compile(r'\b' + keyword + r'\b', re.IGNORECASE)
            formatted_sql = pattern.sub('\n    ' + keyword, formatted_sql)
            
        # Update editor with formatted SQL
        self.set_text(formatted_sql.strip())
        
    def clear_editor(self):
        """Clear the editor"""
        self.editor.clear()
        
    def clear_text(self):
        """Clear the editor text (for app reset)"""
        self.editor.clear()
        self.suggestions = []
        
    def insert_snippet(self, snippet):
        """Insert a SQL snippet at the current cursor position"""
        cursor = self.editor.textCursor()
        cursor.insertText(snippet)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
        

            
    def has_content(self):
        """Check if the editor has content"""
        return bool(self.get_text().strip())

    def apply_widget_theme(self, theme: str):
        """Apply theme-specific styling to the SQL editor."""
        if theme and theme.lower() == "dark":
            qss = """
            QWidget {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            QTextEdit {
                background-color: #333333;
                color: #e0e0e0;
                border: 1px solid #555555;
                font-family: Consolas, monospace;
            }
            QLabel {
                color: #e0e0e0;
                background: transparent;
            }
            QPushButton {
                background-color: #3a6ea5;
                color: white;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #4a7eb5;
            }
            QComboBox {
                background-color: #333333;
                color: #e0e0e0;
                border: 1px solid #555555;
                padding: 5px;
            }
            QLineEdit {
                background-color: #333333;
                color: #e0e0e0;
                border: 1px solid #555555;
                padding: 5px;
            }
            """
            self.setStyleSheet(qss)
        else:
            self.setStyleSheet("")
