import common
import datelib
import income
import expense
import matches
import time
from yadisk import Client
import requests
import sys
from openpyxl import load_workbook
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import datetime, date, timedelta

# можно сделать один метод для доходо и расходов
async def process_input(update, context):
    mode = context.user_data.get("mode")

    if mode == "income":
        await income.process_income_input(update, context)
    elif mode == "expense":
        await expense.process_expense_input(update, context)

async def logs(update: Update, context: CallbackContext):
    try:
        with open(common.log_file_path, "r") as log_file:
            logs = log_file.read().replace("\n", "\n\n")
            if len(logs) > 4000:
                logs = logs[-4000:]
            await update.message.reply_text(logs or "Файл пуст")
    except FileNotFoundError:
        await update.message.reply_text("Файл логов не найден")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

def main():
    application = Application.builder().token(common.BOT_TOKEN).build()

    application.add_handler(CommandHandler("income", income.income))
    application.add_handler(CommandHandler("expense", expense.expense))
    application.add_handler(CommandHandler("logs", logs))
    application.add_handler(CallbackQueryHandler(income.get_income_categories, pattern="get_income_categories"))
    application.add_handler(CallbackQueryHandler(income.get_income_view, pattern="get_income_view"))
    application.add_handler(CallbackQueryHandler(expense.get_expense_view, pattern="get_expense_view"))
    application.add_handler(CallbackQueryHandler(expense.get_expense_categories, pattern="get_expense_categories"))
    application.add_handler(CallbackQueryHandler(income.income, pattern="back_to_income"))
    application.add_handler(CallbackQueryHandler(expense.expense, pattern="back_to_expense"))
    application.add_handler(CallbackQueryHandler(income.select_income_category_handler, pattern="^select_income_category_"))
    application.add_handler(CallbackQueryHandler(expense.select_expense_category_handler, pattern="^select_expense_category_"))
    application.add_handler(CallbackQueryHandler(income.ask_for_income, pattern="^ask_for_income_"))
    application.add_handler(CallbackQueryHandler(expense.ask_for_expense, pattern="^ask_for_expense_"))
    application.add_handler(CallbackQueryHandler(datelib.set_date_handler, pattern="^set_date"))
    application.add_handler(CallbackQueryHandler(income.process_calendar_callback, pattern="^cbcal_"))
    application.add_handler(CallbackQueryHandler(expense.process_calendar_callback, pattern="^cbcal_"))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, process_input)
    )
    common.logger.info("Бот запущен")
    application.run_polling()

if __name__ == '__main__':
    main()