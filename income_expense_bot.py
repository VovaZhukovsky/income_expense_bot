import datetime
import common
import datelib
import action
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

async def process_input(update, context):

    if context.user_data.get('operator') is None:
        common.logger.error("Operator is None")
        await update.message.reply_text("Error: Operator is None")
        return

    await action.process_input(update,context)

def create_action_handler(mode : common.Mode = common.Mode.NONE):
    async def handler(update, context):
        await action.action(update, context, mode)
    return handler

async def get_logs(update: Update, context: CallbackContext):
    try:
        today = datetime.date.today().isoformat()

        open(common.log_file_path, "a").close()
        with open(common.log_file_path, "r", encoding="utf-8") as log_file:
            logs = "".join(
                line for line in log_file
                if line.startswith(today)
            )
            logs = logs.replace("\n", "\n\n")
            await update.message.reply_text(logs[:4000] or "Log file is empty")
    except Exception as e:
        common.logger.error(e)
        await update.message.reply_text("Error occurred while trying to get logs")

def main():
    from telegram.request import HTTPXRequest
    request = HTTPXRequest(read_timeout=30, write_timeout=30, connect_timeout=15, pool_timeout=30)
    application = Application.builder().token(common.BOT_TOKEN).request(request).build()

    auth = common.authorized
    application.add_handler(CommandHandler("income", auth(create_action_handler(common.Mode.INCOME))))
    application.add_handler(CommandHandler("expense", auth(create_action_handler(common.Mode.EXPENSE))))
    application.add_handler(CommandHandler("logs", auth(get_logs)))
    application.add_handler(CallbackQueryHandler(auth(action.get_categories), pattern="get_categories"))
    application.add_handler(CallbackQueryHandler(auth(action.get_view), pattern="get_view"))
    application.add_handler(CallbackQueryHandler(auth(create_action_handler()), pattern="back"))
    application.add_handler(CallbackQueryHandler(auth(action.select_category_handler), pattern="^select_category_"))
    application.add_handler(CallbackQueryHandler(auth(action.ask_for), pattern="^ask_for_"))
    application.add_handler(CallbackQueryHandler(auth(datelib.set_date_handler), pattern="^set_date"))
    application.add_handler(CallbackQueryHandler(auth(action.process_calendar_callback), pattern="^cbcal_"))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, auth(process_input))
    )
    common.logger.info("Bot started")
    application.run_polling()

if __name__ == '__main__':
    main()