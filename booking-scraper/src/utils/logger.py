import logging
import os
from datetime import datetime


def create_logger(name):
    """Creates a logger with the given name and a unique log file."""

    # Create a directory for today's date
    today_date = datetime.now().strftime('%m_%d_%Y')
    daily_logs_path = os.path.join(os.getcwd(), "logs", today_date)
    os.makedirs(daily_logs_path, exist_ok=True)

    # Create a new directory for the current run inside the today's directory
    run_time = datetime.now().strftime('%H_%M_%S')
    run_logs_path = os.path.join(daily_logs_path, run_time)
    os.makedirs(run_logs_path, exist_ok=True)

    # Create a log file for the current spider inside the run's directory
    log_file = f"{name}.log"
    log_file_path = os.path.join(run_logs_path, log_file)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s")

    # Handler for writing to file
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler for writing to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
