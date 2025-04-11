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

