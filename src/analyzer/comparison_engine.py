import pandas as pd
import logging
import re
from pathlib import Path
from src.utils.logging_config import get_logger
from src.plugins import load_plugins, Plugin
from . import (
    column_matching,
    row_comparison,
    sign_flip,
    report_generator,
    discrepancy_classifier,
)

class ComparisonEngine:
    def __init__(self, plugin_dirs=None):
        """Initialize the comparison engine"""
        self.logger = get_logger(__name__)
        self._setup_debug_logger()
        self.comparison_results = {}
        self.tolerance = 0.001  # Default tolerance for numerical comparisons
        self.sign_flip_accounts = set()  # Set of account numbers that should have their signs flipped
        self.plugins = self._load_plugins(plugin_dirs)

    @staticmethod
    def _find_account_columns(columns):
        """Return likely account columns from merged dataframe columns."""
        candidates = [
            "Account",
            "CAReportName",
            "Account Number",
            "Acct",
            "AccountNumber",
        ]
        norm_map = {
            re.sub(r"[\s_]+", "", c).lower(): c for c in candidates
        }
        acct_excel = None
        acct_sql = None
        for col in columns:
            base = col.rsplit("_", 1)[0]
            suffix = col.rsplit("_", 1)[-1]
            norm = re.sub(r"[\s_]+", "", base).lower()
            if norm in norm_map:
                if suffix == "excel":
                    acct_excel = col
                elif suffix == "sql":
                    acct_sql = col
        return acct_excel, acct_sql

    def _setup_debug_logger(self):
        """Create a dedicated debug logger for row level comparison."""
        file_handler = logging.FileHandler('comparison_debug.log', mode='w')
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)

        self.debug_logger = logging.getLogger('comparison_debug')
        self.debug_logger.handlers = []
        self.debug_logger.addHandler(file_handler)
        self.debug_logger.setLevel(logging.DEBUG)

    def _load_plugins(self, plugin_dirs):
        """Load comparison plugins from the given directories."""
        if plugin_dirs is None:
            plugin_dirs = [Path(__file__).resolve().parents[1] / "plugins"]
        elif isinstance(plugin_dirs, (str, Path)):
            plugin_dirs = [plugin_dirs]
        plugins = load_plugins(plugin_dirs)
        if plugins:
            self.logger.info(f"Loaded {len(plugins)} plugins")
        return plugins
    
    def set_tolerance(self, tolerance):
        """Set the tolerance for numerical comparisons"""
        self.tolerance = tolerance
        self.logger.info(f"Comparison tolerance set to {tolerance}")
    
    def set_sign_flip_accounts(self, accounts):
        """Set the list of accounts that should have their signs flipped during comparison"""
        self.sign_flip_accounts = set(accounts) if accounts else set()
        self.logger.info(f"Set sign flip accounts: {self.sign_flip_accounts}")
    
    def _should_flip_sign(self, column_name):
        """Check if a column should have its sign flipped based on account number"""
        # Check if the column name contains any of the sign flip account numbers
        return any(account in str(column_name) for account in self.sign_flip_accounts)
    
    def normalize_column_names(self, columns):
        """Normalize column names for comparison."""
        return column_matching.normalize_column_names(columns)
    
    def find_matching_columns(self, excel_columns, sql_columns, threshold=0.6):
        """Find matching columns between Excel and SQL results."""
        mappings = column_matching.find_matching_columns(excel_columns, sql_columns, threshold)

        self.logger.info(f"Found {len(mappings)} column mappings between Excel and SQL data")
        for _, mapping in mappings.items():
            self.logger.info(
                f"Mapped '{mapping['excel_column']}' to '{mapping['sql_column']}' (score: {mapping['match_score']:.2f})"
            )
        return mappings
    
    def compare_dataframes(self, excel_df, sql_df, column_mappings=None):
        """Compare Excel and SQL dataframes and identify differences, including duplicate key detection and per-row sign flip"""
        if excel_df.empty or sql_df.empty:
            self.logger.warning("One or both dataframes are empty")
            return {"error": "One or both dataframes are empty"}

        # Store last compared dataframes for later report generation
        self._last_excel_df = excel_df.copy()
        self._last_sql_df = sql_df.copy()
        
        # Print DataFrame info for debugging
        self.logger.info(f"Excel DataFrame info: {excel_df.shape}, columns: {excel_df.columns.tolist()}")
        self.logger.info(f"SQL DataFrame info: {sql_df.shape}, columns: {sql_df.columns.tolist()}")
        
        # Clean up column names to handle any whitespace issues
        excel_df.columns = [str(col).strip() for col in excel_df.columns]
        sql_df.columns = [str(col).strip() for col in sql_df.columns]

        # Run plugin pre-comparison hooks
        for plugin in self.plugins:
            try:
                excel_df, sql_df = plugin.pre_compare(excel_df, sql_df)
            except Exception as e:
                self.logger.warning(f"Plugin {plugin.__class__.__name__} failed in pre_compare: {e}")
        
        # If no column mappings provided, check for exact header match first
        if column_mappings is None:
            if list(excel_df.columns) == list(sql_df.columns):
                column_mappings = {
                    i: {
                        "excel_column": col,
                        "sql_column": col,
                        "match_score": 1.0,
                    }
                    for i, col in enumerate(excel_df.columns)
                }
            else:
                column_mappings = self.find_matching_columns(
                    excel_df.columns, sql_df.columns
                )
        
        if not column_mappings:
            self.logger.warning("No matching columns found between Excel and SQL data")
            return {"error": "No matching columns found"}
        
        # Log the column mappings for debugging
        self.logger.info("Column mappings:")
        for excel_idx, mapping in column_mappings.items():
            self.logger.info(f"Excel: '{mapping['excel_column']}' -> SQL: '{mapping['sql_column']}' (score: {mapping['match_score']:.2f})")
        
        # Try to identify key columns for joining
        key_columns = self._identify_key_columns(excel_df, sql_df, column_mappings)
        if not key_columns:
            self.logger.warning("Could not identify key columns for joining")
            return {"error": "Could not identify key columns for joining"}
            
        self.logger.info(f"Using key columns for joining: {key_columns}")
        
        # Create join keys with normalized case/whitespace
        excel_keys = (
            excel_df[key_columns['excel']]
            .astype(str)
            .apply(lambda s: s.str.strip().str.lower())
            .agg('-'.join, axis=1)
        )
        sql_keys = (
            sql_df[key_columns['sql']]
            .astype(str)
            .apply(lambda s: s.str.strip().str.lower())
            .agg('-'.join, axis=1)
        )
        
        # --- Duplicate key detection ---
        excel_dup_keys = excel_keys[excel_keys.duplicated(keep=False)]
        sql_dup_keys = sql_keys[sql_keys.duplicated(keep=False)]
        
        duplicate_key_report = {
            "excel": excel_dup_keys.value_counts().to_dict() if not excel_dup_keys.empty else {},
            "sql": sql_dup_keys.value_counts().to_dict() if not sql_dup_keys.empty else {}
        }
        
        # Add keys to dataframes without mutating the originals
        excel_df = excel_df.copy()
        sql_df = sql_df.copy()
        excel_df['_join_key'] = excel_keys
        sql_df['_join_key'] = sql_keys
        
        # Merge dataframes on join key
        merged_df = pd.merge(
            excel_df,
            sql_df,
            on='_join_key',
            how='outer',
            suffixes=('_excel', '_sql')
        )
        
        # --- Prepare for per-row sign flip ---
        account_col_excel, account_col_sql = self._find_account_columns(merged_df.columns)
        
        # Log merge results
        self.logger.info(f"Merge results - Total rows: {len(merged_df)}")
        self.logger.info(f"Excel-only rows: {len(merged_df[merged_df['_join_key'].isin(excel_keys) & ~merged_df['_join_key'].isin(sql_keys)])}")
        self.logger.info(f"SQL-only rows: {len(merged_df[merged_df['_join_key'].isin(sql_keys) & ~merged_df['_join_key'].isin(excel_keys)])}")
        self.logger.info(f"Matched rows: {len(merged_df[merged_df['_join_key'].isin(excel_keys) & merged_df['_join_key'].isin(sql_keys)])}")
        
        results = {
            "column_mappings": column_mappings,
            "row_count_match": excel_df.shape[0] == sql_df.shape[0],
            "row_counts": {
                "excel": excel_df.shape[0],
                "sql": sql_df.shape[0],
                "matched": len(merged_df[merged_df['_join_key'].isin(excel_keys) & merged_df['_join_key'].isin(sql_keys)])
            },
            "column_comparisons": {},
            "summary": {
                "total_cells": 0,
                "matching_cells": 0,
                "mismatch_cells": 0,
                "mismatch_percentage": 0
            },
            "duplicate_keys": duplicate_key_report,
            "suggested_sign_flips": set(),
        }
        
        # Prepare sign flip accounts as a set of stripped strings
        sign_flip_accounts_str = set(str(acct).strip() for acct in self.sign_flip_accounts)
        if sign_flip_accounts_str:
            self.logger.info(f"Sign flip accounts (as strings): {sign_flip_accounts_str}")
        
        # Compare each mapped column
        for excel_idx, mapping in column_mappings.items():
            excel_col = mapping["excel_column"]
            sql_col = mapping["sql_column"]
            
            # Get the corresponding columns from merged dataframe
            excel_merged_col = f"{excel_col}_excel"
            sql_merged_col = f"{sql_col}_sql"
            
            if excel_merged_col not in merged_df.columns or sql_merged_col not in merged_df.columns:
                self.logger.warning(f"Mapped column not found in merged data: Excel={excel_merged_col}, SQL={sql_merged_col}")
                continue
            
            # Get series from merged dataframe
            excel_series = merged_df[excel_merged_col]
            sql_series = merged_df[sql_merged_col]
            
            # Get account/identifier series for this row
            if account_col_sql:
                account_series = merged_df[account_col_sql].astype(str)
            elif account_col_excel:
                account_series = merged_df[account_col_excel].astype(str)
            else:
                account_series = pd.Series([None]*len(merged_df))
            
            # Log column data types and sample values for debugging
            self.logger.info(f"\nComparing column: {excel_col} -> {sql_col}")
            self.logger.info(f"Excel dtype: {excel_series.dtype}, SQL dtype: {sql_series.dtype}")
            self.logger.info(f"Excel sample values: {excel_series.head().tolist()}")
            self.logger.info(f"SQL sample values: {sql_series.head().tolist()}")
            
            # Compare only matched rows
            matched_mask = merged_df['_join_key'].isin(excel_keys) & merged_df['_join_key'].isin(sql_keys)
            excel_series = excel_series[matched_mask]
            sql_series = sql_series[matched_mask]
            account_series = account_series[matched_mask]
            
            col_results = row_comparison.compare_series(
                excel_series,
                sql_series,
                account_series,
                tolerance=self.tolerance,
                sign_flip_accounts=self.sign_flip_accounts,
            )

            # Merge any suggested sign flips
            suggestions = col_results.pop("sign_flip_candidates", set())
            if suggestions:
                results["suggested_sign_flips"].update(suggestions)

            total_cells = col_results["match_count"] + col_results["mismatch_count"]
            col_results["match_percentage"] = (
                col_results["match_count"] / total_cells * 100
            ) if total_cells > 0 else 0
            
            # Log column comparison results
            self.logger.info(f"Column comparison results for {excel_col}:")
            self.logger.info(f"Matches: {col_results['match_count']}, Mismatches: {col_results['mismatch_count']}")
            self.logger.info(f"Match percentage: {col_results['match_percentage']:.2f}%")
            
            # Add to column comparisons
            results["column_comparisons"][excel_col] = col_results
            
            # Update summary
            results["summary"]["total_cells"] += total_cells
            results["summary"]["matching_cells"] += col_results["match_count"]
            results["summary"]["mismatch_cells"] += col_results["mismatch_count"]
        
        # Calculate overall mismatch percentage
        if results["summary"]["total_cells"] > 0:
            results["summary"]["mismatch_percentage"] = (
                results["summary"]["mismatch_cells"] / results["summary"]["total_cells"] * 100
            )
        
        # Overall assessment
        results["summary"]["overall_match"] = results["summary"]["mismatch_percentage"] < 1  # Less than 1% mismatch
        
        self.logger.info(f"Comparison completed with {results['summary']['mismatch_percentage']:.2f}% mismatch")

        # Identify account level discrepancies for executive summary
        try:
            discrepancies = self.identify_account_discrepancies(excel_df, sql_df, column_mappings)
        except Exception as e:
            self.logger.warning(f"Account discrepancy analysis failed: {e}")
            discrepancies = pd.DataFrame()

        results["account_discrepancies"] = discrepancies
        if (
            isinstance(discrepancies, pd.DataFrame)
            and not discrepancies.empty
            and "Severity" in discrepancies.columns
        ):
            results["discrepancy_severity"] = discrepancies["Severity"].tolist()
        else:
            results["discrepancy_severity"] = []

        # Run plugin post-comparison hooks
        for plugin in self.plugins:
            try:
                results = plugin.post_compare(results)
            except Exception as e:
                self.logger.warning(
                    f"Plugin {plugin.__class__.__name__} failed in post_compare: {e}"
                )

        # Store results
        self.comparison_results = results

        return results
    
    def _identify_key_columns(self, excel_df, sql_df, column_mappings):
        """Identify key columns for joining Excel and SQL data"""

        def _norm(name: str) -> str:
            return re.sub(r"[\s_]+", "", str(name)).lower()

        center_synonyms = {
            "center",
            "centernumber",
            "center number",
            "facility",
            "facilitynumber",
            "facility number",
            "sheet",
            "sheetname",
        }
        acct_synonyms = {
            "careportname",
            "account",
            "accountnumber",
            "account number",
            "acct",
        }
        center_keywords = [
            "center",
            "facility",
            "department",
            "dept",
            "sheet",
        ]
        acct_keywords = [
            "account",
            "careport",
            "acct",
        ]

        # Short-circuit if the headers already match exactly
        if list(excel_df.columns) == list(sql_df.columns):
            key_columns = [
                col
                for col in excel_df.columns
                if _norm(col) in center_synonyms or _norm(col) in acct_synonyms
            ]

            if key_columns:
                return {"excel": key_columns, "sql": key_columns}

            def _is_non_numeric(series):
                try:
                    ratio = pd.to_numeric(series, errors="coerce").notna().mean()
                    return ratio < 0.5
                except Exception:
                    return True

            text_cols = [
                col
                for col in excel_df.columns
                if _is_non_numeric(excel_df[col]) and _is_non_numeric(sql_df[col])
            ]
            if text_cols:
                return {"excel": text_cols, "sql": text_cols}

            return None

        # First try to find Center and CAReportName columns
        key_columns = {"excel": [], "sql": []}

        center_found = False
        acct_found = False

        for mapping in column_mappings.values():
            if _norm(mapping["excel_column"]) in center_synonyms:
                key_columns["excel"].append(mapping["excel_column"])
                key_columns["sql"].append(mapping["sql_column"])
                center_found = True
                break

        for mapping in column_mappings.values():
            if _norm(mapping["excel_column"]) in acct_synonyms:
                key_columns["excel"].append(mapping["excel_column"])
                key_columns["sql"].append(mapping["sql_column"])
                acct_found = True
                break

        # Fallback: check for keywords contained in the normalized names
        if not center_found:
            for mapping in column_mappings.values():
                norm = _norm(mapping["excel_column"])
                if any(kw in norm for kw in center_keywords):
                    key_columns["excel"].append(mapping["excel_column"])
                    key_columns["sql"].append(mapping["sql_column"])
                    center_found = True
                    break

        if not acct_found:
            for mapping in column_mappings.values():
                norm = _norm(mapping["excel_column"])
                if any(kw in norm for kw in acct_keywords):
                    key_columns["excel"].append(mapping["excel_column"])
                    key_columns["sql"].append(mapping["sql_column"])
                    acct_found = True
                    break

        if center_found or acct_found:
            return key_columns
        

        # If we didn't find both key columns, try to find any columns that match
        # exactly. Filter out columns that appear to be mostly numeric to avoid
        # using value columns as join keys.
        def _is_non_numeric(series):
            try:
                ratio = pd.to_numeric(series, errors="coerce").notna().mean()
                return ratio < 0.5
            except Exception:
                return True

        text_matches = []
        for mapping in column_mappings.values():
            if mapping['match_score'] == 1.0:
                ec = mapping['excel_column']
                sc = mapping['sql_column']
                if _is_non_numeric(excel_df[ec]) and _is_non_numeric(sql_df[sc]):
                    text_matches.append({'excel': ec, 'sql': sc})

        if text_matches:
            return {
                'excel': [m['excel'] for m in text_matches],
                'sql': [m['sql'] for m in text_matches]
            }

        return None

    def identify_account_discrepancies(self, excel_df, sql_df, column_mappings=None):
        """Identify accounts with large variances or missing rows.

        The method groups data by Center and Account (CAReportName) and compares
        the total numeric value for the first detected numeric column. Accounts
        with totals that differ by more than the comparison tolerance or that
        are missing in one of the sources are returned.
        """

        if column_mappings is None:
            column_mappings = self.find_matching_columns(excel_df.columns, sql_df.columns)

        key_cols = self._identify_key_columns(excel_df, sql_df, column_mappings)
        if not key_cols or len(key_cols['excel']) < 2:
            self.logger.warning("Could not identify key columns for discrepancy analysis")
            return pd.DataFrame(columns=[
                'Center', 'Account', 'Excel Total', 'SQL Total',
                'Variance', 'Missing in Excel', 'Missing in SQL'
            ])

        center_excel, account_excel = key_cols['excel'][:2]
        center_sql, account_sql = key_cols['sql'][:2]

        # Determine a numeric column to sum
        numeric_pair = None
        for mapping in column_mappings.values():
            if mapping['excel_column'] in key_cols['excel']:
                continue
            try:
                excel_ratio = pd.to_numeric(excel_df[mapping['excel_column']], errors='coerce').notna().mean()
                sql_ratio = pd.to_numeric(sql_df[mapping['sql_column']], errors='coerce').notna().mean()
                if excel_ratio > 0.5 and sql_ratio > 0.5:
                    numeric_pair = (mapping['excel_column'], mapping['sql_column'])
                    break
            except Exception:
                continue

        if not numeric_pair:
            self.logger.warning("No numeric columns found for discrepancy analysis")
            return pd.DataFrame(columns=[
                'Center', 'Account', 'Excel Total', 'SQL Total',
                'Variance', 'Missing in Excel', 'Missing in SQL'
            ])

        excel_col, sql_col = numeric_pair

        excel_tmp = excel_df[[center_excel, account_excel, excel_col]].copy()
        sql_tmp = sql_df[[center_sql, account_sql, sql_col]].copy()
        excel_tmp.columns = ['Center', 'Account', 'Excel']
        sql_tmp.columns = ['Center', 'Account', 'SQL']

        excel_tmp['Excel'] = pd.to_numeric(excel_tmp['Excel'], errors='coerce')
        sql_tmp['SQL'] = pd.to_numeric(sql_tmp['SQL'], errors='coerce')

        sign_flip_set = set(str(a).strip() for a in self.sign_flip_accounts)
        if sign_flip_set:
            sql_tmp.loc[sql_tmp['Account'].astype(str).isin(sign_flip_set), 'SQL'] *= -1

        excel_group = excel_tmp.groupby(['Center', 'Account'], dropna=False)['Excel'].sum().reset_index()
        sql_group = sql_tmp.groupby(['Center', 'Account'], dropna=False)['SQL'].sum().reset_index()

        merged = pd.merge(excel_group, sql_group, on=['Center', 'Account'], how='outer', indicator=True)
        merged['Excel'] = merged['Excel'].fillna(0)
        merged['SQL'] = merged['SQL'].fillna(0)
        merged['Variance'] = merged['Excel'] - merged['SQL']
        merged['Missing in Excel'] = merged['_merge'] == 'right_only'
        merged['Missing in SQL'] = merged['_merge'] == 'left_only'

        tol = self.tolerance
        def needs_flag(row):
            if row['Missing in Excel'] or row['Missing in SQL']:
                return True
            max_val = max(abs(row['Excel']), abs(row['SQL']))
            threshold = tol * max_val
            return abs(row['Variance']) > threshold

        flagged = merged[merged.apply(needs_flag, axis=1)].copy()
        flagged.drop(columns=['_merge'], inplace=True)

        # Classify discrepancies by severity
        flagged = discrepancy_classifier.classify(flagged)

        return flagged

    def explain_variances(self, discrepancies_df):
        """Return human readable messages explaining each discrepancy."""
        messages = []
        if discrepancies_df is None or discrepancies_df.empty:
            return messages

        for _, row in discrepancies_df.iterrows():
            center = row.get("Center")
            account = row.get("Account")
            variance = row.get("Variance")
            if row.get("Missing in Excel"):
                msg = f"Account {account} in Center {center} is missing in Excel"
            elif row.get("Missing in SQL"):
                msg = (
                    f"Variance of {variance} due to missing in SQL for Account {account} in Center {center}"
                )
            else:
                msg = f"Variance of {variance} for Account {account} in Center {center}"
            messages.append(msg)

        return messages

    def generate_comparison_report(self, sheet_name, comparison_results=None, mismatches_df=None, fmt="markdown"):
        """Generate a comparison report in markdown or HTML format."""
        if comparison_results is None:
            comparison_results = self.comparison_results
        if not comparison_results:
            self.logger.warning("No comparison results available")
            return "No comparison results available."

        if mismatches_df is None:
            try:
                mismatches_df = self.generate_detailed_comparison_dataframe(
                    sheet_name,
                    getattr(self, "_last_excel_df", None),
                    getattr(self, "_last_sql_df", None),
                )
            except Exception:
                mismatches_df = None

        suggested = comparison_results.get("suggested_sign_flips", set())
        return report_generator.generate_report(
            sheet_name,
            comparison_results,
            mismatches_df,
            self.sign_flip_accounts,
            suggested,
            fmt=fmt,
        )

    def generate_detailed_comparison_dataframe(
        self,
        sheet_name,
        excel_df,
        sql_df,
        column_mappings=None,
        report_type=None,
        pivot_results=False,
    ):
        """Generate a DataFrame with all matches, mismatches, and missing records
        for export.

        ``report_type`` allows callers to omit certain columns (e.g. ``Center`` or
        sheet name) when not relevant to the report being exported.
        """
        # Run the comparison to get the merged DataFrame and mappings
        if column_mappings is None:
            column_mappings = self.find_matching_columns(excel_df.columns, sql_df.columns)
        key_columns = self._identify_key_columns(excel_df, sql_df, column_mappings)
        if not key_columns:
            raise ValueError("Could not identify key columns for joining")

        # Validate input DataFrames before building join keys
        if excel_df.empty or sql_df.empty:
            self.logger.warning("One or both dataframes are empty")
            return pd.DataFrame()

        missing_excel = [col for col in key_columns['excel'] if col not in excel_df.columns]
        missing_sql = [col for col in key_columns['sql'] if col not in sql_df.columns]
        if missing_excel or missing_sql:
            self.logger.warning(
                "Key columns missing from dataframes. Excel missing: %s; SQL missing: %s",
                missing_excel,
                missing_sql,
            )
            raise ValueError("Key columns missing from dataframes")
        
        # Prepare sign flip accounts as a set of stripped strings
        sign_flip_accounts_str = set(str(acct).strip() for acct in getattr(self, 'sign_flip_accounts', set()))
        
        # Create join keys with normalized case/whitespace
        excel_keys = (
            excel_df[key_columns['excel']]
            .astype(str)
            .apply(lambda s: s.str.strip().str.lower())
            .agg('-'.join, axis=1)
        )
        sql_keys = (
            sql_df[key_columns['sql']]
            .astype(str)
            .apply(lambda s: s.str.strip().str.lower())
            .agg('-'.join, axis=1)
        )
        
        excel_df = excel_df.copy()
        sql_df = sql_df.copy()
        excel_df['_join_key'] = excel_keys
        sql_df['_join_key'] = sql_keys
        
        merged_df = pd.merge(
            excel_df,
            sql_df,
            on='_join_key',
            how='outer',
            suffixes=('_excel', '_sql')
        )
        
        # Try to find the account column in the merged dataframe
        account_col_excel, account_col_sql = self._find_account_columns(merged_df.columns)
        
        include_center = report_type not in ("SOO MFR", "Corp SOO")
        # Always include the sheet name so exports contain a reference to
        # which tab the result came from.
        include_sheet = True

        output_rows = []
        for excel_idx, mapping in column_mappings.items():
            excel_col = mapping["excel_column"]
            sql_col = mapping["sql_column"]
            excel_merged_col = f"{excel_col}_excel"
            sql_merged_col = f"{sql_col}_sql"
            if excel_merged_col not in merged_df.columns or sql_merged_col not in merged_df.columns:
                continue
            for idx, row in merged_df.iterrows():
                center = row.get('Center_excel') or row.get('Center_sql') or ''
                careport = (
                    row.get('CAReportName_excel')
                    or row.get('CAReportName_sql')
                    or (row.get(account_col_excel) if account_col_excel else None)
                    or (row.get(account_col_sql) if account_col_sql else None)
                    or ''
                )
                # Report the SQL column name in the output so mismatches show
                # which field in the database caused the difference.
                field = sql_col
                excel_val = row.get(excel_merged_col, None)
                sql_val = row.get(sql_merged_col, None)
                # Get account value for sign flip
                acct = row.get(account_col_sql) or row.get(account_col_excel) or ''
                acct_str = str(acct).strip()
                match = re.search(r'\d{4}-\d{4}', acct_str)
                acct_extracted = match.group(0) if match else acct_str
                # Apply sign flip if needed
                sql_val_flipped = sql_val
                try:
                    if sql_val is not None and sql_val != 'NULL' and acct_extracted in sign_flip_accounts_str and pd.notna(sql_val):
                        sql_val_flipped = -float(sql_val)
                    elif sql_val is not None and sql_val != 'NULL' and pd.notna(sql_val):
                        sql_val_flipped = float(sql_val)
                except Exception:
                    pass
                # Determine result
                if pd.isna(excel_val) and pd.isna(sql_val):
                    continue  # Both missing, skip
                elif pd.isna(excel_val):
                    result = 'Missing in Excel'
                    variance = ''
                    excel_val_out = 'NULL'
                    sql_val_out = sql_val_flipped
                elif pd.isna(sql_val):
                    result = 'Missing in Database'
                    variance = ''
                    excel_val_out = excel_val
                    sql_val_out = 'NULL'
                else:
                    try:
                        excel_num = float(excel_val)
                        sql_num = float(sql_val_flipped)
                        variance = excel_num - sql_num
                        is_match = abs(variance) <= self.tolerance
                    except Exception:
                        variance = ''
                        is_match = str(excel_val).strip() == str(sql_val_flipped).strip()
                    result = 'Match' if is_match else 'Does Not Match'
                    excel_val_out = excel_val
                    sql_val_out = sql_val_flipped
                row_data = {
                    'Field': field,
                    'Excel Value': excel_val_out,
                    'DataBase Value': sql_val_out,
                    'Variance': variance,
                    'Result': result,
                }
                # Describe any problem in a human readable form
                row_data['Issue'] = result if result != 'Match' else ''
                if include_sheet:
                    row_data['Sheet'] = sheet_name
                if include_center:
                    row_data['Center'] = center
                row_data['CAReport Name'] = careport
                output_rows.append(row_data)

        df = pd.DataFrame(output_rows)
        if pivot_results and not df.empty:
            id_cols = [c for c in ['Sheet', 'Center', 'CAReport Name'] if c in df.columns]
            value_cols = ['Excel Value', 'DataBase Value', 'Variance', 'Result']
            pivot_df = df.pivot_table(index=id_cols, columns='Field', values=value_cols, aggfunc='first')
            pivot_df.columns = [
                f"{field} {val_type.replace('Excel Value', 'Excel').replace('DataBase Value', 'Database')}"
                for val_type, field in pivot_df.columns
            ]
            pivot_df = pivot_df.reset_index()
            df = pivot_df

        # Normalize sheet column to ensure consistent output
        sheet_synonyms = [
            c for c in df.columns
            if re.sub(r"[\s_]+", "", str(c)).lower() in ("sheet", "sheetname")
        ]
        if sheet_synonyms:
            main_col = sheet_synonyms[0]
            for col in sheet_synonyms[1:]:
                if col != main_col:
                    df = df.drop(columns=col)
            if main_col != 'Sheet':
                df = df.rename(columns={main_col: 'Sheet'})
            df['Sheet'] = sheet_name
        else:
            df.insert(0, 'Sheet', sheet_name)

        return df
