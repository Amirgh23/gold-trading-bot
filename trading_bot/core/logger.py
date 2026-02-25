"""Structured logging system with JSON format support."""

import logging
import json
import os
from datetime import datetime
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format."""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logger(name, log_dir='logs', level=logging.INFO):
    """
    Set up structured logging with both file and console handlers.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        level: Logging level
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Use absolute path in user's home directory or current directory
    if log_dir == 'logs':
        # Try current directory first, then user home
        log_dir = Path.cwd() / 'logs'
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                # Fallback to user home directory
                log_dir = Path.home() / '.trading_bot' / 'logs'
                log_dir.mkdir(parents=True, exist_ok=True)
    else:
        log_dir = Path(log_dir)
    
    # Create logs directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # JSON file handler
    log_file = log_dir / f'{name.replace(".", "_")}.json'
    json_handler = logging.FileHandler(str(log_file))
    json_handler.setFormatter(JSONFormatter())
    logger.addHandler(json_handler)
    
    # Console handler with simple format
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger
