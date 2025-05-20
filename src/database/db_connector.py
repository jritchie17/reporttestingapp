import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging
import pyodbc
import re

class DatabaseConnector:
    def __init__(self, server="adwtest", database="cognostesting", trusted_connection=True):
        """Initialize database connection using Windows Authentication"""
        self.server = server
        self.database = database
        self.trusted_connection = trusted_connection
        self.engine = None
        self.Session = None
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up logging for database operations"""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def connect(self):
        """Establish connection to the database"""
        try:
            connection_string = f"mssql+pyodbc://{self.server}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server"
            if self.trusted_connection:
                connection_string += "&trusted_connection=yes"
            
            self.engine = create_engine(connection_string)
            self.Session = sessionmaker(bind=self.engine)
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    self.logger.info(f"Successfully connected to {self.database} on {self.server}")
                    return True
                else:
                    self.logger.error("Connection test failed")
                    return False
                
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            return False
    
    def execute_query(self, query, params=None):
        """Execute a SQL query and return results"""
        if not self.engine:
            self.logger.error("No active database connection")
            return None
        
        try:
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                if result.returns_rows:
                    # Get column names
                    columns = result.keys()
                    
                    # Convert all rows to dictionaries with proper column names
                    data = []
                    for row in result.fetchall():
                        # Create a dictionary with column name as keys and row values
                        row_dict = {}
                        for i, col_name in enumerate(columns):
                            # Ensure column name is hashable (convert to string)
                            col_key = str(col_name)
                            # Use the column index to get the value
                            if i < len(row):
                                row_dict[col_key] = row[i]
                            else:
                                row_dict[col_key] = None
                        data.append(row_dict)
                    
                    self.logger.info(f"Query returned {len(data)} rows")
                    return {"columns": [str(col) for col in columns], "data": data}
                else:
                    return {"message": "Query executed successfully (no rows returned)"}
                
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            return {"error": str(e)}
    
    def execute_transaction(self, queries):
        """Execute multiple SQL queries within a single transaction
        
        Args:
            queries: List of SQL query strings or tuples of (query, params)
            
        Returns:
            Result of the last query executed
        """
        if not self.engine:
            self.logger.error("No active database connection")
            return None
            
        try:
            with self.engine.begin() as conn:
                results = None
                
                for query_item in queries:
                    if isinstance(query_item, tuple):
                        query, params = query_item
                        result = conn.execute(text(query), params)
                    else:
                        result = conn.execute(text(query_item))
                    
                    # Store the last result
                    if result.returns_rows:
                        # Get column names
                        columns = result.keys()
                        
                        # Convert all rows to dictionaries with proper column names
                        data = []
                        for row in result.fetchall():
                            # Create a dictionary with column name as keys and row values
                            row_dict = {}
                            for i, col_name in enumerate(columns):
                                # Ensure column name is hashable (convert to string)
                                col_key = str(col_name)
                                # Use the column index to get the value
                                if i < len(row):
                                    row_dict[col_key] = row[i]
                                else:
                                    row_dict[col_key] = None
                            data.append(row_dict)
                        
                        results = {"columns": [str(col) for col in columns], "data": data}
                        self.logger.info(f"Query returned {len(data)} rows")
                    else:
                        results = {"message": "Query executed successfully (no rows returned)"}
                
                return results
                
        except Exception as e:
            self.logger.error(f"Transaction execution failed: {str(e)}")
            return {"error": str(e)}
    
    def load_sql_file(self, file_path):
        """Load and execute a SQL file"""
        if not os.path.exists(file_path):
            self.logger.error(f"SQL file not found: {file_path}")
            return {"error": f"File not found: {file_path}"}
        
        try:
            with open(file_path, 'r') as f:
                sql_content = f.read()
            
            return self.execute_query(sql_content)
            
        except Exception as e:
            self.logger.error(f"Failed to load SQL file: {str(e)}")
            return {"error": str(e)}
    
    def execute_complex_script(self, script):
        """Execute a complex SQL script that may contain temp tables or multiple statements
        
        This method uses a single transaction to handle scripts with temporary tables.
        
        Args:
            script: SQL script as a string
            
        Returns:
            The result of the final query that returns rows, or status message
        """
        if not self.engine:
            self.logger.error("No active database connection")
            return None
            
        try:
            # Use a transaction to keep the connection open for the entire script
            with self.engine.begin() as conn:
                # Split the script by GO statements if present
                statements = []
                current_statement = []
                
                # Normalize line endings
                normalized_script = script.replace('\r\n', '\n').replace('\r', '\n')
                
                # Process line by line to handle GO statements correctly
                for line in normalized_script.split('\n'):
                    if line.strip().upper() == 'GO':
                        if current_statement:
                            statements.append('\n'.join(current_statement))
                            current_statement = []
                    else:
                        current_statement.append(line)
                
                # Add the last statement if not empty
                if current_statement:
                    statements.append('\n'.join(current_statement))
                
                # If no GO statements found, just use the original script
                if not statements:
                    statements = [script]
                
                self.logger.info(f"Script split into {len(statements)} statements")
                
                # Execute each statement in order
                last_result = None
                for i, statement in enumerate(statements):
                    if not statement.strip():
                        continue
                        
                    self.logger.info(f"Executing statement {i+1} of {len(statements)}")
                    
                    # Execute the statement
                    result = conn.execute(text(statement))
                    
                    # If the statement returns rows, capture the result
                    if result.returns_rows:
                        # Get column names
                        columns = result.keys()
                        
                        # Convert all rows to dictionaries
                        data = []
                        for row in result.fetchall():
                            row_dict = {}
                            for i, col_name in enumerate(columns):
                                col_key = str(col_name)
                                if i < len(row):
                                    row_dict[col_key] = row[i]
                                else:
                                    row_dict[col_key] = None
                            data.append(row_dict)
                        
                        self.logger.info(f"Statement returned {len(data)} rows")
                        last_result = {"columns": [str(col) for col in columns], "data": data}
                
                # Return the last result with rows, or a success message
                if last_result:
                    return last_result
                else:
                    return {"message": "Script executed successfully (no rows returned)"}
                
        except Exception as e:
            self.logger.error(f"Script execution failed: {str(e)}")
            return {"error": str(e)}
    
    def raw_execute(self, script):
        """Execute SQL directly with a single transaction for temp tables
        
        This method maintains a single transaction for the entire script,
        allowing temp tables to persist between statements.
        
        Args:
            script: Complete SQL script as a string
            
        Returns:
            Dictionary with results or error message
        """
        if not self.engine:
            self.logger.error("No active database connection")
            return None
            
        try:
            # Start a transaction
            with self.engine.begin() as conn:
                # Execute the entire script in one go
                self.logger.info("Executing script in a single transaction")
                
                # Split the script if it has GO statements
                statements = []
                current_statement = []
                
                # Normalize line endings
                script = script.replace('\r\n', '\n').replace('\r', '\n')
                
                # Split by GO statements if present
                for line in script.split('\n'):
                    if line.strip().upper() == 'GO':
                        if current_statement:
                            statements.append('\n'.join(current_statement))
                            current_statement = []
                    else:
                        current_statement.append(line)
                
                # Add the last statement if any
                if current_statement:
                    statements.append('\n'.join(current_statement))
                
                # If no GO statements were found, try to split by semicolons
                if len(statements) <= 1:
                    # Just use the original script
                    statements = [script]
                
                # Execute each statement
                self.logger.info(f"Script split into {len(statements)} statements")
                
                last_result = None
                for i, stmt in enumerate(statements):
                    if not stmt.strip():
                        continue
                        
                    self.logger.info(f"Executing statement {i+1} of {len(statements)}")
                    
                    try:
                        result = conn.execute(text(stmt))
                        
                        if result.returns_rows:
                            # Get column names
                            columns = result.keys()
                            
                            # Convert all rows to dictionaries with proper column names
                            data = []
                            for row in result.fetchall():
                                # Create a dictionary with column name as keys and row values
                                row_dict = {}
                                for i, col_name in enumerate(columns):
                                    # Ensure column name is hashable (convert to string)
                                    col_key = str(col_name)
                                    # Use the column index to get the value
                                    if i < len(row):
                                        row_dict[col_key] = row[i]
                                    else:
                                        row_dict[col_key] = None
                                data.append(row_dict)
                            
                            self.logger.info(f"Statement returned {len(data)} rows")
                            last_result = {"columns": [str(col) for col in columns], "data": data}
                    except Exception as e:
                        self.logger.error(f"Error executing statement {i+1}: {str(e)}")
                        if "Incorrect syntax" in str(e):
                            self.logger.error(f"Statement with syntax error: {stmt[:100]}...")
                        return {"error": f"Error in statement {i+1}: {str(e)}"}
                
                # Return the last result that had rows, or a success message
                if last_result:
                    return last_result
                else:
                    return {"message": "Script executed successfully (no rows returned)"}
                
        except Exception as e:
            self.logger.error(f"Transaction execution failed: {str(e)}")
            return {"error": str(e)}
    
    def _normalize_script(self, script):
        """Normalize a SQL script by cleaning up comments and ensuring statement terminators."""
        # Handle different line endings
        normalized = script.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove comments and normalize whitespace
        lines = []
        for line in normalized.split('\n'):
            # Remove comments starting with --
            if '--' in line:
                line = line.split('--')[0]
            
            # Keep non-empty lines
            if line.strip():
                lines.append(line)
        
        # Join back with newlines
        clean_script = '\n'.join(lines)
        
        # Ensure statements end with semicolons
        # This is a simplistic approach and may not work for all scripts
        # Find the pattern "GROUP BY something" followed by "DROP TABLE" or another keyword
        patterns = [
            (r'(GROUP BY[^\n;]+)(\s*DROP TABLE)', r'\1;\n\2'),
            (r'(GROUP BY[^\n;]+)(\s*CREATE TABLE)', r'\1;\n\2'),
            (r'(GROUP BY[^\n;]+)(\s*INSERT INTO)', r'\1;\n\2'),
            (r'(GROUP BY[^\n;]+)(\s*UPDATE)', r'\1;\n\2'),
            (r'(GROUP BY[^\n;]+)(\s*DELETE)', r'\1;\n\2'),
            (r'(GROUP BY[^\n;]+)(\s*SELECT)', r'\1;\n\2'),
            (r'(DROP TABLE[^\n;]+)(\s*\w+)', r'\1;\n\2'),
        ]
        
        for pattern, replacement in patterns:
            clean_script = re.sub(pattern, replacement, clean_script)
        
        self.logger.info(f"Normalized script from {len(script)} to {len(clean_script)} chars")
        
        # Debug: Print the first 200 chars of the normalized script
        self.logger.info(f"Script starts with: {clean_script[:200]}")
        
        return clean_script
    
    def close(self):
        """Close the database connection"""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Database connection closed")
    
    def direct_execute(self, script):
        """Execute SQL using direct ODBC connection with autocommit enabled.
        
        This method directly uses pyodbc with autocommit enabled, which most
        closely mimics how SSMS executes queries. Use this for complex scripts
        with temp tables that aren't working with other methods.
        
        Args:
            script: SQL script as a string
            
        Returns:
            Dictionary with results or error message
        """
        try:
            # Build connection string
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database}"
            if self.trusted_connection:
                conn_str += ";Trusted_Connection=yes"
            else:
                # Add credentials if not using Windows auth
                conn_str += ";UID={uid};PWD={pwd}".format(uid=self.uid, pwd=self.pwd)
                
            self.logger.info(f"Connecting with direct ODBC and autocommit")
            
            # Create connection with autocommit enabled
            conn = pyodbc.connect(conn_str, autocommit=True)
            cursor = conn.cursor()
            
            # Execute the script directly
            self.logger.info("Executing script with pyodbc directly")
            cursor.execute(script)
            
            # Process results
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                
                # Convert rows to dictionaries
                data = []
                for row in rows:
                    row_dict = {}
                    for i, col_name in enumerate(columns):
                        col_key = str(col_name)
                        row_dict[col_key] = row[i] if i < len(row) else None
                    data.append(row_dict)
                
                self.logger.info(f"Query returned {len(data)} rows")
                result = {"columns": columns, "data": data}
            else:
                result = {"message": "Script executed successfully (no rows returned)"}
            
            # Close cursor and connection
            cursor.close()
            conn.close()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Direct ODBC execution failed: {str(e)}")
            return {"error": str(e)} 
