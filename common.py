import os
import sys
import getpass
from enum import Enum
from functools import wraps
import yadisk
from cryptography.fernet import Fernet
import logging
from logging.handlers import WatchedFileHandler
import json
from telegram import Update
from telegram.ext import CallbackContext

config_file_path = os.getenv("CONFIG_PATH", "config.json")

with open(config_file_path, 'r') as f:
    config = json.load(f)
    BOT_TOKEN = os.environ["INCOME_EXPENSE_BOT_TOKEN"]
    local_xlsx_path = config["local_xlsx_path"]
    log_file_path = config["log_file_path"]
    year = config["year"]
    ya_xlsx_path = config["ya_xlsx_path"]
    ALLOWED_USER_IDS = set(config.get("allowed_user_ids", []))
    DEFAULT_INCOME_INFO = config["default_income"]
    DEFAULT_EXPENSE_INFO = config["default_expense"]

ya_token = Fernet(os.environ["KEY"].encode()).decrypt(os.environ["YA_TOKEN_ENCRYPTED"].encode()).decode()

class Mode(str, Enum):
    NONE = ""
    INCOME = "income"
    EXPENSE = "expense"

class Backend_TimeShift_Result:
    def __init__(self, result, old_value = None, new_value = None, diff_value = None):
        self.result = result
        self.old_value = old_value
        self.new_value = new_value
        self.diff_value = diff_value

def get_ya_client():
    return yadisk.Client(token=ya_token)

logger = logging.getLogger("income_expense_bot")
logger.setLevel(logging.INFO)

file_handler = WatchedFileHandler(log_file_path, encoding="utf-8")
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] — %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def authorized(handler):
    @wraps(handler)
    async def wrapper(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
            logger.warning(f"Unauthorized access attempt by user_id={user_id}")
            if update.callback_query:
                await update.callback_query.answer("Access denied.", show_alert=True)
            elif update.message:
                await update.message.reply_text("Access denied.")
            return
        return await handler(update, context)
    return wrapper