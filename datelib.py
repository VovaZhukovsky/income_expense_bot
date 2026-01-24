from datetime import date, timedelta
from telegram import Update
from telegram.ext import CallbackContext
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

async def set_date_handler(update: Update, context: CallbackContext):
    """Обработчик установки даты"""
    query = update.callback_query
    await query.answer()
    await show_date_calendar(update, context, for_hours=False)

async def show_date_calendar(update: Update, context: CallbackContext, for_hours: bool = False):
    """Показывает календарь для выбора даты"""
    query = update.callback_query
    today = date.today()
    first_day = today.replace(day=1)

# Сначала получаем следующий месяц, затем отнимаем 1 день
    if today.month == 12:
    # Если декабрь, следующий месяц - январь следующего года
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)

    last_day = next_month - timedelta(days=1)

    calendar = DetailedTelegramCalendar(
        locale='ru'
    )
    
    calendar_markup, step = calendar.build()
    
    context.user_data['calendar'] = calendar
    
    await query.edit_message_text(
        f"📅 Choose date ({LSTEP[step]}):",
        reply_markup=calendar_markup
    )