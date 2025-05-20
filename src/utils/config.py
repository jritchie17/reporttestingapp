import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

class AppConfig:
    def __init__(self):
        """Initialize application configuration"""
        self.logger = self._setup_logging()
        self.config_file = os.path.join(os.path.expanduser("~"), ".soo_preclose_tester.json")
        self.config = self._load_config()
        self._load_env_vars()
        
    def _setup_logging(self):
        """Set up logging for config operations"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
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
                "theme": "light",
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
            "testing": {
                "auto_generate_queries": True,
                "show_suggestions": True,
                "comparison_threshold": 1.0  # 1% difference allowed
            }
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
