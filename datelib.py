from telegram import Update
from telegram.ext import CallbackContext
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

async def set_date_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    calendar = DetailedTelegramCalendar()
    calendar_markup, step = calendar.build()
    context.user_data['calendar'] = calendar
    await query.edit_message_text(
        f"📅 Choose date ({LSTEP[step]}):",
        reply_markup=calendar_markup
    )