import os
import logging
from logging.handlers import RotatingFileHandler
from backend.app.core.config import settings

def setup_logging():
    """Configure structured logging for the CineMatch AI application."""
    log_dir = os.path.join(settings.BASE_DIR, "backend", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_filepath = os.path.join(log_dir, "app.log")
    
    # Root logger configuration
    logger = logging.getLogger("cinematch")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate logging if already configured
    if logger.handlers:
        return logger
        
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # File Handler (rotating file to keep size small)
    file_handler = RotatingFileHandler(
        log_filepath,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    
    logger.info("Logging configured successfully.")
    return logger
