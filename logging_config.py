"""
Logging configuration for ESG Reporting Application

This module provides centralized logging configuration that can be easily
adjusted for different deployment environments.
"""

import os
import logging
import sys
from datetime import datetime


class LoggingConfig:
    """Centralized logging configuration"""
    
    # Log levels mapping
    LOG_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    @classmethod
    def setup_logging(cls, 
                      log_level: str = None,
                      log_to_file: bool = True,
                      log_file_prefix: str = "app",
                      console_output: bool = True):
        """
        Setup comprehensive logging for the application
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to file
            log_file_prefix: Prefix for log file names
            console_output: Whether to output to console
        """
        
        # Determine log level from environment or parameter
        if log_level is None:
            log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        # Validate log level
        if log_level not in cls.LOG_LEVELS:
            log_level = 'INFO'
            print(f"Invalid log level specified, using INFO")
        
        # Create logs directory if logging to file
        if log_to_file:
            os.makedirs('logs', exist_ok=True)
        
        # Configure formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Setup handlers
        handlers = []
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            # Use simple format for console in production
            env = os.getenv('ENVIRONMENT', 'development').lower()
            if env == 'production':
                console_handler.setFormatter(simple_formatter)
            else:
                console_handler.setFormatter(detailed_formatter)
            handlers.append(console_handler)
        
        # File handler
        if log_to_file:
            log_filename = f'logs/{log_file_prefix}_{datetime.now().strftime("%Y%m%d")}.log'
            file_handler = logging.FileHandler(log_filename)
            file_handler.setFormatter(detailed_formatter)
            handlers.append(file_handler)
        
        # Configure root logger
        logging.basicConfig(
            level=cls.LOG_LEVELS[log_level],
            handlers=handlers,
            force=True  # Override any existing configuration
        )
        
        # Set specific logger levels for third-party packages
        cls._configure_third_party_loggers(log_level)
        
        # Create and return application logger
        logger = logging.getLogger("envizi_esg_app")
        logger.info(f"Logging configured at {log_level} level")
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        return logger
    
    @classmethod
    def _configure_third_party_loggers(cls, app_log_level: str):
        """Configure logging levels for third-party packages"""
        
        # Set appropriate levels for third-party loggers
        third_party_configs = {
            'uvicorn': 'INFO',
            'uvicorn.access': 'INFO' if app_log_level in ['DEBUG', 'INFO'] else 'WARNING',
            'fastapi': 'INFO' if app_log_level == 'DEBUG' else 'WARNING',
            'playwright': 'WARNING',
            'matplotlib': 'WARNING',
            'plotly': 'WARNING',
            'openai': 'INFO' if app_log_level == 'DEBUG' else 'WARNING',
        }
        
        for logger_name, level in third_party_configs.items():
            third_party_logger = logging.getLogger(logger_name)
            third_party_logger.setLevel(cls.LOG_LEVELS.get(level, logging.WARNING))


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Logger name (defaults to envizi_esg_app if None)
    
    Returns:
        Logger instance
    """
    if name is None:
        name = "envizi_esg_app"
    elif not name.startswith("envizi_esg_app"):
        name = f"envizi_esg_app.{name}"
    
    return logging.getLogger(name)


# Environment-specific configurations
ENVIRONMENT_CONFIGS = {
    'development': {
        'log_level': 'DEBUG',
        'log_to_file': True,
        'console_output': True
    },
    'staging': {
        'log_level': 'INFO',
        'log_to_file': True,
        'console_output': True
    },
    'production': {
        'log_level': 'INFO',
        'log_to_file': True,
        'console_output': True
    }
}


def setup_environment_logging():
    """Setup logging based on current environment"""
    env = os.getenv('ENVIRONMENT', 'development').lower()
    config = ENVIRONMENT_CONFIGS.get(env, ENVIRONMENT_CONFIGS['development'])
    
    return LoggingConfig.setup_logging(**config)
