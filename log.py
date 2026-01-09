import logging
import sys

def setup_logging():
    logger = logging.getLogger()  # Get the root logger
    logger.setLevel(logging.INFO)  # Set the log level

    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.INFO)  # Set log level for the file handler

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Set log level for the console handler

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger