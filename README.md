# IBM Cognos Report Tester

A high-quality application for testing Excel reports against SQL databases.

## Features

- Smart Excel parsing and analysis
- SQL query execution with special handling for temporary tables
- Detailed comparison between Excel and SQL data
- Support for all Excel sheets and formats
- Ability to define sheet structure for proper naming and defining of sheet name and account number
- Intelligent data matching algorithms
- Configurable report types and parameters
- Quick **Start Testing** button to launch the automated workflow
- Choose from Light, Dark, Brand, or System interface themes (Brand is the default)

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

### From Source

1. Clone this repository
2. Install the project into your environment:
 ```
  pip install .
  ```
3. Configure your database settings in the application

### Database Settings

The `DatabaseConnector` class accepts the following parameters:

- `server` – SQL Server hostname
- `database` – default database name
- `trusted_connection` – set to `False` to use SQL authentication
- `uid` – SQL username when `trusted_connection` is `False`
- `pwd` – SQL password when `trusted_connection` is `False`

### Using the Executable

For Windows users, a standalone executable is available that doesn't require Python to be installed:

1. Download the latest release
2. Extract the zip file
3. Run the `SOO_PreClose_Tester.exe` file in the extracted folder or use the provided `Run_SOO_PreClose_Tester.bat` file

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

If you're using the executable version, simply double-click the `SOO_PreClose_Tester.exe` file or run the `Run_SOO_PreClose_Tester.bat` batch file.

You can customize the appearance under **Tools -> Settings -> User Interface**.
The Theme drop-down defaults to *Brand* (applying the company's colors) but also allows Light, Dark, or System themes.

To manage account mappings, open **Tools -> Manage Account Categories...**. When this dialog opens the application scans all currently loaded Excel sheets and pre-fills the account list automatically. Columns named `Account` or `CAReportName` are recognized without manual setup. Use the **Add**, **Delete**, and **Rename** buttons to organize both categories and formulas. Renaming a category will also update any formulas that reference it.

### Account Formulas
Formulas entered in this dialog can reference **any** of the category names you create and also any numeric column that exists in the sheet. This makes it easy to compute new values without additional mappings. For example you can define:

```
Gross Margin = Revenue - CostOfSales
Net = Gross - Discounts
```

The above shows both category references (`Revenue`, `CostOfSales`) and direct column references (`Gross`, `Discounts`).

Formulas can optionally be restricted to specific sheets by listing the sheet
names in the **Sheets** column of the *Manage Account Categories* dialog.  When
no sheet is specified, a formula is treated as global and applies to every sheet
of the report.  If calculations are run on results without a sheet column,
all formulas are considered global.

### Report Configurations
Open **Tools → Report Configurations** to define how each report type should be parsed. For every report you can set:
- `header_rows` – the rows that contain column headers
- `skip_rows` – how many rows to skip before reading data
- `first_data_column` – the first column index treated as numeric data
- `center_cell` – optional cell reference used to read the center code

These options control how the `_clean_dataframe` helper processes sheets for that report type.

The application ships with sensible defaults for many reports. In the default
configuration the **Corp SOO** report uses `header_rows` `[5]` and `skip_rows`
set to `7`, meaning the data begins on the eighth row of the sheet.

When Excel files are loaded the analyzer now automatically unmerges any merged
cells.  Only the value from the top-left cell of each merged range is
preserved; the remaining cells are cleared.  This prevents duplicate columns
when headers span multiple columns while still ensuring the cleaning logic
operates on consistent tabular data.

For temp table query testing, you can use the specialized scripts:
```
python src/analyzer/run_real_query.py
```

### Generate the PDF report
First save your comparison results to a CSV file. In the GUI this can be done
via **File -> Export Results**. Scripts under `src/analyzer` can also write the
output directly. When exporting you will be prompted to enter optional testing
notes which appear in the PDF and HTML reports. You may also add an optional
**Issue** column describing each mismatch. The report scripts handle this field
if present. The value for **Issue** can be edited directly in the results table
before exporting. Once you have a `results.csv` (see `sample_data/comparison_results.csv`
for an example that includes the column), run:
```
python src/reporting/generate_pdf_report.py
```
The generated PDF now contains three summary cards with total points, matches
and mismatches. Below the cards a bar chart highlights the accounts with the
largest absolute variance and a small table lists those same accounts.

### Launch the Dashboard
To view mismatches interactively, install the optional dashboard
dependencies and run the Dash server:
```bash
pip install .[dashboard]
python src/reporting/dashboard.py
```

### Running tests
Use `pytest` to run the unit tests:
```
pytest
```
Before running the tests in a fresh environment make sure the required
dependencies are installed. A helper script is provided which installs the
packages listed in `requirements.txt` as well as the lightweight PyQt stubs used
by the tests:

```bash
./scripts/install_test_deps.sh
```

After installing the dependencies the test suite can be executed with
`pytest -q`.

## Building the Executable

If you want to build the executable yourself:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Run the build command:
   ```
   pyinstaller soo_preclose.spec
   ```
   This specification disables UPX compression for greater
   compatibility with some systems.

3. The executable will be generated in the `dist/SOO_PreClose_Tester` directory

## Plugins

The comparison engine can be extended at runtime using plugins. Plugins are
simple Python classes placed in the `src/plugins/` directory or in a custom
directory provided to `ComparisonEngine`. Each plugin subclasses
`plugins.Plugin` and may override `pre_compare` and `post_compare` hooks.

Example plugin that rounds numeric values before comparison:

```python
from src.plugins import Plugin

class RoundingPlugin(Plugin):
    def pre_compare(self, excel_df, sql_df):
        return excel_df.round(2), sql_df.round(2)
```

Create a new file in `src/plugins/` with your plugin class and restart the
application. Plugins can also perform tasks such as account validation or
custom logging.

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

### Key Column Detection
If your Excel export includes the SQL header row (using the "import headers" feature),
the column names will match exactly after loading. In this case the comparison
engine skips its heuristic search entirely and maps columns directly by name.
Otherwise, the engine looks for common keywords when trying to identify the
"Center" and "Account" columns. After normalizing column names, any name
containing the following keywords will be treated as a potential match:

- **Center keywords:** `center`, `facility`, `department`, `dept`
- **Account keywords:** `account`, `careport`, `acct`

If your export uses different wording, ensure that one of these keywords is
present so the automatic matching succeeds.

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
