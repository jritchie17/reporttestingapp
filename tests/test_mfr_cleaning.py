import unittest
import pandas as pd
from tests.qt_stubs import patch_qt_modules


class TestMFRCleaning(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()

    def test_apply_headers_updates_analyzer(self):
        """Importing headers should update analyzer sheet data and affect comparison."""
        from src.ui.excel_viewer import ExcelViewer
        from src.analyzer.excel_analyzer import ExcelAnalyzer
        from src.analyzer.comparison_engine import ComparisonEngine

        class DummyCombo:
            def __init__(self):
                self.items = []
                self.current = ""

            def currentText(self):
                return self.current

            def clear(self):
                self.items = []

            def addItems(self, items):
                self.items.extend(items)

            def findText(self, text):
                try:
                    return self.items.index(text)
                except ValueError:
                    return -1

            def setCurrentIndex(self, idx):
                if 0 <= idx < len(self.items):
                    self.current = self.items[idx]

        class DummyTable:
            def setModel(self, model):
                self.model = model

            def resizeColumnsToContents(self):
                pass

        # Set up viewer without full Qt init
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.df = pd.DataFrame({"A": [1], "B": [2]})
        viewer.filtered_df = viewer.df.copy()
        viewer.sheet_name = "Sheet1"
        viewer.filter_column = DummyCombo()
        viewer.table_view = DummyTable()
        viewer.current_theme = "light"
        viewer.update_view = lambda: None

        # Set up analyzer and parent window
        analyzer = ExcelAnalyzer("dummy.xlsx")
        analyzer.sheet_names = ["Sheet1"]
        analyzer.sheet_data["Sheet1"] = {"dataframe": viewer.df.copy()}

        class Parent:
            def __init__(self, an):
                self.excel_analyzer = an

        parent = Parent(analyzer)
        viewer.window = lambda: parent

        # Apply headers from SQL
        viewer._apply_sql_headers(["X", "Y"])

        self.assertEqual(
            list(analyzer.sheet_data["Sheet1"]["dataframe"].columns), ["X", "Y"]
        )

        # Comparison should succeed with new headers
        engine = ComparisonEngine()
        sql_df = pd.DataFrame({"X": [1], "Y": [2]})
        result = engine.compare_dataframes(analyzer.sheet_data["Sheet1"]["dataframe"], sql_df)
        self.assertTrue(result["summary"]["overall_match"])

    def test_clean_sheet_updates_analyzer(self):
        """Cleaning a sheet should update the analyzer's dataframe."""
        from src.ui.excel_viewer import ExcelViewer
        from src.analyzer.excel_analyzer import ExcelAnalyzer

        class DummyButton:
            def setEnabled(self, val):
                self.enabled = val

            def setToolTip(self, text):
                self.tip = text

        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 1,
            'description': ''
        }
        viewer.report_type = None

        df = pd.DataFrame([
            ['A', 'B'],
            [1, 2],
            [3, 4]
        ])

        viewer.df = df
        viewer.filtered_df = df.copy()
        viewer.sheet_name = 'Sheet1'
        viewer.clean_button = DummyButton()
        viewer.update_button_states = lambda *a, **k: None
        viewer.load_dataframe = lambda *a, **k: None

        analyzer = ExcelAnalyzer('dummy.xlsx')
        analyzer.sheet_names = ['Sheet1']
        analyzer.sheet_data['Sheet1'] = {'dataframe': df.copy()}

        class Parent:
            def __init__(self, an):
                self.excel_analyzer = an

        parent = Parent(analyzer)
        viewer.window = lambda: parent

        viewer.clean_sheet()

        cleaned = analyzer.sheet_data['Sheet1']['dataframe']
        self.assertEqual(list(cleaned.columns), ['Sheet_Name', 'A', 'B'])
        self.assertEqual(len(cleaned), 2)

    def test_mfr_headers_prefixed(self):
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 4,
            'description': ''
        }
        viewer.report_type = 'SOO MFR'

        df = pd.DataFrame([
            ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S'],
            [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
        ])

        from PyQt6.QtWidgets import QInputDialog
        responses = iter([('May', True), ('2025', True)])
        QInputDialog.getItem = staticmethod(lambda *a, **k: next(responses))

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        expected = [
            'A','B','C',
            'May 2025 D','May 2025 E','May 2025 F','May 2025 G','May 2025 H','May 2025 I',
            'May 2024 J','May 2024 K','May 2024 L',
            'YTD May 2025 M','YTD May 2025 N','YTD May 2025 O','YTD May 2025 P',
            'YTD May 2024 Q','YTD May 2024 R','YTD May 2024 S'
        ]
        self.assertEqual(list(cleaned.columns), expected)

    def test_mfr_preclose_headers_prefixed(self):
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 4,
            'description': ''
        }
        viewer.report_type = 'MFR PreClose'

        df = pd.DataFrame([
            ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S'],
            [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
        ])

        from PyQt6.QtWidgets import QInputDialog
        responses = iter([('May', True), ('2025', True)])
        QInputDialog.getItem = staticmethod(lambda *a, **k: next(responses))

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)
        expected = [
            'Sheet_Name','A','B','C',
            'May 2025 D','May 2025 E','May 2025 F','May 2025 G','May 2025 H','May 2025 I',
            'May 2024 J','May 2024 K','May 2024 L',
            'YTD May 2025 M','YTD May 2025 N','YTD May 2025 O','YTD May 2025 P',
            'YTD May 2024 Q','YTD May 2024 R','YTD May 2024 S'
        ]
        self.assertEqual(list(cleaned.columns), expected)

    def test_prefix_respects_first_data_column(self):
        """Columns starting at index defined by ``first_data_column`` should be
        prefixed after cleaning."""
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 2,
            'description': ''
        }
        viewer.report_type = 'SOO MFR'

        df = pd.DataFrame([
            ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S'],
            [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
        ])

        from PyQt6.QtWidgets import QInputDialog
        responses = iter([('May', True), ('2025', True)])
        QInputDialog.getItem = staticmethod(lambda *a, **k: next(responses))

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)

        # Columns C and D correspond to indices 2 and 3. With ``first_data_column``
        # set to 2, these should receive prefixes.
        self.assertEqual(cleaned.columns[2], 'May 2025 C')
        self.assertEqual(cleaned.columns[3], 'May 2025 D')
        self.assertEqual(cleaned.columns[4], 'May 2025 E')

    def test_duplicate_headers_suffix_removed(self):
        """Numbering applied to resolve duplicates should be dropped if prefixes make them unique."""
        from src.ui.excel_viewer import ExcelViewer
        viewer = ExcelViewer.__new__(ExcelViewer)
        viewer.report_config = {
            'header_rows': [0],
            'skip_rows': 1,
            'first_data_column': 2,
            'description': ''
        }
        viewer.report_type = 'SOO MFR'

        df = pd.DataFrame([
            ['A','B','Acct','D','E','F','G','H','Acct','J','K','L'],
            [1,2,3,4,5,6,7,8,9,10,11,12]
        ])

        from PyQt6.QtWidgets import QInputDialog
        responses = iter([('May', True), ('2025', True)])
        QInputDialog.getItem = staticmethod(lambda *a, **k: next(responses))

        cleaned = ExcelViewer._clean_dataframe(viewer, df, 'Sheet1')
        self.assertIsNotNone(cleaned)

        # Suffix numbering should be removed when not needed
        self.assertIn('May 2025 Acct', cleaned.columns)
        self.assertIn('May 2024 Acct', cleaned.columns)
        self.assertNotIn('May 2024 Acct_1', cleaned.columns)


if __name__ == '__main__':
    unittest.main()
