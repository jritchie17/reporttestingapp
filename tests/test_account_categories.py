import os
import pandas as pd
import unittest

from src.utils.account_categories import CategoryCalculator

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestCategoryCalculator(unittest.TestCase):
    def setUp(self):
        df = pd.read_csv(os.path.join(FIXTURES, 'sql_data.csv'))
        self.rows = df.to_dict(orient='records')
        self.categories = {
            'CatA': ['1234-5678'],
            'CatB': ['9999-0000'],
        }
        self.formulas = {
            'Net': 'CatA + CatB'
        }

    def test_compute_totals_and_formulas(self):
        calc = CategoryCalculator(self.categories, self.formulas)
        result = calc.compute(list(self.rows))
        self.assertEqual(len(result), len(self.rows) + 3)
        cat_a = next(r for r in result if r['CAReportName'] == 'CatA')
        self.assertEqual(cat_a['Amount'], -100)
        cat_b = next(r for r in result if r['CAReportName'] == 'CatB')
        self.assertEqual(cat_b['Amount'], 50)
        net = next(r for r in result if r['CAReportName'] == 'Net')
        self.assertEqual(net['Amount'], -50)


if __name__ == '__main__':
    unittest.main()
