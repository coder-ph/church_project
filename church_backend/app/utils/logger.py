import logging
import os

def setup_logger(name="flask_app"):
    logger = logging.getLogger(name)
    
    logger.setLevel(logging.DEBUG if os.getenv("FLASK_ENV")== ("development") else logging.INFO)

    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger