import sys
import os
import unittest
import pandas as pd
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.config import AppConfig
from src.database.db_connector import DatabaseConnector
from src.analyzer.excel_analyzer import ExcelAnalyzer
from src.analyzer.comparison_engine import ComparisonEngine
from src.utils.query_builder import QueryBuilder


class TestBasicFunctionality(unittest.TestCase):
    """Basic tests to verify functionality"""
    
    def test_config_loads(self):
        """Test that the configuration loads properly"""
        config = AppConfig()
        
        # Check default values
        self.assertEqual(config.get("database", "server"), "adwtest")
        self.assertEqual(config.get("database", "database"), "cognostesting")
        self.assertTrue(config.get("database", "trusted_connection"))
        
    @patch('src.database.db_connector.create_engine')
    def test_database_connector(self, mock_create_engine):
        """Test the database connector with mocked engine"""
        # Mock the database connection
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        # Mock engine.connect().execute().scalar()
        mock_connection = MagicMock()
        mock_engine.connect.return_value = mock_connection
        mock_execute = MagicMock()
        mock_connection.execute.return_value = mock_execute
        mock_execute.scalar.return_value = 1
        
        # Create connector
        connector = DatabaseConnector(server="test_server", database="test_db")
        
        # Test connection
        self.assertTrue(connector.connect())
        
        # Check expected calls
        mock_create_engine.assert_called_once()
        mock_engine.connect.assert_called_once()
        
    def test_comparison_engine(self):
        """Test comparison engine with basic dataframes"""
        # Create test dataframes
        excel_data = {'A': [1, 2, 3], 'B': ['x', 'y', 'z']}
        sql_data = {'A': [1, 2, 3], 'B': ['x', 'y', 'z']}
        
        excel_df = pd.DataFrame(excel_data)
        sql_df = pd.DataFrame(sql_data)
        
        # Create comparison engine
        engine = ComparisonEngine()
        
        # Perform comparison
        result = engine.compare_dataframes(excel_df, sql_df)
        
        # Check results
        self.assertTrue(result["row_count_match"])
        self.assertEqual(result["row_counts"]["excel"], 3)
        self.assertEqual(result["row_counts"]["sql"], 3)
        self.assertEqual(result["summary"]["mismatch_percentage"], 0)
        self.assertTrue(result["summary"]["overall_match"])
        
    def test_excel_analyzer_init(self):
        """Test Excel analyzer initialization"""
        # Create analyzer with fake path
        analyzer = ExcelAnalyzer("fake_path.xlsx")
        
        # Check initialization
        self.assertEqual(analyzer.file_path, "fake_path.xlsx")
        self.assertIsNone(analyzer.excel_file)
        self.assertEqual(analyzer.sheet_names, [])
        
    def test_query_builder(self):
        """Test query builder with sample dataframe"""
        # Create test dataframe
        data = {
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C'],
            'value': [10.5, 20.5, 30.5],
            'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03'])
        }
        df = pd.DataFrame(data)
        
        # Create query builder
        builder = QueryBuilder()
        
        # Generate table query
        table_query = builder.create_table_query(df, "test_table")
        
        # Check query contains all columns
        self.assertIn("id", table_query)
        self.assertIn("name", table_query)
        self.assertIn("value", table_query)
        self.assertIn("date", table_query)
        
        # Generate select query
        select_query = builder.create_select_query(df, "test_table")
        
        # Check query format
        self.assertTrue(select_query.startswith("SELECT"))
        self.assertIn("FROM test_table", select_query)


if __name__ == '__main__':
    unittest.main()
