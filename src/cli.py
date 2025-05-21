import argparse
import os
import sys
import pandas as pd

from src.utils.config import AppConfig
from src.database.db_connector import DatabaseConnector
from src.analyzer.excel_analyzer import ExcelAnalyzer
from src.analyzer.comparison_engine import ComparisonEngine
from src.reporting import generate_pdf_report


def load_excel_command(args):
    analyzer = ExcelAnalyzer(args.excel)
    if not analyzer.load_excel():
        print("Failed to load Excel file")
        return
    print("Available sheets:")
    for name in analyzer.sheet_names:
        print(f"- {name}")


def run_sql_command(args):
    config = AppConfig()
    db = DatabaseConnector(**config.get_db_connection_params())
    if not db.connect():
        print("Failed to connect to database")
        return
    with open(args.sql, 'r', encoding='utf-8') as f:
        sql = f.read()
    result = db.raw_execute(sql)
    if "error" in result:
        print(f"Error executing query: {result['error']}")
    else:
        df = pd.DataFrame(result.get("data", []))
        if args.output:
            df.to_csv(args.output, index=False)
            print(f"Results written to {args.output}")
        else:
            print(df.head())
    db.close()


def compare_command(args):
    analyzer = ExcelAnalyzer(args.excel)
    if not analyzer.load_excel():
        print("Failed to load Excel file")
        return
    excel_df = pd.read_excel(args.excel, sheet_name=args.sheet)

    config = AppConfig()
    db = DatabaseConnector(**config.get_db_connection_params())
    if not db.connect():
        print("Failed to connect to database")
        return
    with open(args.sql, 'r', encoding='utf-8') as f:
        sql = f.read()
    result = db.raw_execute(sql)
    db.close()
    if "error" in result:
        print(f"Error executing query: {result['error']}")
        return
    sql_df = pd.DataFrame(result.get("data", []))

    engine = ComparisonEngine()
    detailed_df = engine.generate_detailed_comparison_dataframe(args.sheet, excel_df, sql_df)
    detailed_df.to_csv(args.output, index=False)
    print(f"Comparison results saved to {args.output}")

    if args.pdf:
        generate_pdf_report.generate_pdf(args.output, args.pdf)
        print(f"PDF report generated: {args.pdf}")


def main():
    parser = argparse.ArgumentParser(description="SOO PreClose Report Tester CLI")
    subparsers = parser.add_subparsers(dest="command")

    p_excel = subparsers.add_parser("load-excel", help="Load an Excel file and list sheets")
    p_excel.add_argument("excel", help="Path to Excel workbook")
    p_excel.set_defaults(func=load_excel_command)

    p_sql = subparsers.add_parser("run-sql", help="Execute a SQL file")
    p_sql.add_argument("sql", help="Path to SQL file")
    p_sql.add_argument("--output", help="Optional CSV output path")
    p_sql.set_defaults(func=run_sql_command)

    p_compare = subparsers.add_parser("compare", help="Compare Excel sheet with SQL results")
    p_compare.add_argument("excel", help="Path to Excel workbook")
    p_compare.add_argument("sql", help="SQL file to execute")
    p_compare.add_argument("--sheet", default="Sheet1", help="Sheet name in Excel")
    p_compare.add_argument("--output", default="results.csv", help="CSV to store detailed results")
    p_compare.add_argument("--pdf", help="Optional path for generated PDF report")
    p_compare.set_defaults(func=compare_command)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
