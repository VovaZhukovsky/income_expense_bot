from datetime import datetime, date, timedelta
import yadisk
import hashlib
import base64
from cryptography.fernet import Fernet
import logging
import json
import os

config_file_path = 'config.json'

with open(config_file_path, 'r') as f:
    config = json.load(f)
    BOT_TOKEN = config["bot_token"]
    ENCRYPT_TOKEN = f"{config["encrypt_token"]}".encode()
    local_xlsx_path = config["local_xlsx_path"]
    log_file_path = config["log_file_path"]
    year = config["year"]
    ya_xlsx_path = config["ya_xlsx_path"]

DEFAULT_INCOME_INFO = {"id": 20, "name": "job","month": f"{datetime.now().strftime('%B')}"}
DEFAULT_EXPENSE_INFO = {"id": 4, "name": "delivery cafe","month": f"{datetime.now().strftime('%B')}"}

def get_ya_client(user_id):
    key_bytes = hashlib.sha256(f"{user_id}".encode()).digest() 
    key = base64.urlsafe_b64encode(key_bytes)
    cipher = Fernet(key)
    return yadisk.Client(token=cipher.decrypt(ENCRYPT_TOKEN).decode())

logger = logging.getLogger("income_expense_bot")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] — %(message)s"
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


