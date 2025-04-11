import telebot
import os

# دریافت توکن از متغیر محیطی (در Render تنظیم خواهی کرد)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ایجاد نمونه بات
bot = telebot.TeleBot(TOKEN)

# فرمان استارت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! به GEmploymentBot خوش آمدید. 👋")

# اجرای دائمی ربات
bot.polling()



bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "سلام! من وصل شدم 🎉")

bot.polling()
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    import telebot

    TOKEN = "توکن ربات خودت"
    bot = telebot.TeleBot(TOKEN)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Hello! I'm running on Render.")

    # اجرای Flask در یک ترد جداگانه
    threading.Thread(target=run_flask).start()
    
    # اجرای ربات
    bot.infinity_polling()

