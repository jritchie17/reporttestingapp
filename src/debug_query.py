import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent))

from database.db_connector import DatabaseConnector
from utils.config import AppConfig

def main():
    """Test SQL queries using different execution methods"""
    # Get query path from command line argument
    if len(sys.argv) < 2:
        print("Usage: python debug_query.py <path_to_sql_file> [--method method_name]")
        print("Available methods: standard, complex, direct, all (default)")
        return
    
    # Get the query file
    query_file = sys.argv[1]
    if not os.path.exists(query_file):
        print(f"Error: File {query_file} not found.")
        return
    
    # Parse optional method argument
    method = "all"  # Default to all methods
    if len(sys.argv) > 2 and sys.argv[2] == "--method" and len(sys.argv) > 3:
        method = sys.argv[3].lower()
        if method not in ["standard", "complex", "direct", "all"]:
            print(f"Invalid method: {method}")
            print("Available methods: standard, complex, direct, all")
            return
    
    # Read the query
    with open(query_file, 'r') as f:
        query = f.read()
    
    # Initialize database connector
    config = AppConfig()
    db_params = config.get_db_connection_params()
    db = DatabaseConnector(**db_params)
    
    if not db.connect():
        print("Failed to connect to database.")
        return
    
    try:
        print(f"Testing query from {query_file}")
        print(f"Query has {len(query)} characters and contains {'#' if '#' in query else 'no'} temp tables")
        print("=" * 80)
        
        # Test with standard execute_query
        if method in ["standard", "all"]:
            print("\nMethod 1: Standard execute_query")
            print("-" * 40)
            result = db.execute_query(query)
            print_result(result)
        
        # Test with execute_complex_script
        if method in ["complex", "all"]:
            print("\nMethod 2: execute_complex_script (transaction mode)")
            print("-" * 40)
            result = db.execute_complex_script(query)
            print_result(result)
        
        # Test with direct_execute
        if method in ["direct", "all"]:
            print("\nMethod 3: direct_execute (ODBC with autocommit)")
            print("-" * 40)
            result = db.direct_execute(query)
            print_result(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()
        print("\nDatabase connection closed")

def print_result(result):
    """Print execution result in a readable format"""
    if "error" in result:
        print(f"ERROR: {result['error']}")
    elif "data" in result and result["data"]:
        print(f"SUCCESS: Query returned {len(result['data'])} rows")
        print("Sample of results:")
        for i, row in enumerate(result["data"][:5]):
            print(f"Row {i+1}: {row}")
        if len(result["data"]) > 5:
            print(f"... and {len(result['data']) - 5} more rows")
    else:
        print("NOTICE: Query executed successfully but returned no data")
        print(result.get("message", "No message"))

if __name__ == "__main__":
    main() 