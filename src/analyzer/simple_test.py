import os
import sys
import pyodbc
from pathlib import Path

# Get the absolute path to the root directory
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

# Add the project root to the Python path
sys.path.append(project_root)

def run_temp_table_test():
    """Run a simple temp table test using direct ODBC connection"""
    
    # Connection parameters - using the same as your app
    server = "adwtest"
    database = "cognostesting"
    
    # Create connection string with trusted connection
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
    
    # Simple temp table test query
    test_query = """
    -- Create a temp table
    CREATE TABLE #TestData (ID INT, Name VARCHAR(50), Value DECIMAL(10,2));
    
    -- Insert some data
    INSERT INTO #TestData (ID, Name, Value) 
    VALUES (1, 'Test 1', 100.00), (2, 'Test 2', 200.00), (3, 'Test 3', 300.00);
    
    -- Query the data
    SELECT * FROM #TestData;
    
    -- Clean up
    DROP TABLE #TestData;
    """
    
    try:
        # Connect with autocommit mode (important for temp tables)
        print(f"Connecting to {server}/{database}...")
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        # Execute the query
        print("Executing temp table test...")
        
        # Split the query into separate statements
        statements = test_query.split(";")
        
        # Execute each statement separately
        for stmt in statements:
            if stmt.strip():
                try:
                    cursor.execute(stmt)
                    
                    # Check if this statement returns results
                    if cursor.description:
                        rows = cursor.fetchall()
                        
                        # Print the results
                        print(f"\nQuery results ({len(rows)} rows):")
                        for row in rows:
                            print(f"ID={row.ID}, Name={row.Name}, Value={row.Value}")
                except Exception as e:
                    print(f"Error executing statement: {e}")
                    print(f"Statement: {stmt}")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_temp_table_test() 
