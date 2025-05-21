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
2. Install the project into your environment:
   ```
   pip install .
   ```
3. Configure your database settings in the application

## Usage

### Launch the GUI
After installation you can open the PyQt interface with:
```
python -m soo_preclose_tester
```
or simply use the console script:
```
soo-preclose-tester
```

For temp table query testing, you can use the specialized scripts:
```
python src/analyzer/run_real_query.py
```

### Generate the PDF report
First save your comparison results to a CSV file. In the GUI this can be done
via **File -> Export Results**. Scripts under `src/analyzer` can also write the
output directly. Once you have a `results.csv` (see
`sample_data/comparison_results.csv` for an example), run:
```
python src/reporting/generate_pdf_report.py
```

### Running tests
Use `pytest` to run the unit tests:
```
pytest
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

This project is licensed under the MIT License.

MIT License

Copyright (c) 2023 Your Organization

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
