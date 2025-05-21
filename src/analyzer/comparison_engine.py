import pandas as pd
import numpy as np
from difflib import SequenceMatcher
import logging
from src.utils.logging_config import get_logger
import re

class ComparisonEngine:
    def __init__(self):
        """Initialize the comparison engine"""
        self.logger = get_logger(__name__)
        self._setup_debug_logger()
        self.comparison_results = {}
        self.tolerance = 0.001  # Default tolerance for numerical comparisons
        self.sign_flip_accounts = set()  # Set of account numbers that should have their signs flipped

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
        """Normalize column names for comparison"""
        normalized = []
        for col in columns:
            if not isinstance(col, str):
                col = str(col)
            
            # Remove special characters and standardize spacing
            col = re.sub(r'[^\w\s]', ' ', col)
            # Remove common words that don't add meaning (e.g., "the", "and", etc.)
            col = re.sub(r'\b(the|and|or|of|in|for|to|a|an)\b', '', col, flags=re.IGNORECASE)
            # Normalize whitespace
            col = re.sub(r'\s+', ' ', col).strip().lower()
            normalized.append(col)
        
        return normalized
    
    def find_matching_columns(self, excel_columns, sql_columns, threshold=0.6):
        """Find matching columns between Excel and SQL results"""
        excel_normalized = self.normalize_column_names(excel_columns)
        sql_normalized = self.normalize_column_names(sql_columns)
        
        # Log column names for debugging
        self.logger.info(f"Excel columns: {excel_columns}")
        self.logger.info(f"SQL columns: {sql_columns}")
        self.logger.info(f"Normalized Excel columns: {excel_normalized}")
        self.logger.info(f"Normalized SQL columns: {sql_normalized}")
        
        # Check for exact matches first (case-insensitive)
        mappings = {}
        used_sql_indices = set()
        
        # First pass: look for exact matches after normalization
        for i, excel_col in enumerate(excel_normalized):
            for j, sql_col in enumerate(sql_normalized):
                if j in used_sql_indices:
                    continue
                    
                if excel_col == sql_col:
                    mappings[i] = {
                        "excel_column": excel_columns[i],
                        "sql_column": sql_columns[j],
                        "match_score": 1.0
                    }
                    used_sql_indices.add(j)
                    break
        
        # Second pass: fuzzy matching for remaining columns
        for i, excel_col in enumerate(excel_normalized):
            if i in mappings:
                continue
                
            best_match = None
            best_score = threshold
            
            for j, sql_col in enumerate(sql_normalized):
                if j in used_sql_indices:
                    continue
                    
                # Try different fuzzy matching techniques
                
                # 1. Sequence matcher ratio
                score1 = SequenceMatcher(None, excel_col, sql_col).ratio()
                
                # 2. Check if one is substring of the other
                excel_words = set(excel_col.split())
                sql_words = set(sql_col.split())
                common_words = excel_words.intersection(sql_words)
                
                # Calculate word overlap ratio
                score2 = len(common_words) / max(len(excel_words), len(sql_words)) if excel_words or sql_words else 0
                
                # 3. Check for substring matches
                score3 = 0
                if excel_col in sql_col or sql_col in excel_col:
                    # Calculate length ratio of the shorter to longer string
                    min_len = min(len(excel_col), len(sql_col))
                    max_len = max(len(excel_col), len(sql_col))
                    score3 = min_len / max_len if max_len > 0 else 0
                
                # Take the best score
                score = max(score1, score2, score3)
                
                if score > best_score:
                    best_score = score
                    best_match = j
            
            if best_match is not None:
                mappings[i] = {
                    "excel_column": excel_columns[i],
                    "sql_column": sql_columns[best_match],
                    "match_score": best_score
                }
                used_sql_indices.add(best_match)
        
        # If still no mappings, try a very low threshold for any column that might be similar
        if not mappings:
            fallback_threshold = 0.3  # Very low threshold for last resort matching
            for i, excel_col in enumerate(excel_normalized):
                best_match = None
                best_score = fallback_threshold
                
                for j, sql_col in enumerate(sql_normalized):
                    if j in used_sql_indices:
                        continue
                        
                    score = SequenceMatcher(None, excel_col, sql_col).ratio()
                    if score > best_score:
                        best_score = score
                        best_match = j
                
                if best_match is not None:
                    mappings[i] = {
                        "excel_column": excel_columns[i],
                        "sql_column": sql_columns[best_match],
                        "match_score": best_score
                    }
                    used_sql_indices.add(best_match)
        
        # Last resort: if Sheet_Name is in excel columns, try to match by position
        if "Sheet_Name" in excel_columns and not mappings:
            sheet_name_idx = list(excel_columns).index("Sheet_Name")
            # Skip Sheet_Name column and match others by position
            for i, excel_col in enumerate(excel_columns):
                if i == sheet_name_idx:
                    continue  # Skip Sheet_Name column
                
                # Calculate the adjusted SQL index
                j = i if i < sheet_name_idx else i - 1
                if j < len(sql_columns):
                    mappings[i] = {
                        "excel_column": excel_columns[i],
                        "sql_column": sql_columns[j],
                        "match_score": 0.5  # Default score for position-based matching
                    }
        
        self.logger.info(f"Found {len(mappings)} column mappings between Excel and SQL data")
        for i, mapping in mappings.items():
            self.logger.info(f"Mapped '{mapping['excel_column']}' to '{mapping['sql_column']}' (score: {mapping['match_score']:.2f})")
        
        return mappings
    
    def compare_dataframes(self, excel_df, sql_df, column_mappings=None):
        """Compare Excel and SQL dataframes and identify differences, including duplicate key detection and per-row sign flip"""
        if excel_df.empty or sql_df.empty:
            self.logger.warning("One or both dataframes are empty")
            return {"error": "One or both dataframes are empty"}
        
        # Print DataFrame info for debugging
        self.logger.info(f"Excel DataFrame info: {excel_df.shape}, columns: {excel_df.columns.tolist()}")
        self.logger.info(f"SQL DataFrame info: {sql_df.shape}, columns: {sql_df.columns.tolist()}")
        
        # Clean up column names to handle any whitespace issues
        excel_df.columns = [str(col).strip() for col in excel_df.columns]
        sql_df.columns = [str(col).strip() for col in sql_df.columns]
        
        # If no column mappings provided, try to create them
        if column_mappings is None:
            column_mappings = self.find_matching_columns(excel_df.columns, sql_df.columns)
        
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
        
        # Create join keys
        excel_keys = excel_df[key_columns['excel']].astype(str).agg('-'.join, axis=1)
        sql_keys = sql_df[key_columns['sql']].astype(str).agg('-'.join, axis=1)
        
        # --- Duplicate key detection ---
        excel_dup_keys = excel_keys[excel_keys.duplicated(keep=False)]
        sql_dup_keys = sql_keys[sql_keys.duplicated(keep=False)]
        
        duplicate_key_report = {
            "excel": excel_dup_keys.value_counts().to_dict() if not excel_dup_keys.empty else {},
            "sql": sql_dup_keys.value_counts().to_dict() if not sql_dup_keys.empty else {}
        }
        
        # Add keys to dataframes
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
        # Try to find the account column in the merged dataframe
        account_col_excel = None
        account_col_sql = None
        for col in ['Account', 'CAReportName', 'Account Number', 'Acct', 'AccountNumber']:
            if f'{col}_excel' in merged_df.columns:
                account_col_excel = f'{col}_excel'
            if f'{col}_sql' in merged_df.columns:
                account_col_sql = f'{col}_sql'
        
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
            "duplicate_keys": duplicate_key_report
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
            
            # Initialize comparison results for this column
            col_results = {
                "is_numeric": False,
                "match_count": 0,
                "mismatch_count": 0,
                "mismatch_rows": [],
                "null_mismatch_count": 0,
                "sign_flipped": bool(self.sign_flip_accounts)
            }
            
            # Compare only matched rows
            matched_mask = merged_df['_join_key'].isin(excel_keys) & merged_df['_join_key'].isin(sql_keys)
            excel_series = excel_series[matched_mask]
            sql_series = sql_series[matched_mask]
            account_series = account_series[matched_mask]
            
            # Attempt to convert both to numeric if they appear to be numeric
            try:
                excel_numeric = pd.to_numeric(excel_series, errors='coerce')
                sql_numeric = pd.to_numeric(sql_series, errors='coerce')
                excel_numeric_ratio = excel_numeric.notna().mean()
                sql_numeric_ratio = sql_numeric.notna().mean()
                self.logger.info(f"Numeric conversion ratios - Excel: {excel_numeric_ratio:.2f}, SQL: {sql_numeric_ratio:.2f}")
                if excel_numeric_ratio > 0.5 and sql_numeric_ratio > 0.5:
                    col_results["is_numeric"] = True
                    excel_series = excel_numeric
                    sql_series = sql_numeric
            except Exception as e:
                self.logger.debug(f"Numeric conversion failed for {excel_col}/{sql_col}: {str(e)}")
            
            # Compare values, applying sign flip per row if needed
            for i, (excel_val, sql_val, acct) in enumerate(zip(excel_series, sql_series, account_series)):
                # Check for null values
                excel_null = pd.isna(excel_val)
                sql_null = pd.isna(sql_val)
                
                # Robust account matching: extract account number if needed
                acct_str = str(acct).strip()
                # Try to extract xxxx-xxxx pattern from the string
                match = re.search(r'\d{4}-\d{4}', acct_str)
                acct_extracted = match.group(0) if match else acct_str
                flip = col_results["is_numeric"] and acct_extracted in sign_flip_accounts_str and pd.notna(sql_val)
                # Log every row to the debug log file
                self.debug_logger.info(f"Row {i}: AccountRaw='{acct_str}', AccountExtracted='{acct_extracted}', Excel={excel_val}, SQL(before flip)={sql_val}, Flip={flip}")
                if flip:
                    sql_val = -sql_val
                    self.debug_logger.info(f"Row {i}: SQL value after flip: {sql_val}")
                
                if excel_null and sql_null:
                    col_results["match_count"] += 1
                elif excel_null != sql_null:
                    col_results["null_mismatch_count"] += 1
                    col_results["mismatch_count"] += 1
                    col_results["mismatch_rows"].append({
                        "row": i,
                        "excel_value": excel_val,
                        "sql_value": sql_val,
                        "difference": "NULL mismatch"
                    })
                elif col_results["is_numeric"]:
                    try:
                        excel_num = float(excel_val)
                        sql_num = float(sql_val)
                        abs_diff = abs(excel_num - sql_num)
                        if abs(excel_num) > 1.0 or abs(sql_num) > 1.0:
                            max_val = max(abs(excel_num), abs(sql_num))
                            rel_diff = abs_diff / max_val if max_val > 0 else abs_diff
                            is_match = rel_diff <= self.tolerance
                            if not is_match and i < 5:
                                self.logger.info(f"Row {i} mismatch - Excel: {excel_num}, SQL: {sql_num}, "
                                               f"Abs diff: {abs_diff}, Rel diff: {rel_diff:.6f}, "
                                               f"Tolerance: {self.tolerance}")
                        else:
                            is_match = abs_diff <= self.tolerance
                            if not is_match and i < 5:
                                self.logger.info(f"Row {i} mismatch - Excel: {excel_num}, SQL: {sql_num}, "
                                               f"Abs diff: {abs_diff}, Tolerance: {self.tolerance}")
                        if is_match:
                            col_results["match_count"] += 1
                        else:
                            col_results["mismatch_count"] += 1
                            col_results["mismatch_rows"].append({
                                "row": i,
                                "excel_value": excel_val,
                                "sql_value": sql_val,
                                "difference": excel_num - sql_num
                            })
                    except (ValueError, TypeError) as e:
                        self.logger.warning(f"Error comparing values at row {i}: {str(e)}")
                        if str(excel_val).strip() == str(sql_val).strip():
                            col_results["match_count"] += 1
                        else:
                            col_results["mismatch_count"] += 1
                            col_results["mismatch_rows"].append({
                                "row": i,
                                "excel_value": excel_val,
                                "sql_value": sql_val,
                                "difference": "String mismatch"
                            })
                else:
                    excel_str = str(excel_val).strip().lower()
                    sql_str = str(sql_val).strip().lower()
                    if excel_str == sql_str:
                        col_results["match_count"] += 1
                    else:
                        col_results["mismatch_count"] += 1
                        col_results["mismatch_rows"].append({
                            "row": i,
                            "excel_value": excel_val,
                            "sql_value": sql_val,
                            "difference": "String mismatch"
                        })
            
            # Calculate match percentage for this column
            total_cells = col_results["match_count"] + col_results["mismatch_count"]
            col_results["match_percentage"] = (col_results["match_count"] / total_cells * 100) if total_cells > 0 else 0
            
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
        
        # Store results
        self.comparison_results = results
        
        return results
    
    def _identify_key_columns(self, excel_df, sql_df, column_mappings):
        """Identify key columns for joining Excel and SQL data"""
        # First try to find Center and CAReportName columns
        key_columns = {
            'excel': [],
            'sql': []
        }
        
        # Look for Center column
        for mapping in column_mappings.values():
            if mapping['excel_column'].lower() == 'center':
                key_columns['excel'].append(mapping['excel_column'])
                key_columns['sql'].append(mapping['sql_column'])
                break
        
        # Look for CAReportName column
        for mapping in column_mappings.values():
            if mapping['excel_column'].lower() == 'careportname':
                key_columns['excel'].append(mapping['excel_column'])
                key_columns['sql'].append(mapping['sql_column'])
                break
        
        # If we found both key columns, return them
        if len(key_columns['excel']) == 2:
            return key_columns
        
        # If we didn't find both key columns, try to find any columns that match exactly
        exact_matches = []
        for mapping in column_mappings.values():
            if mapping['match_score'] == 1.0:  # Exact match
                exact_matches.append({
                    'excel': mapping['excel_column'],
                    'sql': mapping['sql_column']
                })
        
        if exact_matches:
            return {
                'excel': [m['excel'] for m in exact_matches],
                'sql': [m['sql'] for m in exact_matches]
            }
        
        return None
    
    def generate_comparison_report(self, sheet_name, comparison_results=None):
        """Generate a detailed, executive-friendly report of comparison results"""
        if comparison_results is None:
            comparison_results = self.comparison_results
            
        if not comparison_results:
            self.logger.warning("No comparison results available")
            return "No comparison results available."
        
        # Get key column information to extract account numbers and other identifying info
        key_columns = []
        for i, mapping in comparison_results.get("column_mappings", {}).items():
            # Look for key columns like Center, Account, CAReportName
            if mapping['excel_column'].lower() in ['center', 'account', 'careportname', 'sheet_name']:
                key_columns.append(mapping['excel_column'])
        
        report = f"# Comparison Report: {sheet_name}\n\n"
        
        # --- Duplicate key reporting ---
        dup_report = comparison_results.get("duplicate_keys", {})
        if dup_report and (dup_report.get("excel") or dup_report.get("sql")):
            report += "## Duplicate Join Keys Detected\n\n"
            if dup_report.get("excel"):
                report += "**Excel duplicate keys:**\n\n"
                report += "| Join Key | Count |\n|---------|-------|\n"
                for key, count in dup_report["excel"].items():
                    report += f"| {key} | {count} |\n"
            if dup_report.get("sql"):
                report += "\n**SQL duplicate keys:**\n\n"
                report += "| Join Key | Count |\n|---------|-------|\n"
                for key, count in dup_report["sql"].items():
                    report += f"| {key} | {count} |\n"
            report += "\n**Warning:** Duplicate join keys can cause inflated matched record counts and inaccurate comparisons. Please review your data.\n\n"
        
        # High-level executive summary
        report += "## Executive Summary\n\n"
        
        # Determine overall status
        mismatch_pct = comparison_results["summary"]["mismatch_percentage"]
        if mismatch_pct == 0:
            status = "✅ PERFECT MATCH"
        elif mismatch_pct < 1:
            status = "✅ GOOD MATCH"
        elif mismatch_pct < 5:
            status = "⚠️ MODERATE MISMATCH"
        else:
            status = "❌ SIGNIFICANT MISMATCH"
            
        report += f"**Status:** {status}\n\n"
        report += f"**Match Rate:** {100 - mismatch_pct:.2f}% ({comparison_results['summary']['matching_cells']} of {comparison_results['summary']['total_cells']} cells match)\n\n"
        
        # Row statistics 
        report += "## Data Coverage\n\n"
        report += f"**Excel Records:** {comparison_results['row_counts']['excel']}\n"
        report += f"**SQL Records:** {comparison_results['row_counts']['sql']}\n"
        report += f"**Matched Records:** {comparison_results['row_counts']['matched']}\n"
        
        # Unmatched record explanation if applicable
        excel_only = comparison_results['row_counts']['excel'] - comparison_results['row_counts']['matched']
        sql_only = comparison_results['row_counts']['sql'] - comparison_results['row_counts']['matched']
        
        if excel_only > 0 or sql_only > 0:
            report += "\n### Unmatched Records\n\n"
            if excel_only > 0:
                report += f"* **Excel-only Records:** {excel_only} (in Excel but not found in SQL)\n"
            if sql_only > 0:
                report += f"* **SQL-only Records:** {sql_only} (in SQL but not found in Excel)\n"
        
        # Mismatch analysis
        report += "\n## Mismatch Analysis\n\n"
        
        # Show column-level statistics
        column_stats = []
        for excel_col, results in comparison_results["column_comparisons"].items():
            # Skip columns with perfect matches
            if results["mismatch_count"] == 0:
                continue
                
            sql_col = next((m["sql_column"] for i, m in comparison_results["column_mappings"].items() 
                          if m["excel_column"] == excel_col), "Unknown")
                          
            mismatch_pct = (results["mismatch_count"] / (results["match_count"] + results["mismatch_count"])) * 100
            
            column_stats.append({
                "excel_column": excel_col,
                "sql_column": sql_col,
                "mismatch_count": results["mismatch_count"],
                "mismatch_percentage": mismatch_pct,
                "is_numeric": results["is_numeric"]
            })
        
        # Sort columns by mismatch percentage (highest first)
        column_stats.sort(key=lambda x: x["mismatch_percentage"], reverse=True)
        
        if column_stats:
            report += "### Columns with Mismatches\n\n"
            report += "| Column | SQL Column | Mismatch Count | Mismatch % | Type |\n"
            report += "|--------|------------|---------------|------------|------|\n"
            
            for stat in column_stats:
                report += f"| {stat['excel_column']} | {stat['sql_column']} | {stat['mismatch_count']} | {stat['mismatch_percentage']:.2f}% | {'Numeric' if stat['is_numeric'] else 'Text'} |\n"
            
            report += "\n"
        
        # Detailed mismatch report - by account/identifying info
        report += "## Detailed Mismatch Report\n\n"
        
        # Gather all mismatches with identity information
        all_mismatches = []
        
        for excel_col, results in comparison_results["column_comparisons"].items():
            # Skip if no mismatches
            if not results["mismatch_rows"]:
                continue
                
            sql_col = next((m["sql_column"] for i, m in comparison_results["column_mappings"].items() 
                          if m["excel_column"] == excel_col), "Unknown")
            
            for mismatch in results["mismatch_rows"]:
                # Add column info to the mismatch
                mismatch_with_col = mismatch.copy()
                mismatch_with_col["excel_column"] = excel_col
                mismatch_with_col["sql_column"] = sql_col
                
                all_mismatches.append(mismatch_with_col)
        
        # Sort mismatches by row number for consistent reporting
        all_mismatches.sort(key=lambda x: x["row"])
        
        if all_mismatches:
            if key_columns:
                # Group mismatches by key columns for more organized reporting
                report += f"### Mismatch Details by {', '.join(key_columns)}\n\n"
                
                # We need access to the full merged dataframe to extract key column values
                # For now, we'll just show the mismatches in a well-formatted table
                report += "| Row | Account Info | Column | Excel Value | SQL Value | Difference |\n"
                report += "|-----|-------------|--------|-------------|-----------|------------|\n"
                
                for i, mismatch in enumerate(all_mismatches[:50]):  # Limit to 50 mismatches
                    row = mismatch["row"]
                    excel_val = str(mismatch["excel_value"]).replace("|", "\\|")
                    sql_val = str(mismatch["sql_value"]).replace("|", "\\|")
                    diff = str(mismatch["difference"]).replace("|", "\\|")
                    excel_col = mismatch["excel_column"]
                    
                    # Account info placeholder - in a full implementation, 
                    # this would extract values from key columns for this row
                    account_info = f"Row {row}"
                    
                    report += f"| {row} | {account_info} | {excel_col} | {excel_val} | {sql_val} | {diff} |\n"
                
                if len(all_mismatches) > 50:
                    report += f"\n*...and {len(all_mismatches) - 50} more mismatches.*\n"
            else:
                # Simple mismatch table
                report += "### All Mismatches\n\n"
                report += "| Row | Column | Excel Value | SQL Value | Difference |\n"
                report += "|-----|--------|-------------|-----------|------------|\n"
                
                for i, mismatch in enumerate(all_mismatches[:50]):  # Limit to 50 mismatches
                    row = mismatch["row"]
                    excel_val = str(mismatch["excel_value"]).replace("|", "\\|")
                    sql_val = str(mismatch["sql_value"]).replace("|", "\\|")
                    diff = str(mismatch["difference"]).replace("|", "\\|")
                    excel_col = mismatch["excel_column"]
                    
                    report += f"| {row} | {excel_col} | {excel_val} | {sql_val} | {diff} |\n"
                
                if len(all_mismatches) > 50:
                    report += f"\n*...and {len(all_mismatches) - 50} more mismatches.*\n"
        else:
            report += "No mismatches found! All values match perfectly.\n"
                
        return report 

    def generate_detailed_comparison_dataframe(self, sheet_name, excel_df, sql_df, column_mappings=None):
        """Generate a DataFrame with all matches, mismatches, and missing records for export, including sign flip and field column."""
        # Run the comparison to get the merged DataFrame and mappings
        if column_mappings is None:
            column_mappings = self.find_matching_columns(excel_df.columns, sql_df.columns)
        key_columns = self._identify_key_columns(excel_df, sql_df, column_mappings)
        if not key_columns:
            raise ValueError("Could not identify key columns for joining")
        
        # Prepare sign flip accounts as a set of stripped strings
        sign_flip_accounts_str = set(str(acct).strip() for acct in getattr(self, 'sign_flip_accounts', set()))
        
        # Create join keys
        excel_keys = excel_df[key_columns['excel']].astype(str).agg('-'.join, axis=1)
        sql_keys = sql_df[key_columns['sql']].astype(str).agg('-'.join, axis=1)
        
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
        account_col_excel = None
        account_col_sql = None
        for col in ['Account', 'CAReportName', 'Account Number', 'Acct', 'AccountNumber']:
            if f'{col}_excel' in merged_df.columns:
                account_col_excel = f'{col}_excel'
            if f'{col}_sql' in merged_df.columns:
                account_col_sql = f'{col}_sql'
        
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
                careport = row.get('CAReportName_excel') or row.get('CAReportName_sql') or ''
                field = excel_col
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
                output_rows.append({
                    'Sheet': sheet_name,
                    'Center': center,
                    'CAReport Name': careport,
                    'Field': field,
                    'Excel Value': excel_val_out,
                    'DataBase Value': sql_val_out,
                    'Variance': variance,
                    'Result': result
                })
        return pd.DataFrame(output_rows) 
