import sys
import types
import unittest
from unittest.mock import MagicMock

from tests.qt_stubs import patch_qt_modules




class TestWorkflowWizard(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()
        from src.ui.main_window import MainWindow
        from src.ui.workflow_wizard import WorkflowWizard
        self.MainWindow = MainWindow
        self.WorkflowWizard = WorkflowWizard

    def test_wizard_sequence(self):
        calls = []

        window = self.MainWindow.__new__(self.MainWindow)
        window.tab_widget = type('TabWidget', (), {'setCurrentIndex': MagicMock()})()
        window.excel_viewer = type('Viewer', (), {})()

        window.open_excel_file = MagicMock(side_effect=lambda: calls.append('excel'))
        window.open_sql_file = MagicMock(side_effect=lambda: calls.append('sql'))
        window.execute_sql = MagicMock(side_effect=lambda: calls.append('execute'))
        window.compare_results = MagicMock(side_effect=lambda: calls.append('compare'))

        window.excel_viewer.clean_data = MagicMock(side_effect=lambda: calls.append('clean'))
        window.excel_viewer.remove_empty_data_rows = MagicMock(side_effect=lambda: calls.append('remove_empty'))
        window.excel_viewer.extract_sql_codes = MagicMock(side_effect=lambda: calls.append('extract'))
        window.excel_viewer.import_column_headers = MagicMock(side_effect=lambda: calls.append('headers'))

        wizard = self.WorkflowWizard(window)
        wizard.start()

        self.assertEqual(calls, ['excel', 'clean', 'remove_empty', 'sql', 'extract', 'execute', 'headers', 'compare'])
        window.tab_widget.setCurrentIndex.assert_called_with(2)

    def test_step_failure_stops_execution(self):
        calls = []

        window = self.MainWindow.__new__(self.MainWindow)
        window.tab_widget = type('TabWidget', (), {'setCurrentIndex': MagicMock()})()
        window.excel_viewer = type('Viewer', (), {})()

        window.open_excel_file = MagicMock(side_effect=lambda: calls.append('excel'))
        window.open_sql_file = MagicMock(side_effect=lambda: calls.append('sql'))

        def fail_execute():
            calls.append('execute')
            return False

        window.execute_sql = MagicMock(side_effect=fail_execute)
        window.compare_results = MagicMock(side_effect=lambda: calls.append('compare'))

        window.excel_viewer.clean_data = MagicMock(side_effect=lambda: calls.append('clean'))
        window.excel_viewer.remove_empty_data_rows = MagicMock(side_effect=lambda: calls.append('remove_empty'))
        window.excel_viewer.extract_sql_codes = MagicMock(side_effect=lambda: calls.append('extract'))
        window.excel_viewer.import_column_headers = MagicMock(side_effect=lambda: calls.append('headers'))

        wizard = self.WorkflowWizard(window)
        wizard.start()

        self.assertEqual(calls, ['excel', 'clean', 'remove_empty', 'sql', 'extract', 'execute'])
        window.tab_widget.setCurrentIndex.assert_not_called()


if __name__ == '__main__':
    unittest.main()
