import datetime
import common
import datelib
import income
import re
import expense
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

# to-do можно сделать один метод для доходо и расходов
async def process_input(update, context):
    mode = context.user_data.get("mode")

    match mode:
        case "income":
            await income.process_income_input(update,context)
        case "expense":
            await expense.process_expense_input(update,context)
        case _:
            message = "mode not defined"
            common.logger.error(message)
            await update.message.reply_text(message)

async def get_logs(update: Update, context: CallbackContext):
    try:
        today = datetime.date.today().isoformat()

        with open(common.log_file_path, "r", encoding="utf-8") as log_file:
            logs = "\n".join(
                line for line in log_file
                if line.startswith(today)
            )
            logs = logs.replace("\n", "\n\n")
            await update.message.reply_text(logs[:4000] or "Log file is empty")
    except FileNotFoundError:
        message = "Log file is not found"
        common.logger.error(message)
        await update.message.reply_text(message)
    except Exception as e:
        common.logger.error(e)
        await update.message.reply_text(f"Error: {e}")

def main():
    application = Application.builder().token(common.BOT_TOKEN).build()

    application.add_handler(CommandHandler("income", income.income))
    application.add_handler(CommandHandler("expense", expense.expense))
    application.add_handler(CommandHandler("logs", get_logs))
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
    common.logger.info("Bot started")
    application.run_polling()

if __name__ == '__main__':
    main()