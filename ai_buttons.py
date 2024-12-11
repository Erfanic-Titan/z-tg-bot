from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from languages import languages

def create_ai_keyboard(language_code: str, chat_list=None):
    keyboard = [
        [InlineKeyboardButton(languages[language_code]['new_chat'], callback_data='ai_new_chat')],
        [InlineKeyboardButton("🗑 " + languages[language_code]['clear-database'], callback_data="ai_clear_history")],
        [InlineKeyboardButton(languages[language_code]['back'], callback_data='back-menu-for-else')]
    ]
    
    # اگر چت‌های قبلی وجود دارند، نمایش داده شوند
    if chat_list:
        for chat in chat_list:
            keyboard.insert(-1, [
                InlineKeyboardButton(
                    f"💬 {chat[1]}",  # نام چت
                    callback_data=f"ai_select_chat_{chat[0]}"
                ),
                InlineKeyboardButton(
                    "✏️",  # دکمه تغییر نام
                    callback_data=f"ai_rename_chat_{chat[0]}"
                ),
                InlineKeyboardButton(
                    "🗑️",  # دکمه حذف
                    callback_data=f"ai_delete_chat_{chat[0]}"
                )
            ])
    
    return InlineKeyboardMarkup(keyboard)
