# SOO PreClose Report Tester

A high-quality application for testing Excel reports against SQL databases, especially designed for SOO (Statement of Operations) PreClose reports.

## Features

- Smart Excel parsing and analysis
- SQL query execution with special handling for temporary tables
- Detailed comparison between Excel and SQL data
- Support for all Excel sheets and formats
- Intelligent data matching algorithms
- Configurable report types and parameters

## Requirements

- Python 3.6+
- SQL Server with ODBC Driver 17
- Required Python packages:
  - SQLAlchemy
  - PyQt6
  - pandas
  - pyodbc
  - qtawesome

## Installation

1. Clone this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Configure your database settings in the application

## Usage

Run the main application:
```
python main.py
```

For temp table query testing, you can use the specialized scripts:
```
python src/analyzer/run_real_query.py
```

## Project Structure

- `main.py` - Main application entry point
- `src/` - Source code directory
  - `database/` - Database connection and query handling
  - `ui/` - User interface components
  - `analyzer/` - Excel and SQL analysis tools
  - `utils/` - Utility functions and helpers

## Troubleshooting

### Temp Table Issues

SQL Server temporary tables need special handling in multi-statement scripts. This application implements several methods to handle temp tables correctly:

1. `execute_complex_script` - Uses a single transaction approach
2. `direct_execute` - Uses direct ODBC connections with autocommit
3. Custom statement parsing - Splits SQL scripts into separate executable statements

If you're experiencing issues with temp tables, try:
- Adding semicolons between statements
- Using the specialized scripts in the `src/analyzer/` directory

## License

Copyright © 2023-2025