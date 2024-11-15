import os
import logging

def setup_logging(log_file, logger_name):
    logger = logging.getLogger(logger_name)  # Use a unique logger name
    logger.setLevel(logging.DEBUG)  # Set the logger level to DEBUG

    # Only add the file handler if there are no handlers already
    if not logger.hasHandlers():
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
