from pyrogram import Client, filters, enums
from pyrogram.types import ReplyKeyboardRemove
from buttons2 import *
from languages import *
import os
from db4 import *
import time
import re
from ai_tool import handle_ai_message, show_chat_menu, get_or_create_chat
import asyncio

# env
bot_token = os.environ.get("TOKEN", "7752567428:AAGtdwtAWyyi5IANET-xuG3TuUUMMn6yvB4") 
api_hash = os.environ.get("HASH", "a7d65ff251cb1c8cf51f3ca1b90b5a0a") 
api_id = os.environ.get("ID", "25791738")

# bot
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_type_status = {}

@app.on_message(filters.command("start"))
async def start(client_parametr, info_message_parametr):
    chat_id_user_start = info_message_parametr.from_user.id
    first_name = info_message_parametr.from_user.first_name
    last_name = info_message_parametr.from_user.last_name

    it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chat_id_user_start)

    if it_is_true_exists:
        keyboards = create_keyboard(language_code, 'welcome-send-text')
        await info_message_parametr.reply(
            languages[language_code]['welcome-send-text'],
            reply_markup=keyboards,
            reply_to_message_id=info_message_parametr.id
        )
    else:
        await info_message_parametr.reply(
            languages['start-text'],
            reply_markup=keyboard_select_orders_or_tools,
            reply_to_message_id=info_message_parametr.id
        )

@app.on_callback_query()
async def handle_callback_query_for_select_language(client, callback_query):
    data = callback_query.data
    user_id_user_click_callback = callback_query.from_user.id
    chat_id_user_click_callback = callback_query.message.chat.id
    first_name_user_click_callback = callback_query.from_user.first_name
    last_name_user_click_callback = callback_query.from_user.last_name
    user_name_user_click_callback = callback_query.from_user.username

    it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chat_id_user_click_callback)

    if data in ('fa', 'en'):
        database_insert_data(
            chat_id_user_click_callback,
            first_name_user_click_callback,
            last_name_user_click_callback,
            user_name_user_click_callback,
            data
        )
        await callback_query.answer(languages[data]['select-language'])
        keyboards = create_keyboard(data, 'select-language')
        await callback_query.edit_message_text(
            text=languages[data]['welcome-send-text'],
            reply_markup=keyboards
        )

    if data in ('tools', 'orders', 'setting', 'account'):
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code][f'{data}-text'],
            reply_markup=keyboards
        )
    
    if data == 'change-language':
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code][f'{data}-text'],
            reply_markup=keyboards
        )
        
    if data in ('fa-change', 'en-change'):
        result_change = data.split('-')[0]
        await callback_query.answer(languages[result_change]['change-language-db-text'])
        
    if data == '2fa':
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code][f'{data}-text'],
            reply_markup=keyboards
        )
        
    if data == 'clear-database':
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code][f'{data}-text'],
            reply_markup=keyboards
        )

    if data == 'clear-database-yes':
        await callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes'])
        await asyncio.sleep(2)
        await callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes2'])
        await asyncio.sleep(2)
        await callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes3'])
        await asyncio.sleep(2)
        await callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes4'])
        await asyncio.sleep(2)
        await callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes5'])
        await asyncio.sleep(1)
        await callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes6'])
        await asyncio.sleep(1)
        await callback_query.edit_message_text(text=languages[language_code]['change-language-db-text-yes7'])
        
    if data == 'clear-database-nope':
        keyboards = create_keyboard(language_code, 'back-menu-for-else')
        await callback_query.edit_message_text(
            text=languages[language_code]['welcome-send-text'],
            reply_markup=keyboards
        )
        
    if data == 'account-upgrade':
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code][f'{data}-text'],
            reply_markup=keyboards
        )     
    
    if data == 'active-by-user-password':
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code][f'{data}-text'],
            reply_markup=keyboards
        )     
    
    if data == 'activate-with-email-and-password':
        state = user_type_status.get(chat_id_user_click_callback, None)
        if state is None:
            user_type_status[chat_id_user_click_callback] = "waiting_for_email"
            await callback_query.edit_message_text(
                text=languages[language_code]['a-written-text-for-requesting-to-send-an-email']
            )
    
    if data == 'activate-with-phone':
        user_type_status[chat_id_user_click_callback] = "waiting_for_phone"
        state = user_type_status.get(chat_id_user_click_callback, None)
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code][f'{data}-text'],
            reply_markup=keyboards
        )
        if state == "waiting_for_phone":
            keyboards = create_keyboard(language_code, 'send-button-number')
            await callback_query.message.reply_text(
                languages[language_code]['xx'],
                reply_markup=keyboards
            )
             
    if data == 'activate-with-phone-text-button-nope':
        user_type_status.pop(chat_id_user_click_callback, None)
        remove_keyboard = ReplyKeyboardRemove()
        await callback_query.message.reply_text(
            languages[language_code]['deleted-keyboard-send-phone'],
            reply_markup=remove_keyboard
        )
        keyboards = create_keyboard(language_code, 'account-upgrade')
        await callback_query.edit_message_text(
            languages[language_code]['account-upgrade-text'],
            reply_markup=keyboards
        )
    
    if data == 'account-status-guide':
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code][f'{data}-text'],
            reply_markup=keyboards
        )
        
    if data == 'recovery-account':
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code][f'{data}-text'],
            reply_markup=keyboards
        )
        
    if data == 'invitation-to-friends':
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code][f'{data}-text'],
            reply_markup=keyboards
        )
        
    if data == 'history-of-my-account':
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code][f'{data}-text'],
            reply_markup=keyboards
        )
        
    if data == 'wallet-recharge':
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code][f'{data}-text'],
            reply_markup=keyboards
        )

    if data == 'back-home':
        keyboards = create_keyboard(language_code, f'{data}')
        await callback_query.edit_message_text(
            text=languages[language_code]['welcome-send-text'],
            reply_markup=keyboards
        )

    if data == 'artificial-intelligence':
        keyboards = create_keyboard(language_code, 'artificial-intelligence')
        
        await callback_query.message.delete()
        await show_chat_menu(client, chat_id_user_click_callback, language_code)


    # در تابع handle_callback_query_for_select_language اضافه کنید:
    
    # برای دکمه چت جدید
    if data == "ai_new_chat":
        user_type_status[chat_id_user_click_callback] = "ai_chat"
        await callback_query.answer("چت جدید شروع شد!")
        await callback_query.message.reply("لطفاً پیام خود را ارسال کنید.")

    # برای دکمه پاکسازی تاریخچه
    elif data == "ai_clear_history":
        # پاک کردن تاریخچه از دیتابیس
        conn = database_create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ai_chat_history WHERE user_id = %s", (chat_id_user_click_callback,))
        conn.commit()
        conn.close()
        
        await callback_query.answer("تاریخچه چت‌ها پاک شد!")
        keyboards = create_keyboard(language_code, 'artificial-intelligence')
        await callback_query.message.edit_text(
            languages[language_code]['ai_welcome'],
            reply_markup=keyboards
        )

    # برای دکمه بازگشت
    elif data == "back-menu-for-else":
        user_type_status[chat_id_user_click_callback] = None  # پاک کردن وضعیت AI
        keyboards = create_keyboard(language_code, 'tools')
        await callback_query.message.edit_text(
            languages[language_code]['tools-text'],
            reply_markup=keyboards
        )

@app.on_message(filters.command(["help"]) & filters.private)
async def help_command(client, message):
    chat_id = message.chat.id
    it_is_true_exists, _, _, _, _, language_code = check_for_existence_in_the_database(chat_id)
    if it_is_true_exists:
        await message.reply(languages[language_code]['ai_help'])

@app.on_message(
    (filters.text | filters.photo | filters.video | filters.audio | filters.voice | filters.document) &
    filters.private
)
async def process_ai_message(client, message):
    chat_id = message.chat.id
    it_is_true_exists, _, _, _, _, language_code = check_for_existence_in_the_database(chat_id)
    
    if it_is_true_exists:
        # بررسی وضعیت فعلی کاربر
        state = user_type_status.get(chat_id)
        
        # اگر کاربر در وضعیت چت با هوش مصنوعی است
        if state == "ai_chat":
            await handle_ai_message(client, message, language_code)
        else:
            # پردازش سایر پیام‌ها
            await handler_email(client, message)

@app.on_message(filters.private & filters.text)
async def handler_email(client, message):
    chat_id_user_active_with_email_password = message.chat.id
    chid = message.from_user.id
    it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chid)
    
    state = user_type_status.get(chat_id_user_active_with_email_password, None)
        
    if state == "waiting_for_email":
        user_input = message.text
        email_is_or_not_safe, safe_input_email = sanitize_input(user_input)

        if is_valid_gmail(safe_input_email):
            await message.reply(
                languages[language_code]['written-text-for-a-password-request'],
                reply_to_message_id=message.id
            )
            user_type_status[chat_id_user_active_with_email_password] = "waiting_for_password"
        else:
            await message.reply(
                languages[language_code]['the-written-text-for-an-incorrect-email'],
                reply_to_message_id=message.id
            )

    elif state == "waiting_for_password":
        user_input_password = message.text 
        password_is_or_not_safe, safe_output_password = sanitize_input(user_input_password)

        if not password_is_or_not_safe:
            await message.reply(languages[language_code]['written-text-for-unsafe-characters'])
        else:
            if validate_password(safe_output_password):
                keyboards = create_keyboard(language_code, 'text-announcement-to-declare-the-end-of-the-request-for-email-and-password-operations')
                await message.reply(
                    languages[language_code]['text-announcement-to-declare-the-end-of-the-request-for-email-and-password-operations'],
                    reply_markup=keyboards
                )
                user_type_status.pop(chat_id_user_active_with_email_password, None)
            else:
                await message.reply(languages[language_code]['text-for-password-length'])

def is_valid_gmail(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return re.match(pattern, email) is not None

def sanitize_input(user_input):
    dangerous_pattern = r'[<>;&\'"\/();{}[\]\\#|^]'
    if re.search(dangerous_pattern, user_input):
        safe_output_password = re.sub(dangerous_pattern, '00', user_input)
        return False, safe_output_password
    return True, user_input

def validate_password(password):
    if len(password) == 12:
        pattern = r'^[!?@$*()0-9a-zA-Z]+$'
        return re.match(pattern, password) is not None
    return False


@app.on_message(filters.contact)
async def handle_contact(client, message):
    chid = message.from_user.id
    chtid = message.chat.id
    it_is_true_exists, chat_id, first_name, last_name, user_name, language_code = check_for_existence_in_the_database(chtid)
    phone_number = message.contact.phone_number
    formatted_number = "+" + phone_number
    country_code = phone_number[:2]
    local_number = phone_number[2:]
    user_type_status.pop(chtid, None)
    print("شماره فرمت شده:", formatted_number)
    print("کد کشور:", country_code)
    print("شماره محلی:", local_number)
    remove_keyboard = ReplyKeyboardRemove()
    await message.reply_text(languages[language_code]['deleted-keyboard-send-phone'], reply_markup=remove_keyboard)


app.run()