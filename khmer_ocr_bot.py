import telebot
import pytesseract
from PIL import Image
import io
import os


# ជំនួស 'YOUR_BOT_TOKEN' ជាមួយ Token របស់ Bot អ្នក
API_TOKEN = '7328885744:AAGDvDt85Se9oenNL-tAxr9MIMkU7ytuN30'
bot = telebot.TeleBot(API_TOKEN)


# Keep track of users who have started the bot
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

# មុខងារសម្រាប់ទទួលរូបភាព

@bot.message_handler(content_types=['photo', 'document'])
def handle_image(message):
    user_id = message.from_user.id
    if user_id not in started_users:
        bot.reply_to(message, "សូមចុច /start ជាមុនសិន ដើម្បីប្រើប្រាស់ bot នេះ។\nPlease send /start first to use this bot.")
        return
    try:
        # ផ្ញើសារប្រាប់ថា Bot កំពុងដំណើរការបម្លែង
        processing_message = bot.reply_to(message, "កំពុងបម្លែងរូបភាពទៅជាអក្សរ...")

        # ទទួលរូបភាព
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
        elif message.content_type == 'document' and 'image' in message.document.mime_type:
            file_info = bot.get_file(message.document.file_id)
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=processing_message.message_id, text="សូមមេត្តាផ្ញើតែរូបភាពប៉ុណ្ណោះ។")
            return

        downloaded_file = bot.download_file(file_info.file_path)

        # បើករូបភាពដោយប្រើ PIL
        image_stream = io.BytesIO(downloaded_file)
        img = Image.open(image_stream)

        # ប្រើ Tesseract OCR ជាមួយភាសាខ្មែរនិងអង់គ្លេស
        # ប្រើ option '--psm 6' សម្រាប់បម្លែងរូបភាពដែលមានអក្សរជាជួរៗ
        # option 'config' នេះជួយឱ្យការបម្លែងបានល្អជាងមុន
        ocr_result = pytesseract.image_to_string(img, lang='khm+eng', config='--psm 6')

        # ផ្ញើលទ្ធផលទៅអ្នកប្រើ
        if ocr_result.strip():  # ពិនិត្យមើលថាតើលទ្ធផលមានអក្សរឬអត់
            bot.edit_message_text(chat_id=message.chat.id, message_id=processing_message.message_id, text=ocr_result)
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=processing_message.message_id, text="មិនអាចស្គាល់អក្សរបានទេ សូមផ្ញើរូបភាពដែលច្បាស់ជាងមុន។")

    except Exception as e:
        # ដោះស្រាយករណីមានកំហុស
        error_message = f"មានកំហុស៖ {e}"
        bot.edit_message_text(chat_id=message.chat.id, message_id=processing_message.message_id, text=error_message)
        print(f"Error occurred: {e}")

# ចាប់ផ្ដើម Bot
print("Bot is running...")
bot.polling(none_stop=True)