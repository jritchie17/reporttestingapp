import os
import sys
import re
from pathlib import Path

# Get the absolute path to the root directory
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

# Add the project root to the Python path
sys.path.append(project_root)

from src.database.db_connector import DatabaseConnector
from src.utils.config import AppConfig

def fix_query_syntax(sql_content):
    """Fix the SQL query by adding proper statement separators"""
    # Look for pattern where GROUP BY is immediately followed by DROP TABLE
    pattern = r'(GROUP BY\s+[a-zA-Z0-9_.]+)(\s*DROP\s+TABLE)'
    fixed_sql = re.sub(pattern, r'\1;\n\2', sql_content)
    
    # If no match was found, try a different pattern
    if fixed_sql == sql_content:
        # Try to find any last statement before DROP TABLE
        pattern = r'(\S+\s*?)(\s*DROP\s+TABLE)'
        fixed_sql = re.sub(pattern, r'\1;\n\2', sql_content)
    
    # Add a debug message
    print(f"Original SQL length: {len(sql_content)}")
    print(f"Modified SQL length: {len(fixed_sql)}")
    
    # Check if the fix was applied
    if ";" in fixed_sql and "DROP TABLE" in fixed_sql:
        print("Semi-colon added before DROP TABLE statement")
    
    return fixed_sql

def main():
    # Get the query file path
    query_file = os.path.join(os.path.dirname(__file__), "query.sql")
    
    try:
        # Read the query content
        with open(query_file, 'r') as f:
            sql_content = f.read()
        
        # Fix the query syntax
        fixed_sql = fix_query_syntax(sql_content)
        
        # Initialize database connector
        config = AppConfig()
        db_params = config.get_db_connection_params()
        db = DatabaseConnector(**db_params)
        
        if not db.connect():
            print("Failed to connect to database")
            return
        
        # Execute the fixed query
        print(f"Executing fixed query...")
        result = db.direct_execute(fixed_sql)
        
        # Check the result
        if "error" in result:
            print(f"Error: {result['error']}")
        elif "data" in result and result["data"]:
            print(f"Success! Query returned {len(result['data'])} rows")
            print("Sample of first 5 rows:")
            for i, row in enumerate(result["data"][:5]):
                print(f"Row {i+1}: {row}")
        else:
            print(f"Query executed successfully but returned no data")
            print(result.get("message", "No message"))
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'db' in locals() and db:
            db.close()

if __name__ == "__main__":
    main() 
