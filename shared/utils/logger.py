"""
Centralized Logging System
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
import sys

# Import settings
from shared.config.settings import LOGS_DIR, LOGGING_CONFIG


class LoggerManager:
    """Manage loggers for different modules"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name, log_file=None):
        """
        Get or create a logger
        
        Args:
            name: Logger name (e.g., 'scraper', 'webapp', 'scheduler')
            log_file: Optional custom log file name
        
        Returns:
            logging.Logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = cls._create_logger(name, log_file)
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def _create_logger(cls, name, log_file=None):
        """Create a new logger with handlers"""
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
        
        # Remove existing handlers
        logger.handlers = []
        
        # File handler with rotation
        if not log_file:
            log_file = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_path = LOGS_DIR / log_file
        
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=LOGGING_CONFIG['max_file_size'],
            backupCount=LOGGING_CONFIG['backup_count'],
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatters
        detailed_formatter = logging.Formatter(
            LOGGING_CONFIG['format'],
            datefmt=LOGGING_CONFIG['date_format']
        )
        
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    @classmethod
    def log_exception(cls, logger, exception, context=""):
        """Log an exception with context"""
        logger.error(
            f"{context} - Exception: {type(exception).__name__}: {str(exception)}",
            exc_info=True
        )
    
    @classmethod
    def log_performance(cls, logger, operation, duration):
        """Log performance metrics"""
        logger.info(f"Performance - {operation}: {duration:.2f} seconds")


# Convenience functions
def get_scraper_logger():
    """Get scraper logger"""
    return LoggerManager.get_logger('scraper')

def get_webapp_logger():
    """Get web app logger"""
    return LoggerManager.get_logger('webapp')

def get_scheduler_logger():
    """Get scheduler logger"""
    return LoggerManager.get_logger('scheduler')

def get_translator_logger():
    """Get translator logger"""
    return LoggerManager.get_logger('translator')


# Example usage
if __name__ == "__main__":
    # Test logging
    logger = get_scraper_logger()
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    
    print(f"\nLog file created at: {LOGS_DIR}")