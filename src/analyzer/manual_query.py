import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from database.db_connector import DatabaseConnector

def run_query():
    """Run a simple test query with a temp table to verify it works"""
    db = DatabaseConnector()
    if not db.connect():
        print("Failed to connect to database")
        return
    
    try:
        # Use with engine.begin() to create a transaction that stays open
        with db.engine.begin() as conn:
            # Create a temp table
            print("Creating temp table...")
            conn.execute(text("CREATE TABLE #TestTable (ID INT, Name VARCHAR(50))"))
            
            # Insert data
            print("Inserting data...")
            conn.execute(text("INSERT INTO #TestTable (ID, Name) VALUES (1, 'Test 1'), (2, 'Test 2'), (3, 'Test 3')"))
            
            # Select data
            print("Selecting data...")
            result = conn.execute(text("SELECT * FROM #TestTable"))
            
            # Print results
            for row in result:
                print(f"Row: ID={row[0]}, Name={row[1]}")
            
            # Drop temp table
            print("Dropping temp table...")
            conn.execute(text("DROP TABLE #TestTable"))
            
            print("Test completed successfully!")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_query() 