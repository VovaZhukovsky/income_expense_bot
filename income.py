import common
import os
import matches
from openpyxl import load_workbook
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import datetime, date, timedelta

async def income(update: Update, context: CallbackContext):
    context.user_data["mode"] = "income"
    keyboard = [
        [InlineKeyboardButton("✏️ Изменить категорию", callback_data=f"get_income_categories")],
        [InlineKeyboardButton("📅 Изменить дату", callback_data=f"set_date")],
        [InlineKeyboardButton("➕ Добавить доход", callback_data=f"ask_for_income_increment")],
        [InlineKeyboardButton("➖ Уменьшить доход", callback_data=f"ask_for_income_decrement")],
        [InlineKeyboardButton("🔍 Посмотреть доход", callback_data=f"get_income_view")]
    ]

    if not os.path.isfile(common.local_xlsx_path):
        client = common.get_ya_client(context._user_id)
        with client:
            client.download(common.ya_xlsx_path, common.local_xlsx_path)

    workbook = load_workbook(common.local_xlsx_path)
    sheet = workbook[common.year]
    context.user_data['sheet'] = sheet
    context.user_data['workbook'] = workbook

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        if context.user_data.get("selected_income_category") is None:
            context.user_data['selected_income_category'] = common.DEFAULT_INCOME_INFO
        if context.user_data.get("selected_date") is None:
            context.user_data['selected_date'] = date.today()
    else:
        context.user_data['selected_income_category'] = common.DEFAULT_INCOME_INFO
        context.user_data['selected_date'] = date.today()

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "Доход\n"
            f"Категория: {context.user_data['selected_income_category']['name']}\n"
            f"Дата: {context.user_data['selected_date']}\n\n",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Доход\n"
            f"Категория: {context.user_data['selected_income_category']['name']}\n"
            f"Дата: {context.user_data['selected_date']}\n\n",
            reply_markup=reply_markup
        )

async def get_income_categories(update: Update, context: CallbackContext):
    sheet = context.user_data['sheet']
    category_list = []
    index = 21
    for col in sheet.iter_cols(min_col=21,min_row=2, max_col=24, values_only=True):
        category_list.append({"id": index, "name": col[0], "month": matches.get_month(index)})
        index += 1

    context.user_data['category_list'] = category_list
    
    keyboard = []
   
    for category in category_list:
        keyboard.append([
            InlineKeyboardButton(
                f"{category['name']}",
                callback_data=f"select_income_category_{category['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_income")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "Выберите категорию:",
            reply_markup=reply_markup
        )

async def select_income_category_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Извлекаем ID категории из callback_data
    category_id = int(query.data.replace("select_income_category_", ""))

    # Находим категорию в списке
    category_list = context.user_data.get('category_list', [])
    selected_category = next((c for c in category_list if c['id'] == category_id), None)

    if not selected_category:
        await query.edit_message_text("Категория не найдена!")
        return

    # Сохраняем выбранную категорию в контексте
    context.user_data['selected_income_category'] = selected_category
    await income(update, context)

async def process_calendar_callback(update: Update, context: CallbackContext):
    """Обработчик выбора даты из календаря"""
    query = update.callback_query
    await query.answer()
    
    calendar = context.user_data.get('calendar')
    
    if not calendar:
        calendar = DetailedTelegramCalendar()
    
    # Обрабатываем выбор в календаре
    result, key, step = calendar.process(query.data)
    
    if not result and key:
        # Обновляем календарь для следующего шага
        await query.edit_message_text(
            f"📅 Выберите дату ({LSTEP[step]}):",
            reply_markup=key
        )
    elif result:
        # Дата выбрана
        selected_date = result
        context.user_data['selected_date'] = selected_date
        
        await income(update, context)

async def ask_for_income(update: Update, context: CallbackContext):
    """Запрашиваем доход"""
    
    query = update.callback_query
    await query.answer()

    operator = query.data.replace("ask_for_income_", "")
    context.user_data['operator'] = operator

    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_income")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"Категория: {context.user_data['selected_income_category']['name']}\n"
        f"Дата: {context.user_data['selected_date']}\n\n"
        "Введите сумму дохода:",
        reply_markup=reply_markup)

async def get_income_view(update: Update, context: CallbackContext):
    """Запрашиваем просмотр дохода"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_income")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        sheet = context.user_data.get('sheet')
        selected_category = context.user_data.get('selected_income_category')
        # Запись данных
        month = context.user_data['selected_date'].strftime("%B")
        row = matches.get_month(month)
        col = matches.get_day_number(selected_category['id'])
        current_value = sheet[f'{col}{row}'].value
        if current_value is None:
            current_value = 0
        
        await query.edit_message_text(
                f"✅ Успешно!\n\n"
                f"Категория: {context.user_data['selected_income_category']['name']}\n"
                f"📅 Дата: {context.user_data['selected_date']}\n"
                f"💰 Текущий доход: {current_value}\n\n"
                "Что дальше?",
                reply_markup=reply_markup
            )

    except ValueError:
        await update.message.reply_text("При получении инфы о доходе произошла ошибка.")


async def process_income_input(update: Update, context: CallbackContext):
    """Обрабатывает введенное количество часов"""

    try:
        # Парсим введенное значение
        income_text = update.message.text.strip()
        income = float(update.message.text.strip().replace(',', '.'))
        
        # Проверяем валидность
        if income <= 0:
            await update.message.reply_text("Пожалуйста, введите положительное число:")
            return
        
        success = await backend_add_income_to_timesheet(context=context, income=income)
        
        if success:
            keyboard = [
                [InlineKeyboardButton("➕ Добавить доход", callback_data=f"ask_for_income_increment")],
                [InlineKeyboardButton("➖ Уменьшить доход", callback_data=f"ask_for_income_decrement")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_income")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ Успешно добавлено!\n\n"
                f"Категория: {context.user_data['selected_income_category']['name']}\n"
                f"📅 Дата: {context.user_data['selected_date']}\n"
                f"💰 Доход: {income}\n\n"
                "Что дальше?",
                reply_markup=reply_markup
            )
            client = common.get_ya_client(context._user_id)
            with client:
                client.upload(common.local_xlsx_path, common.ya_xlsx_path,overwrite=True)
            os.remove(common.local_xlsx_path)

        else:
            await update.message.reply_text("❌ Ошибка при добавлении дохода. Попробуйте еще раз.")

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число")

async def backend_add_income_to_timesheet(context: CallbackContext, income: float) -> bool:
    """Ваша бэкенд логика для добавления дохода в табель"""
    try:
        sheet = context.user_data.get('sheet')
        selected_category = context.user_data.get('selected_income_category')
        # Запись данных
        month = context.user_data['selected_date'].strftime("%B")
        row = matches.get_month(month)
        col = matches.get_day_number(selected_category['id'])
        current_value = sheet[f'{col}{row}'].value
        if current_value is None:
            current_value = 0
        if context.user_data['operator'] == "increment":
            sheet[f'{col}{row}'].value = float(current_value) + income
            logaction = "прибавлено"
            particle = "к"
        elif context.user_data['operator'] == "decrement":
            sheet[f'{col}{row}'].value = float(current_value) - income
            logaction = "вычтено"
            particle = "из"
        context.user_data.get('workbook').save(common.local_xlsx_path)
        common.logger.info(f"Изменен доход: Категория {context.user_data['selected_income_category']['name']}, "
            f"Дата: {context.user_data['selected_date']}, {particle} сумме: {current_value} {logaction} {income}. Результат: {sheet[f'{col}{row}'].value}")
        return True
    except Exception as e:
        common.logger.error(f"Ошибка при изменении дохода: {e}")
        return False