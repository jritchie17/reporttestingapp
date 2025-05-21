from src.plugins import Plugin

class DummyPlugin(Plugin):
    def __init__(self):
        self.pre_called = False
        self.post_called = False

    def pre_compare(self, excel_df, sql_df):
        self.pre_called = True
        return excel_df, sql_df

    def post_compare(self, results):
        self.post_called = True
        results['plugin_executed'] = True
        return results
