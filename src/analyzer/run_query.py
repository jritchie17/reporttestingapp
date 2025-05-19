import os
import sys
import re
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_connector import DatabaseConnector

def fix_sql_syntax(sql_content):
    """Add proper statement separators to SQL queries"""
    # First normalize line endings
    normalized = sql_content.replace('\r\n', '\n').replace('\r', '\n')
    
    # Find the pattern "GROUP BY something" followed by "DROP TABLE"
    # This is a common pattern that needs a separator
    pattern = r'(GROUP BY[^\n;]+)(\s*DROP TABLE)'
    fixed_sql = re.sub(pattern, r'\1;\n\2', normalized)
    
    return fixed_sql

def main():
    # Initialize database connection
    db = DatabaseConnector()
    if not db.connect():
        print("Failed to connect to database")
        return
    
    # Get the path to the query file
    query_file = os.path.join(os.path.dirname(__file__), "query.sql")
    
    # Read the query from the file
    try:
        with open(query_file, 'r') as f:
            sql_content = f.read()
        
        # Fix the SQL syntax
        print("Fixing SQL syntax...")
        fixed_sql = fix_sql_syntax(sql_content)
        
        # Write the fixed SQL to a temp file for inspection
        temp_file = os.path.join(os.path.dirname(__file__), "query_temp_fixed.sql")
        with open(temp_file, 'w') as f:
            f.write(fixed_sql)
        print(f"Fixed SQL written to {temp_file}")
        
        # Process the query with GO statements correctly
        print("Executing query using raw_execute method...")
        result = db.raw_execute(fixed_sql)
        
        # Check if there was an error
        if 'error' in result:
            print(f"Error executing query: {result['error']}")
            return
            
        # Print result
        if 'data' in result and len(result['data']) > 0:
            print(f"Query returned {len(result['data'])} rows")
            # Print first few rows
            for i, row in enumerate(result['data'][:5]):
                print(f"Row {i+1}: {row}")
                if i >= 4:
                    print("...")
                    break
        else:
            print("Query executed successfully but returned no data")
            print(result)
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 