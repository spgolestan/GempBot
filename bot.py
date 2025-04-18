import psycopg2
import telebot
import os
from flask import Flask
import threading
import config  # بارگیری تنظیمات پایگاه داده از config.py

# دریافت اطلاعات پایگاه داده از متغیرهای محیطی
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# اتصال به پایگاه داده
try:
    conn = psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )
    cursor = conn.cursor()
    print("✅ اتصال به پایگاه داده موفقیت‌آمیز بود!")
except Exception as e:
    print("❌ خطا در اتصال به پایگاه داده:", e)

# ایجاد جدول اگر وجود نداشته باشد
cursor.execute("""
    CREATE TABLE IF NOT EXISTS applicants (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255),
        age INTEGER,
        education VARCHAR(255),
        experience TEXT,
        available_days TEXT[],
        job_interest VARCHAR(255),
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()
print("✅ جدول applicants با موفقیت ایجاد شد!")

# دریافت توکن تلگرام
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if TOKEN is None:
    raise ValueError("❌ توکن بات تنظیم نشده است!")

bot = telebot.TeleBot(TOKEN)

# فرمان استارت و نمایش گزینه‌های اصلی
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 شروع", "👀 مشاهده شرایط کاری", "📌 مشاهده موقعیت‌های شغلی", "📝 ثبت‌نام برای همکاری", "📞 ارتباط با ما")
    
    bot.send_message(message.chat.id, 
                     "سلام! به بات استخدامی مرکز خرید گلستان خوش آمدید. 🌟\n"
                     "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", 
                     reply_markup=markup)

# نمایش موقعیت‌های شغلی فعال
@bot.message_handler(func=lambda message: message.text == "📌 مشاهده موقعیت‌های شغلی")
def show_jobs(message):
    cursor.execute("SELECT job_interest FROM applicants")
    jobs = cursor.fetchall()
    job_list = "\n".join([f"- {job[0]}" for job in jobs])
    bot.send_message(message.chat.id, f"📌 فرصت‌های شغلی موجود:\n{job_list}")

# فرآیند ثبت‌نام کاربران
@bot.message_handler(commands=['register'])
def register_user(message):
    bot.send_message(message.chat.id, "📝 لطفاً نام و نام خانوادگی خود را وارد کنید:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    full_name = message.text
    bot.send_message(message.chat.id, "🔢 لطفاً سن خود را وارد کنید:")
    bot.register_next_step_handler(message, get_age, full_name)

def get_age(message, full_name):
    try:
        age = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ سن نامعتبر است! لطفاً عدد وارد کنید.")
        return bot.register_next_step_handler(message, get_age, full_name)
    
    bot.send_message(message.chat.id, "🎓 لطفاً میزان تحصیلات خود را وارد کنید:")
    bot.register_next_step_handler(message, get_education, full_name, age)

def get_education(message, full_name, age):
    education = message.text
    bot.send_message(message.chat.id, "📞 لطفاً شماره تماس خود را وارد کنید:")
    bot.register_next_step_handler(message, save_user, full_name, age, education)

def save_user(message, full_name, age, education):
    phone = message.text
    try:
        cursor.execute("INSERT INTO applicants (full_name, age, education, phone) VALUES (%s, %s, %s, %s)", 
                       (full_name, age, education, phone))
        conn.commit()
        bot.send_message(message.chat.id, "✅ اطلاعات شما با موفقیت ثبت شد!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطا در ذخیره اطلاعات: {e}")

# تنظیم Flask برای بررسی وضعیت ربات
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

# اجرای ربات و Flask
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()