import telebot
import os
from flask import Flask
import threading

# دریافت توکن از متغیر محیطی
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if TOKEN is None:
    raise ValueError("TOKEN is not set! Please configure the environment variable.")

# ایجاد نمونه بات
bot = telebot.TeleBot(TOKEN)

# فرمان استارت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! به GEmploymentBot خوش آمدید. 👋")

# تنظیم Flask برای بررسی وضعیت ربات
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))  # خواندن پورت از متغیر محیطی

# اجرای Flask و ربات در دو ترد جداگانه
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
