
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from .config import settings

def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Set up root logger
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(
                "logs/app.log", 
                maxBytes=10485760,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set third-party loggers to less verbose levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    # Create separate access log
    access_logger = logging.getLogger("access")
    access_handler = RotatingFileHandler(
        "logs/access.log",
        maxBytes=10485760,
        backupCount=10
    )
    access_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    access_handler.setFormatter(access_formatter)
    access_logger.addHandler(access_handler)
    access_logger.propagate = False
    
    # Create separate error log
    error_logger = logging.getLogger("error")
    error_handler = RotatingFileHandler(
        "logs/error.log",
        maxBytes=10485760,
        backupCount=10
    )
    error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)
    error_logger.propagate = False
