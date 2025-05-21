from __future__ import annotations

"""Plugin system for extending the comparison engine."""

from pathlib import Path
import importlib.util
import inspect
from typing import Iterable, List, Type


class Plugin:
    """Base plugin class.

    Plugins can override :meth:`pre_compare` and :meth:`post_compare` to
    customize comparison behaviour. Both methods should return the (possibly
    modified) objects they receive.
    """

    def pre_compare(self, excel_df, sql_df):
        """Hook executed before dataframe comparison."""
        return excel_df, sql_df

    def post_compare(self, results):
        """Hook executed after comparison is complete."""
        return results


def _load_from_file(file: Path) -> List[Plugin]:
    plugins: List[Plugin] = []
    spec = importlib.util.spec_from_file_location(file.stem, file)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for obj in module.__dict__.values():
            if inspect.isclass(obj) and issubclass(obj, Plugin) and obj is not Plugin:
                plugins.append(obj())
    return plugins


def load_plugins(directories: Iterable[Path | str] | None = None) -> List[Plugin]:
    """Load plugins from the given directories."""
    if directories is None:
        directories = [Path(__file__).parent]
    loaded: List[Plugin] = []
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue
        for file in dir_path.glob("*.py"):
            if file.name == "__init__.py":
                continue
            try:
                loaded.extend(_load_from_file(file))
            except Exception:
                # Ignore faulty plugins but continue loading others
                pass
    return loaded

__all__ = ["Plugin", "load_plugins"]
