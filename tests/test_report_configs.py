import os
import tempfile
import unittest

from tests.qt_stubs import patch_qt_modules


class ReportConfigTests(unittest.TestCase):
    def setUp(self):
        patch_qt_modules()

    def test_config_save_and_load(self):
        from src.utils.config import AppConfig

        with tempfile.TemporaryDirectory() as tmp:
            old_home = os.environ.get('HOME')
            os.environ['HOME'] = tmp

            cfg = AppConfig()
            rc = cfg.get_report_config('SOO PreClose')
            rc['skip_rows'] = 99
            rc['center_cell'] = 'B2'
            cfg.set_report_config('SOO PreClose', rc)

            cfg2 = AppConfig()
            loaded = cfg2.get_report_config('SOO PreClose')
            self.assertEqual(loaded['skip_rows'], 99)
            self.assertEqual(loaded['center_cell'], 'B2')

            if old_home is not None:
                os.environ['HOME'] = old_home
            else:
                del os.environ['HOME']

    def test_soo_mfr_default_config(self):
        from src.utils.config import AppConfig

        with tempfile.TemporaryDirectory() as tmp:
            old_home = os.environ.get('HOME')
            os.environ['HOME'] = tmp

            cfg = AppConfig()
            self.assertEqual(
                cfg.get_report_config('SOO MFR'),
                {
                    'header_rows': [9],
                    'skip_rows': 10,
                    'first_data_column': 4,
                    'center_cell': None,
                    'description': 'SOO MFR report with header on row 10'
                }
            )

            if old_home is not None:
                os.environ['HOME'] = old_home
            else:
                del os.environ['HOME']

    def test_mfr_preclose_default_config(self):
        from src.utils.config import AppConfig

        with tempfile.TemporaryDirectory() as tmp:
            old_home = os.environ.get('HOME')
            os.environ['HOME'] = tmp

            cfg = AppConfig()
            self.assertEqual(
                cfg.get_report_config('MFR PreClose'),
                {
                    'header_rows': [9],
                    'skip_rows': 10,
                    'first_data_column': 4,
                    'center_cell': None,
                    'description': 'MFR PreClose report with header on row 10'
                }
            )

            if old_home is not None:
                os.environ['HOME'] = old_home
            else:
                del os.environ['HOME']

    def test_corp_soo_default_config(self):
        from src.utils.config import AppConfig

        with tempfile.TemporaryDirectory() as tmp:
            old_home = os.environ.get('HOME')
            os.environ['HOME'] = tmp

            cfg = AppConfig()
            self.assertEqual(
                cfg.get_report_config('Corp SOO'),
                {
                    'header_rows': [5],
                    'skip_rows': 7,
                    'first_data_column': 2,
                    'center_cell': None,
                    'description': 'Corporate SOO report with header on row 6'
                }
            )

            if old_home is not None:
                os.environ['HOME'] = old_home
            else:
                del os.environ['HOME']


if __name__ == '__main__':
    unittest.main()

