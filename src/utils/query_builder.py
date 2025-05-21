import re
import pandas as pd
from .logging_config import get_logger
from datetime import datetime

class QueryBuilder:
    def __init__(self):
        """Initialize the query builder"""
        self.logger = get_logger(__name__)
    
    def clean_column_name(self, name):
        """Clean and normalize column name for SQL query"""
        if not isinstance(name, str):
            name = str(name)
            
        # Remove special characters
        name = re.sub(r'[^\w\s]', ' ', name)
        
        # Replace multiple spaces with single space
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        
        # Make sure it's a valid SQL identifier
        if name and not name[0].isalpha() and name[0] != '_':
            name = 'col_' + name
            
        return name.lower()
    
    def guess_sql_type(self, series):
        """Guess SQL data type from pandas series"""
        if pd.api.types.is_integer_dtype(series):
            return "INT"
        elif pd.api.types.is_float_dtype(series):
            return "FLOAT"
        elif pd.api.types.is_datetime64_dtype(series):
            return "DATETIME"
        elif pd.api.types.is_bool_dtype(series):
            return "BIT"
        elif pd.api.types.is_string_dtype(series):
            # Check max length to determine VARCHAR size
            max_len = series.astype(str).str.len().max()
            if max_len <= 50:
                return f"VARCHAR(50)"
            elif max_len <= 255:
                return f"VARCHAR(255)"
            else:
                return "TEXT"
        else:
            return "VARCHAR(255)"  # Default type
    
    def create_table_query(self, df, table_name):
        """Generate a CREATE TABLE SQL query from dataframe"""
        if df.empty:
            self.logger.warning("Cannot create table query from empty dataframe")
            return None
            
        # Clean table name
        table_name = re.sub(r'[^a-zA-Z0-9_]', '_', table_name)
        
        # Build query
        query = f"CREATE TABLE {table_name} (\n"
        
        # Add columns
        columns = []
        for col in df.columns:
            col_name = self.clean_column_name(col)
            col_type = self.guess_sql_type(df[col])
            columns.append(f"    {col_name} {col_type}")
            
        query += ",\n".join(columns)
        query += "\n);"
        
        self.logger.info(f"Created table query for {table_name} with {len(columns)} columns")
        return query
    
    def create_insert_query(self, df, table_name, batch_size=1000):
        """Generate INSERT SQL queries from dataframe"""
        if df.empty:
            self.logger.warning("Cannot create insert query from empty dataframe")
            return None
            
        # Clean table name
        table_name = re.sub(r'[^a-zA-Z0-9_]', '_', table_name)
        
        # Clean column names
        columns = [self.clean_column_name(col) for col in df.columns]
        column_str = ", ".join(columns)
        
        # Generate insert statements in batches
        queries = []
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            query = f"INSERT INTO {table_name} ({column_str}) VALUES\n"
            
            # Generate value rows
            rows = []
            for _, row in batch.iterrows():
                values = []
                for val in row:
                    if pd.isna(val):
                        values.append("NULL")
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    elif isinstance(val, datetime):
                        values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                    elif isinstance(val, bool):
                        values.append("1" if val else "0")
                    else:
                        # Escape single quotes in strings
                        val_str = str(val).replace("'", "''")
                        values.append(f"'{val_str}'")
                        
                rows.append(f"({', '.join(values)})")
                
            query += ",\n".join(rows)
            query += ";"
            
            queries.append(query)
            
        self.logger.info(f"Created {len(queries)} insert queries for {table_name}")
        return queries
    
    def create_select_query(self, df, table_name, conditions=None, limit=None):
        """Generate a SELECT SQL query from dataframe"""
        if df.empty:
            self.logger.warning("Cannot create select query from empty dataframe")
            return None
            
        # Clean table name
        table_name = re.sub(r'[^a-zA-Z0-9_]', '_', table_name)
        
        # Clean column names
        columns = [self.clean_column_name(col) for col in df.columns]
        column_str = ",\n    ".join(columns)
        
        # Build query
        query = f"SELECT\n    {column_str}\nFROM {table_name}"
        
        # Add conditions if provided
        if conditions:
            query += f"\nWHERE {conditions}"
            
        # Add limit if provided
        if limit:
            query += f"\nLIMIT {limit}"
            
        query += ";"
        
        self.logger.info(f"Created select query for {table_name} with {len(columns)} columns")
        return query
    
    def analyze_excel_for_query(self, df, sheet_name):
        """Analyze Excel data and suggest SQL queries"""
        if df.empty:
            self.logger.warning("Cannot analyze empty dataframe")
            return []
            
        suggested_queries = []
        
        # Clean sheet name to use as table name
        table_name = re.sub(r'[^a-zA-Z0-9_]', '_', sheet_name)
        
        # Suggest CREATE TABLE query
        create_query = self.create_table_query(df, table_name)
        if create_query:
            suggested_queries.append({
                "name": f"Create {table_name} table",
                "sql": create_query,
                "purpose": "Creates a table structure based on the Excel sheet"
            })
            
        # Suggest INSERT query for sample data
        insert_queries = self.create_insert_query(df.head(10), table_name)
        if insert_queries:
            suggested_queries.append({
                "name": f"Insert sample data into {table_name}",
                "sql": insert_queries[0],
                "purpose": "Inserts a sample of data from the Excel sheet"
            })
            
        # Suggest SELECT query
        select_query = self.create_select_query(df, table_name)
        if select_query:
            suggested_queries.append({
                "name": f"Select all data from {table_name}",
                "sql": select_query,
                "purpose": "Retrieves all data from the table for comparison"
            })
            
        # Suggest SELECT query with limit
        select_limit_query = self.create_select_query(df, table_name, limit=100)
        if select_limit_query:
            suggested_queries.append({
                "name": f"Select sample data from {table_name}",
                "sql": select_limit_query,
                "purpose": "Retrieves a sample of data from the table for comparison"
            })
            
        # Try to identify key columns for filtering
        # Look for ID-like columns
        id_columns = [col for col in df.columns if 'id' in str(col).lower()]
        if id_columns:
            for id_col in id_columns:
                clean_id_col = self.clean_column_name(id_col)
                # Suggest a query with WHERE clause
                where_query = self.create_select_query(
                    df, 
                    table_name, 
                    conditions=f"{clean_id_col} = your_value_here"
                )
                if where_query:
                    suggested_queries.append({
                        "name": f"Filter {table_name} by {id_col}",
                        "sql": where_query,
                        "purpose": f"Retrieves specific data filtered by {id_col}"
                    })
                    
        # Look for date-like columns for time-based filtering
        date_columns = [
            col for col in df.columns 
            if any(date_term in str(col).lower() for date_term in ['date', 'time', 'day', 'month', 'year'])
        ]
        if date_columns:
            for date_col in date_columns:
                clean_date_col = self.clean_column_name(date_col)
                # Suggest a query with date range
                date_query = self.create_select_query(
                    df, 
                    table_name, 
                    conditions=f"{clean_date_col} BETWEEN 'start_date' AND 'end_date'"
                )
                if date_query:
                    suggested_queries.append({
                        "name": f"Filter {table_name} by {date_col} range",
                        "sql": date_query,
                        "purpose": f"Retrieves data within a specific date range based on {date_col}"
                    })
                    
        self.logger.info(f"Generated {len(suggested_queries)} suggested queries for {sheet_name}")
        return suggested_queries 
