import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

from .logging_config import configure_logging, get_logger


DEFAULT_SHEET_NAME = "__default__"


class AppConfig:
    def __init__(self):
        """Initialize application configuration"""
        # Basic logging setup so that load steps emit messages
        configure_logging()
        self.logger = get_logger(__name__)

        self.config_file = os.path.join(
            os.path.expanduser("~"), ".soo_preclose_tester.json"
        )
        self.config = self._load_config()

        # Reconfigure logging based on loaded config
        log_cfg = self.config.get("logging", {})
        level = getattr(
            logging, str(log_cfg.get("level", "INFO")).upper(), logging.INFO
        )
        log_file = log_cfg.get("file")
        configure_logging(level=level, log_file=log_file, force=True)

        self._load_env_vars()

    def _load_env_vars(self):
        """Load environment variables from .env file if it exists"""
        env_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
        )
        if os.path.exists(env_path):
            load_dotenv(env_path)
            self.logger.info(f"Loaded environment variables from {env_path}")

            # Override config with environment variables if they exist
            if os.getenv("DB_SERVER"):
                self.config["database"]["server"] = os.getenv("DB_SERVER")
            if os.getenv("DB_NAME"):
                self.config["database"]["database"] = os.getenv("DB_NAME")

    def _load_config(self):
        """Load configuration from file or create default"""
        default_config = {
            "database": {
                "server": "adwtest",
                "database": "cognostesting",
                "trusted_connection": True,
            },
            "ui": {
                "theme": "brand",
                "font_size": 10,
                "show_line_numbers": True,
                "auto_save_queries": True,
            },
            "excel": {
                "default_header_rows": 5,
                "numerical_comparison_tolerance": 0.001,
                "skip_empty_rows": True,
                "skip_empty_columns": True,
            },
            "paths": {"last_excel_file": "", "last_sql_file": "", "recent_files": []},
            "logging": {"level": "INFO", "file": "app.log"},
            "testing": {
                "auto_generate_queries": True,
                "comparison_threshold": 1.0,  # 1% difference allowed
            },
            "account_categories": {},
            "account_formulas": {},
            "formula_library": {},
            "report_formulas": {},
            "report_configs": self.initialize_report_configs(),
        }

        # Create config file if it doesn't exist
        if not os.path.exists(self.config_file):
            with open(self.config_file, "w") as f:
                json.dump(default_config, f, indent=4)
            self.logger.info(
                f"Created default configuration file at {self.config_file}"
            )
            return default_config

        # Load existing config
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
            self.logger.info(f"Loaded configuration from {self.config_file}")

            # Update config with any missing default values
            updated = False
            for section in default_config:
                if section not in config:
                    config[section] = default_config[section]
                    updated = True
                elif isinstance(default_config[section], dict):
                    for key in default_config[section]:
                        if key not in config[section]:
                            config[section][key] = default_config[section][key]
                            updated = True

            # Merge report_configs separately to preserve user additions
            merged_reports = default_config["report_configs"].copy()
            merged_reports.update(config.get("report_configs", {}))
            if config.get("report_configs") != merged_reports:
                updated = True
            config["report_configs"] = merged_reports

            # Migrate account categories/formulas to new sheet-aware structure
            if self._migrate_account_data(config):
                updated = True

            if updated:
                self.save_config(config)

            return config

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            self.logger.info("Using default configuration")
            return default_config

    def _migrate_account_data(self, cfg: dict) -> bool:
        """Migrate account data to newer structures."""
        updated = False

        for key in ["account_categories", "account_formulas"]:
            section = cfg.get(key, {})
            for rpt, mapping in list(section.items()):
                if mapping and all(not isinstance(v, dict) for v in mapping.values()):
                    # Old style: mapping[category] -> values
                    section[rpt] = {DEFAULT_SHEET_NAME: mapping}
                    updated = True
            cfg[key] = section

        rpt_forms = cfg.setdefault("report_formulas", {})
        acc_forms = cfg.get("account_formulas", {})
        for rpt, by_sheet in acc_forms.items():
            dest = rpt_forms.setdefault(rpt, {})
            for sheet, mapping in by_sheet.items():
                for name, expr in mapping.items():
                    entry = dest.setdefault(
                        name,
                        {
                            "expr": expr,
                            "display_name": name,
                            "sheets": [sheet],
                        },
                    )
                    if entry.get("expr") == expr:
                        sheets = entry.setdefault("sheets", [])
                        if sheet not in sheets:
                            sheets.append(sheet)
                            updated = True
                    else:
                        idx = 1
                        new_name = name
                        while new_name in dest and dest[new_name].get("expr") != expr:
                            idx += 1
                            new_name = f"{name}_{idx}"
                        if new_name not in dest:
                            dest[new_name] = {
                                "expr": expr,
                                "display_name": name,
                                "sheets": [sheet],
                            }
                            updated = True

        if acc_forms:
            cfg["account_formulas"] = {}
            updated = True

        lib = cfg.get("formula_library", {})
        if lib:
            for rpt in cfg.get("report_configs", {}).keys():
                dest = rpt_forms.setdefault(rpt, {})
                for name, info in lib.items():
                    entry = dest.setdefault(
                        name,
                        {
                            "expr": info.get("expr", ""),
                            "display_name": info.get("display_name", name),
                            "sheets": list(info.get("sheets") or []),
                        },
                    )
                    if entry.get("expr") == info.get("expr", ""):
                        for sheet in info.get("sheets") or []:
                            if sheet not in entry.setdefault("sheets", []):
                                entry["sheets"].append(sheet)
                                updated = True
                    else:
                        idx = 1
                        new_name = name
                        while new_name in dest and dest[new_name].get("expr") != info.get("expr", ""):
                            idx += 1
                            new_name = f"{name}_{idx}"
                        if new_name not in dest:
                            dest[new_name] = {
                                "expr": info.get("expr", ""),
                                "display_name": info.get("display_name", name),
                                "sheets": list(info.get("sheets") or []),
                            }
                            updated = True
            cfg["formula_library"] = {}
            updated = True

        return updated

    def _serialize(self, obj):
        """Return JSON serializable representation of ``obj``."""
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, set):
            return sorted(obj)
        if isinstance(obj, dict):
            return {k: self._serialize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._serialize(v) for v in obj]
        return obj

    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config

        try:
            with open(self.config_file, "w") as f:
                json.dump(self._serialize(config), f, indent=4)
            self.logger.info(f"Saved configuration to {self.config_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            return False

    def get(self, section, key=None):
        """Get configuration value"""
        if section not in self.config:
            self.logger.warning(f"Configuration section '{section}' not found")
            return None

        if key is None:
            return self.config[section]

        if key not in self.config[section]:
            self.logger.warning(
                f"Configuration key '{key}' not found in section '{section}'"
            )
            return None

        return self.config[section][key]

    def set(self, section, key, value):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}

        self.config[section][key] = value
        self.save_config()
        self.logger.info(f"Set configuration {section}.{key} = {value}")

    def add_recent_file(self, file_path, max_recent=10):
        """Add a file to the recent files list"""
        if not file_path or not os.path.exists(file_path):
            return False

        # Get absolute path
        file_path = os.path.abspath(file_path)

        # Get recent files list
        recent_files = self.config["paths"].get("recent_files", [])

        # Remove if already in list
        if file_path in recent_files:
            recent_files.remove(file_path)

        # Add to beginning of list
        recent_files.insert(0, file_path)

        # Trim list if needed
        if len(recent_files) > max_recent:
            recent_files = recent_files[:max_recent]

        # Update config
        self.config["paths"]["recent_files"] = recent_files
        self.save_config()

        self.logger.info(f"Added {file_path} to recent files")
        return True

    def get_db_connection_params(self):
        """Get database connection parameters"""
        return {
            "server": self.config["database"].get("server", "adwtest"),
            "database": self.config["database"].get("database", "cognostesting"),
            "trusted_connection": self.config["database"].get(
                "trusted_connection", True
            ),
        }

    def update_last_excel_file(self, file_path):
        """Update the last Excel file path"""
        if not file_path:
            return False

        self.config["paths"]["last_excel_file"] = file_path
        self.add_recent_file(file_path)
        self.save_config()
        return True

    def update_last_sql_file(self, file_path):
        """Update the last SQL file path"""
        if not file_path:
            return False

        self.config["paths"]["last_sql_file"] = file_path
        self.add_recent_file(file_path)
        self.save_config()
        return True

    def get_account_categories(self, report_type, sheet_name=None):
        """Return account categories for ``report_type`` and optional ``sheet_name``."""
        cats_by_type = self.config.get("account_categories", {}).get(report_type, {})

        if sheet_name is None:
            if DEFAULT_SHEET_NAME in cats_by_type and len(cats_by_type) == 1:
                return cats_by_type.get(DEFAULT_SHEET_NAME, {})
            combined = {}
            for _sheet, cats in cats_by_type.items():
                if isinstance(cats, dict):
                    for name, accounts in cats.items():
                        combined.setdefault(name, [])
                        for acc in accounts:
                            if acc not in combined[name]:
                                combined[name].append(acc)
            return combined

        return cats_by_type.get(sheet_name) or cats_by_type.get(DEFAULT_SHEET_NAME, {})

    def set_account_categories(self, report_type, categories, sheet_name=None):
        """Set account categories for a report type and persist the config"""
        if "account_categories" not in self.config:
            self.config["account_categories"] = {}
        if sheet_name is None:
            sheet_name = DEFAULT_SHEET_NAME

        self.config["account_categories"].setdefault(report_type, {})[
            sheet_name
        ] = categories
        self.save_config()

    def get_account_formulas(self, report_type, sheet_name=None):
        """Return account formulas for ``report_type`` and optional ``sheet_name``.

        Formulas defined directly under ``account_formulas`` take precedence.
        Formulas from the global ``formula_library`` that apply to the requested
        sheet are merged in.
        """
        formulas_by_type = self.config.get("account_formulas", {}).get(report_type, {})

        if sheet_name is None:
            if DEFAULT_SHEET_NAME in formulas_by_type and len(formulas_by_type) == 1:
                result = dict(formulas_by_type.get(DEFAULT_SHEET_NAME, {}))
            else:
                result = {}
                for _sheet, forms in formulas_by_type.items():
                    if isinstance(forms, dict):
                        result.update(forms)
        else:
            result = formulas_by_type.get(sheet_name) or formulas_by_type.get(
                DEFAULT_SHEET_NAME, {}
            )
            result = dict(result)

        lib = self.get_formula_library()
        for name, info in lib.items():
            sheets = info.get("sheets") or []
            if (
                sheet_name is None
                or sheet_name in sheets
                or DEFAULT_SHEET_NAME in sheets
            ):
                result.setdefault(name, info.get("expr", ""))

        return result

    def set_account_formulas(self, report_type, formulas, sheet_name=None):
        """Set account formulas for a report type and persist the config"""
        if "account_formulas" not in self.config:
            self.config["account_formulas"] = {}

        if sheet_name is None:
            sheet_name = DEFAULT_SHEET_NAME

        self.config["account_formulas"].setdefault(report_type, {})[
            sheet_name
        ] = formulas
        self.save_config()

    # Report formulas helpers -------------------------------------------------

    def get_report_formulas(self, report_type: str, sheet_name: str | None = None) -> dict:
        """Return formulas for ``report_type`` filtered by ``sheet_name``."""
        mapping = self.config.get("report_formulas", {}).get(report_type, {})

        def _copy(src: dict) -> dict:
            return {k: dict(v) for k, v in src.items()}

        if sheet_name is None:
            result = _copy(mapping)
        else:
            result = {}
            for name, info in mapping.items():
                sheets = info.get("sheets") or []
                if (not sheets or sheet_name in sheets or DEFAULT_SHEET_NAME in sheets):
                    result[name] = dict(info)
        return result

    def set_report_formulas(self, report_type: str, formulas: dict) -> None:
        """Set formulas for ``report_type`` and persist the config."""
        if "report_formulas" not in self.config:
            self.config["report_formulas"] = {}
        cleaned = {}
        for name, info in (formulas or {}).items():
            entry = dict(info)
            if not entry.get("sheets"):
                entry.pop("sheets", None)
            cleaned[name] = entry
        self.config["report_formulas"][report_type] = cleaned
        self.save_config()

    # Formula library helpers -------------------------------------------------

    def get_formula_library(self):
        """Return the global formula library."""
        return self.config.get("formula_library", {})

    def set_formula_library(self, library: dict):
        """Replace the global formula library and persist it."""
        self.config["formula_library"] = library
        self.save_config()

    # Report configuration helpers -------------------------------------------------

    def initialize_report_configs(self):
        """Return default report configurations."""
        return {
            "SOO PreClose": {
                "header_rows": [5, 6],
                "skip_rows": 7,
                "first_data_column": 2,
                "description": "SOO PreClose report with headers on rows 6 and 7",
                "center_cell": None,
            },
            "SOO MFR": {
                "header_rows": [9],
                "skip_rows": 10,
                "first_data_column": 4,
                "description": "SOO MFR report with header on row 10",
                "center_cell": None,
            },
            "MFR PreClose": {
                "header_rows": [9],
                "skip_rows": 10,
                "first_data_column": 4,
                "description": "MFR PreClose report with header on row 10",
                "center_cell": None,
            },
            "Executive Book": {
                "header_rows": [2, 3],
                "skip_rows": 4,
                "first_data_column": 2,
                "description": "Executive Book report with headers on rows 3 and 4",
                "center_cell": None,
            },
            "Statement of Operations": {
                "header_rows": [4, 5],
                "skip_rows": 6,
                "first_data_column": 2,
                "description": "Statement of Operations report with headers on rows 5 and 6",
                "center_cell": None,
            },
            "Corp SOO": {
                "header_rows": [5],
                "skip_rows": 7,
                "first_data_column": 2,
                "description": "Corporate SOO report with header on row 6",
                "center_cell": None,
            },
            "AR Center": {
                "header_rows": [4, 5],
                "skip_rows": 6,
                "first_data_column": 2,
                "description": "AR Center report with headers on rows 5 and 6",
                "center_cell": None,
            },
        }

    def get_report_config(self, name):
        """Retrieve report configuration by name."""
        cfg = self.config.get("report_configs", {}).get(name)
        if cfg and "first_data_column" not in cfg:
            cfg["first_data_column"] = 2
        return cfg

    def set_report_config(self, name, cfg):
        """Set a report configuration and persist it."""
        if "report_configs" not in self.config:
            self.config["report_configs"] = {}
        self.config["report_configs"][name] = cfg
        self.save_config()
