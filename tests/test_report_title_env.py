import importlib
import os
import unittest

class TestReportTitleEnv(unittest.TestCase):
    def test_html_report_title_from_env(self):
        env_title = "Custom HTML Title"
        with unittest.mock.patch.dict(os.environ, {"REPORT_TITLE": env_title}):
            module = importlib.import_module("src.reporting.generate_html_report")
            importlib.reload(module)
            self.assertEqual(module.REPORT_TITLE, env_title)

    def test_pdf_report_title_from_env(self):
        env_title = "Custom PDF Title"
        with unittest.mock.patch.dict(os.environ, {"REPORT_TITLE": env_title}):
            module = importlib.import_module("src.reporting.generate_pdf_report")
            importlib.reload(module)
            self.assertEqual(module.REPORT_TITLE, env_title)

if __name__ == "__main__":
    unittest.main()
