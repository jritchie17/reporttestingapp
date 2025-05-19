import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_connector import DatabaseConnector

def main():
    # Initialize database connection
    db = DatabaseConnector()
    if not db.connect():
        print("Failed to connect to database")
        return
    
    # Get the query file path
    query_file = os.path.join(os.path.dirname(__file__), "query.sql")
    
    try:
        # Read the query content
        with open(query_file, 'r') as f:
            query_content = f.read()
        
        print(f"Executing query from {query_file}...")
        print("Using execute_complex_script method to handle temp tables...")
        
        # Execute the query using the execute_complex_script method
        result = db.execute_complex_script(query_content)
        
        # Check for errors
        if 'error' in result:
            print(f"Error executing query: {result['error']}")
        elif 'data' in result and result['data']:
            print(f"Query executed successfully! Returned {len(result['data'])} rows.")
            # Print a few rows as sample
            for i, row in enumerate(result['data'][:5]):
                print(f"Row {i+1}: {row}")
                if i >= 4:
                    print("...")
                    break
        else:
            print("Query executed successfully, but returned no data.")
            print(result)
    
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 