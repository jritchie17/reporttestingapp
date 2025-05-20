import unittest
from unittest.mock import MagicMock
from src.database.db_connector import DatabaseConnector

class TestDatabaseConnector(unittest.TestCase):
    def test_execute_query_success(self):
        db = DatabaseConnector()
        db.engine = MagicMock()
        conn = MagicMock()
        db.engine.connect.return_value.__enter__.return_value = conn
        result = MagicMock()
        result.returns_rows = True
        result.keys.return_value = ['a', 'b']
        result.fetchall.return_value = [(1, 'x'), (2, 'y')]
        conn.execute.return_value = result

        data = db.execute_query('SELECT')
        self.assertEqual(data['columns'], ['a', 'b'])
        self.assertEqual(len(data['data']), 2)
        self.assertEqual(data['data'][0]['a'], 1)

    def test_execute_query_error(self):
        db = DatabaseConnector()
        db.engine = MagicMock()
        db.engine.connect.side_effect = Exception('fail')
        res = db.execute_query('SELECT')
        self.assertIn('error', res)

    def test_execute_transaction(self):
        db = DatabaseConnector()
        db.engine = MagicMock()
        conn = MagicMock()
        db.engine.begin.return_value.__enter__.return_value = conn
        result1 = MagicMock()
        result1.returns_rows = False
        result2 = MagicMock()
        result2.returns_rows = True
        result2.keys.return_value = ['x']
        result2.fetchall.return_value = [(1,), (2,)]
        conn.execute.side_effect = [result1, result2]

        data = db.execute_transaction(['Q1', 'Q2'])
        self.assertEqual(data['columns'], ['x'])
        self.assertEqual(len(data['data']), 2)
