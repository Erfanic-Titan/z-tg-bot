from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
from db4 import database_create_connection
import json
import logging
from languages import languages
import os
import base64
<<<<<<< HEAD
from buttons2 import create_keyboard
=======
from ai_buttons import create_ai_keyboard
>>>>>>> bd6d513 (Initial commit)
import asyncio

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ai_tool.log'
)
logger = logging.getLogger(__name__)

# تنظیم کلید API جمینی
GOOGLE_API_KEY = "AIzaSyAHHkMQa9h_-tbBmyY9qt0v4D14-vgOdHQ"
genai.configure(api_key=GOOGLE_API_KEY)

# تنظیم مدل جمینی
model = genai.GenerativeModel('gemini-1.5-pro')

class AIChat:
    def __init__(self, chat_id: int, user_id: int):
        self.chat_id = chat_id
        self.user_id = user_id
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
    async def send_message(self, content: str, file_data=None):
        try:
            # آماده‌سازی پیام با توجه به نوع فایل
            if file_data:
                if isinstance(file_data, dict):
                    if file_data['type'] == 'image':
                        response = await self.model.generate_content_async([content, file_data['data']])
                    elif file_data['type'] in ['video', 'audio', 'document']:
                        response = await self.model.generate_content_async(
                            f"{content}\n[File type: {file_data['type']}]\n{file_data['description']}"
                        )
                else:
                    response = await self.model.generate_content_async(content)
            else:
                response = await self.model.generate_content_async(content)
            
            # ذخیره پیام‌ها در دیتابیس
            conn = database_create_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO ai_messages (chat_id, content, role) VALUES (%s, %s, %s)",
                    (self.chat_id, content, 'user')
                )
                cursor.execute(
                    "INSERT INTO ai_messages (chat_id, content, role) VALUES (%s, %s, %s)",
                    (self.chat_id, response.text, 'assistant')
                )
                conn.commit()
            finally:
                conn.close()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in send_message: {str(e)}")
            return None

# ذخیره چت‌های فعال
active_chats = {}

async def get_or_create_chat(user_id: int) -> AIChat:
    if user_id not in active_chats:
        active_chats[user_id] = AIChat(user_id)
    return active_chats[user_id]

async def save_chat_history(user_id: int, chat_name: str, history: list):
    try:
        conn = database_create_connection()
        cursor = conn.cursor()
        
        # ذخیره تاریخچه چت در دیتابیس
        cursor.execute("""
            INSERT INTO ai_chat_history (user_id, chat_name, history, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, chat_name, json.dumps(history)))
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"Error saving chat history: {str(e)}")
    finally:
        conn.close()

async def load_chat_history(user_id: int) -> list:
    try:
        conn = database_create_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT chat_name, history FROM ai_chat_history
            WHERE user_id = %s ORDER BY created_at DESC
        """, (user_id,))
        
        chats = cursor.fetchall()
        return [{"name": chat[0], "history": json.loads(chat[1])} for chat in chats]
        
    except Exception as e:
        logger.error(f"Error loading chat history: {str(e)}")
        return []
    finally:
        conn.close()

async def handle_ai_message(client: Client, message: Message, language_code: str):
    try:
        user_id = message.from_user.id
        
        # ارسال پیام "در حال فکر کردن"
        thinking_msg = await message.reply("در حال فکر کردن... 🤔", quote=True)
        
        # دریافت یا ایجاد چت
        chat = await get_or_create_chat(user_id)
        
        # پردازش تصویر اگر وجود داشته باشد
        image_data = None
        if message.photo:
            file_path = await message.download()
            with open(file_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode()
            os.remove(file_path)
        
        # دریافت متن پیام
        user_message = message.text or message.caption or ""
        if not user_message and message.voice:
            user_message = "لطفاً این پیام صوتی را تحلیل کن"
        elif not user_message and message.video:
            user_message = "لطفاً این ویدیو را تحلیل کن"
        elif not user_message and message.document:
            user_message = "لطفاً این فایل را تحلیل کن"
        
        # دریافت پاسخ از مدل
        response = await chat.send_message(user_message, image_data)
        
        # ارسال پاسخ به صورت استریم
        if not response:
            await thinking_msg.edit(languages[language_code]['ai_error'])
            return

        # تقسیم پاسخ به قطعات ۱۰۰ کاراکتری برای نمایش استریم
        chunk_size = 100
        chunks = [response[i:i+chunk_size] for i in range(0, len(response), chunk_size)]
        
        # نمایش استریم پاسخ
        current_text = ""
        for chunk in chunks:
            current_text += chunk
            try:
                await thinking_msg.edit(current_text)
                await asyncio.sleep(0.1)  # تاخیر کوتاه برای نمایش بهتر استریم
            except Exception as e:
                logger.error(f"Error in streaming response: {e}")
                # اگر ویرایش پیام با خطا مواجه شد، پیام جدید ارسال می‌کنیم
                if current_text:
                    await message.reply(current_text, quote=True)
                break
        
    except Exception as e:
        logger.error(f"Error in handle_ai_message: {str(e)}")
        await thinking_msg.edit(languages[language_code]['ai_error'])

def create_chat_keyboard(language_code: str, chat_list: list) -> InlineKeyboardMarkup:
    keyboard = []
    
    # دکمه چت جدید
    keyboard.append([InlineKeyboardButton(
        languages[language_code]['new_chat'],
        callback_data="ai_new_chat"
    )])
    
    # لیست چت‌های موجود
    for chat in chat_list:
        keyboard.append([InlineKeyboardButton(
            chat['name'],
            callback_data=f"ai_load_chat_{chat['name']}"
        )])
    
    return InlineKeyboardMarkup(keyboard)

async def show_chat_menu(client: Client, chat_id: int, language_code: str):
<<<<<<< HEAD
    # نمایش منوی چت‌ها
    chat_list = await load_chat_history(chat_id)
    keyboard = create_keyboard(language_code, 'artificial-intelligence')  # تغییر این خط
    
    # اضافه کردن متن خوش‌آمدگویی به پیام اصلی
=======
    chat_list = await get_user_chats(chat_id)
    keyboard = create_ai_keyboard(language_code, chat_list)  # از تابع جدید استفاده می‌کنیم
    
>>>>>>> bd6d513 (Initial commit)
    text = languages[language_code]['ai_welcome'] + "\n\n" + languages[language_code]['select_chat']
    
    await client.send_message(
        chat_id,
        text,
        reply_markup=keyboard
    )


async def create_new_chat(user_id: int, chat_name: str = "چت جدید") -> int:
    conn = database_create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO ai_chats (user_id, chat_name) VALUES (%s, %s)",
            (user_id, chat_name)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

async def get_user_chats(user_id: int) -> list:
    conn = database_create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT id, chat_name, created_at 
            FROM ai_chats WHERE user_id = %s 
            ORDER BY created_at DESC""",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()

async def rename_chat(chat_id: int, new_name: str):
    conn = database_create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE ai_chats SET chat_name = %s WHERE id = %s",
            (new_name, chat_id)
        )
        conn.commit()
    finally:
        conn.close()

async def delete_chat(chat_id: int):
    conn = database_create_connection()
    cursor = conn.cursor()
    try:
        # اول پیام‌های چت را پاک می‌کنیم
        cursor.execute("DELETE FROM ai_messages WHERE chat_id = %s", (chat_id,))
        # سپس خود چت را پاک می‌کنیم
        cursor.execute("DELETE FROM ai_chats WHERE id = %s", (chat_id,))
        conn.commit()
    finally:
        conn.close()