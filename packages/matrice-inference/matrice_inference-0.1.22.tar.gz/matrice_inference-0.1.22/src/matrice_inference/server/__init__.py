import os
import logging

# Define paths
log_path = os.path.join(os.getcwd(), "deploy_server.log")

# Create handlers explicitly
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(log_path)

# Set levels
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

# Define a formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Get the root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Root level must be the lowest (DEBUG)

# Optional: remove any default handlers if basicConfig was called earlier
if logger.hasHandlers():
    logger.handlers.clear()

logger.addHandler(console_handler)
logger.addHandler(file_handler)