import os
import sys
import pyodbc
import re
from pathlib import Path

# Get the absolute path to the root directory
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

# Add the project root to the Python path
sys.path.append(project_root)

def extract_statements(sql_content):
    """Extract statements from SQL file, handling temp tables properly"""
    # Define the statements that need to be separated
    parts = []
    
    # 1. Create temp table statement
    create_temp_pattern = r'.*?INTO\s+#HierarchyData.*?(?=SELECT\s+h\.Center|$)'
    create_temp_match = re.search(create_temp_pattern, sql_content, re.DOTALL | re.IGNORECASE)
    
    if create_temp_match:
        parts.append(create_temp_match.group(0).strip())
        
        # 2. Main query
        remaining = sql_content[create_temp_match.end():].strip()
        
        # Find where DROP TABLE starts
        drop_pattern = r'DROP\s+TABLE\s+#HierarchyData'
        drop_match = re.search(drop_pattern, remaining, re.IGNORECASE)
        
        if drop_match:
            # Extract the main query part before DROP TABLE
            main_query = remaining[:drop_match.start()].strip()
            parts.append(main_query)
            
            # Extract the DROP TABLE part
            drop_statement = remaining[drop_match.start():].strip()
            parts.append(drop_statement)
        else:
            # If no DROP TABLE is found, just add the remaining query
            parts.append(remaining)
    else:
        # If no match for create temp table, just use the whole script
        parts.append(sql_content)
    
    return parts

def run_real_query():
    """Run the real query with proper handling for temp tables"""
    
    # Connection parameters
    server = "adwtest"
    database = "cognostesting"
    
    # Create connection string with trusted connection
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
    
    try:
        # Get the query file path
        query_file = os.path.join(os.path.dirname(__file__), "query.sql")
        
        # Read the query content
        with open(query_file, 'r') as f:
            sql_content = f.read()
        
        # Extract statements
        statements = extract_statements(sql_content)
        
        print(f"Query split into {len(statements)} statements")
        for i, stmt in enumerate(statements):
            print(f"Statement {i+1} length: {len(stmt)} characters")
        
        # Connect with autocommit mode
        print(f"Connecting to {server}/{database}...")
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        # Execute each statement separately
        for i, stmt in enumerate(statements):
            if stmt.strip():
                print(f"Executing statement {i+1}...")
                try:
                    cursor.execute(stmt)
                    
                    # Check if this statement returns results
                    if cursor.description:
                        columns = [column[0] for column in cursor.description]
                        print(f"Columns: {', '.join(columns)}")
                        
                        rows = cursor.fetchall()
                        print(f"Results: {len(rows)} rows returned")
                        
                        # Display a sample of the results
                        if rows:
                            print("\nSample of first 5 rows:")
                            for row in rows[:5]:
                                print(row)
                    else:
                        print("Statement executed successfully (no results)")
                except Exception as e:
                    print(f"Error executing statement {i+1}: {e}")
                    # Print the first 200 characters of the statement for debugging
                    print(f"Statement begins with: {stmt[:200]}...")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        print("Query execution completed!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_real_query() 
