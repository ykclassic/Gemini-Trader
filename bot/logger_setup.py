import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name="crypto_bot"):
    """Configures multi-destination logging (Console + File)."""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs if handler exists
    if not logger.handlers:
        # File Handler: Rotates after 5MB, keeps 5 old logs
        file_handler = RotatingFileHandler(
            'logs/app.log', maxBytes=5*1024*1024, backupCount=5
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
