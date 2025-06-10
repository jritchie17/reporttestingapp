import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

from .logging_config import configure_logging, get_logger

class AppConfig:
    def __init__(self):
        """Initialize application configuration"""
        # Basic logging setup so that load steps emit messages
        configure_logging()
        self.logger = get_logger(__name__)

        self.config_file = os.path.join(os.path.expanduser("~"), ".soo_preclose_tester.json")
        self.config = self._load_config()

        # Reconfigure logging based on loaded config
        log_cfg = self.config.get("logging", {})
        level = getattr(logging, str(log_cfg.get("level", "INFO")).upper(), logging.INFO)
        log_file = log_cfg.get("file")
        configure_logging(level=level, log_file=log_file, force=True)

        self._load_env_vars()
        
    
    def _load_env_vars(self):
        """Load environment variables from .env file if it exists"""
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
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
                "trusted_connection": True
            },
            "ui": {
                "theme": "brand",
                "font_size": 10,
                "show_line_numbers": True,
                "auto_save_queries": True
            },
            "excel": {
                "default_header_rows": 5,
                "numerical_comparison_tolerance": 0.001,
                "skip_empty_rows": True,
                "skip_empty_columns": True
            },
            "paths": {
                "last_excel_file": "",
                "last_sql_file": "",
                "recent_files": []
            },
            "logging": {
                "level": "INFO",
                "file": "app.log"
            },
            "testing": {
                "auto_generate_queries": True,
                "comparison_threshold": 1.0  # 1% difference allowed
            },
            "account_categories": {},
            "account_formulas": {},
            "report_configs": self.initialize_report_configs()
        }
        
        # Create config file if it doesn't exist
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            self.logger.info(f"Created default configuration file at {self.config_file}")
            return default_config
        
        # Load existing config
        try:
            with open(self.config_file, 'r') as f:
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
            
            if updated:
                self.save_config(config)
                
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            self.logger.info("Using default configuration")
            return default_config
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
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
            self.logger.warning(f"Configuration key '{key}' not found in section '{section}'")
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
            "trusted_connection": self.config["database"].get("trusted_connection", True)
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

    def get_account_categories(self, report_type):
        """Return account categories mapping for a given report type"""
        return self.config.get("account_categories", {}).get(report_type, {})

    def set_account_categories(self, report_type, categories):
        """Set account categories for a report type and persist the config"""
        if "account_categories" not in self.config:
            self.config["account_categories"] = {}

        self.config["account_categories"][report_type] = categories
        self.save_config()

    def get_account_formulas(self, report_type):
        """Return account formulas mapping for a given report type"""
        return self.config.get("account_formulas", {}).get(report_type, {})

    def set_account_formulas(self, report_type, formulas):
        """Set account formulas for a report type and persist the config"""
        if "account_formulas" not in self.config:
            self.config["account_formulas"] = {}

        self.config["account_formulas"][report_type] = formulas
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
            },
            "SOO MFR": {
                "header_rows": [9],
                "skip_rows": 10,
                "first_data_column": 4,
                "description": "SOO MFR report with header on row 10",
            },
            "MFR PreClose": {
                "header_rows": [9],
                "skip_rows": 10,
                "first_data_column": 4,
                "description": "MFR PreClose report with header on row 10",
            },
            "Executive Book": {
                "header_rows": [2, 3],
                "skip_rows": 4,
                "first_data_column": 2,
                "description": "Executive Book report with headers on rows 3 and 4",
            },
            "Statement of Operations": {
                "header_rows": [4, 5],
                "skip_rows": 6,
                "first_data_column": 2,
                "description": "Statement of Operations report with headers on rows 5 and 6",
            },
            "Corp SOO": {
                "header_rows": [5],
                "skip_rows": 7,
                "first_data_column": 2,
                "description": "Corporate SOO report with header on row 6"
            },
            "AR Center": {
                "header_rows": [4, 5],
                "skip_rows": 6,
                "first_data_column": 2,
                "description": "AR Center report with headers on rows 5 and 6",
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
