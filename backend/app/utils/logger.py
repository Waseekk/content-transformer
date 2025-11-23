"""
Centralized Logging System
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

from app.config import get_settings

settings = get_settings()


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
        logger.setLevel(getattr(logging, settings.LOG_LEVEL))

        # Remove existing handlers
        logger.handlers = []

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler
        if log_file is None:
            log_file = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"

        log_path = settings.LOG_DIR / log_file

        # Ensure log directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger


def get_scraper_logger():
    """Get logger for scraper module"""
    return LoggerManager.get_logger('scraper')


def get_webapp_logger():
    """Get logger for web application"""
    return LoggerManager.get_logger('webapp')


def get_scheduler_logger():
    """Get logger for scheduler"""
    return LoggerManager.get_logger('scheduler')


def get_enhancer_logger():
    """Get logger for enhancer module"""
    return LoggerManager.get_logger('enhancer')


def get_translator_logger():
    """Get logger for translator module"""
    return LoggerManager.get_logger('translator')
