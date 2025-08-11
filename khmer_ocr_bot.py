
# --- Flask Webhook Version for Render Web Service ---
import telebot
import pytesseract
from PIL import Image
import io
import os
from flask import Flask, request

API_TOKEN = '7328885744:AAGDvDt85Se9oenNL-tAxr9MIMkU7ytuN30'
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')  # Set this in Render environment variables

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

started_users = set()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    started_users.add(user_id)
    welcome_message = """
សូមស្វាគមន៍មកកាន់ Telegram bot ដែលបម្លែងពីរូបភាពទៅជាអក្សរ ។​ \n
Welcome to the image to text conversion Telegram bot.\n
ខ្ញុំបាទឈ្មោះ ហេង សេងលៀង ជាអ្នកបង្កើត Telegram bot នេះឡើងក្នុងគោលបំណងសម្រាប់ងាយស្រួលដល់និស្សិតធ្វើការបម្លែងពីរូបភាពទៅជាអក្សរ ដូច្នេះសូមប្រើដោយក្ដីរីករាយ ! \n
I am Heng Sengleang, the creator of this Telegram bot, designed to facilitate students in converting images to text. Please use it with joy!\n
សូមផ្ញើរូបភាពមកខ្ញុំដើម្បីធ្វើការបម្លែងពីរូបភាពទៅជាអក្សរ ។​​​ \n
Please send an image to me for conversion from image to text.
"""
    bot.reply_to(message, welcome_message)

@bot.message_handler(content_types=['photo', 'document'])
def handle_image(message):
    user_id = message.from_user.id
    if user_id not in started_users:
        bot.reply_to(message, "សូមចុច /start ជាមុនសិន ដើម្បីប្រើប្រាស់ bot នេះ។\nPlease send /start first to use this bot.")
        return
    try:
        processing_message = bot.reply_to(message, "កំពុងបម្លែងរូបភាពទៅជាអក្សរ...")
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
        elif message.content_type == 'document' and 'image' in message.document.mime_type:
            file_info = bot.get_file(message.document.file_id)
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=processing_message.message_id, text="សូមមេត្តាផ្ញើតែរូបភាពប៉ុណ្ណោះ។")
            return
        downloaded_file = bot.download_file(file_info.file_path)
        image_stream = io.BytesIO(downloaded_file)
        img = Image.open(image_stream)
        ocr_result = pytesseract.image_to_string(img, lang='khm+eng', config='--psm 6')
        if ocr_result.strip():
            bot.edit_message_text(chat_id=message.chat.id, message_id=processing_message.message_id, text=ocr_result)
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=processing_message.message_id, text="មិនអាចស្គាល់អក្សរបានទេ សូមផ្ញើរូបភាពដែលច្បាស់ជាងមុន។")
    except Exception as e:
        error_message = f"មានកំហុស៖ {e}"
        bot.edit_message_text(chat_id=message.chat.id, message_id=processing_message.message_id, text=error_message)
        print(f"Error occurred: {e}")

# Flask route for Telegram webhook
@app.route(f"/webhook/{API_TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return '', 403

@app.route('/')
def index():
    return 'Telegram Khmer OCR Bot is running!'

if __name__ == "__main__":
    # Set webhook
    if WEBHOOK_URL:
        full_webhook_url = f"{WEBHOOK_URL}/webhook/{API_TOKEN}"
        bot.remove_webhook()
        bot.set_webhook(url=full_webhook_url)
        print(f"Webhook set to: {full_webhook_url}")
    else:
        print("WEBHOOK_URL environment variable not set!")
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)