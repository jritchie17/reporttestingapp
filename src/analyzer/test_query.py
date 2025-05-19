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
    
    # Very simple temp table test
    test_query = """
CREATE TABLE #TestTable (ID INT, Name VARCHAR(50));

INSERT INTO #TestTable (ID, Name) VALUES (1, 'Test 1'), (2, 'Test 2'), (3, 'Test 3');

SELECT * FROM #TestTable;

DROP TABLE #TestTable;
    """
    
    try:
        print("Running simple temp table test with raw_execute...")
        result = db.raw_execute(test_query)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        elif 'data' in result and result['data']:
            print(f"Success! Got {len(result['data'])} rows back")
            for row in result['data']:
                print(row)
        else:
            print("No data returned")
            print(result)
            
    except Exception as e:
        print(f"Exception: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 