import os
import pandas as pd
from src.analyzer.comparison_engine import ComparisonEngine

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')
PLUGIN_DIR = os.path.join(os.path.dirname(__file__), 'plugins')


def test_plugin_hooks_called():
    excel_df = pd.read_csv(os.path.join(FIXTURES, 'excel_data.csv'))
    sql_df = pd.read_csv(os.path.join(FIXTURES, 'sql_data.csv'))
    engine = ComparisonEngine(plugin_dirs=[PLUGIN_DIR])
    result = engine.compare_dataframes(excel_df, sql_df)
    plugin = engine.plugins[0]
    assert plugin.pre_called
    assert plugin.post_called
    assert result.get('plugin_executed') is True

