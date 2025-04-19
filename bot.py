import psycopg2
from psycopg2 import sql
from psycopg2.pool import SimpleConnectionPool
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
pool = SimpleConnectionPool(1, 10,
                            dbname=config.DB_NAME,
                            user=config.DB_USER,
                            password=config.DB_PASSWORD,
                            host=config.DB_HOST,
                            port=config.DB_PORT)

# بررسی اتصال
try:
    conn = pool.getconn()
    cursor = conn.cursor()
    print("✅ اتصال به پایگاه داده موفقیت‌آمیز بود!")
except Exception as e:
    print("❌ خطا در اتصال به پایگاه داده:", e)

# ایجاد جدول اگر وجود نداشته باشد
try:
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
    print("✅ جدول applicants با موفقیت ایجاد یا تأیید شد!")
except Exception as e:
    conn.rollback()
    print(f"❌ خطا در ایجاد جدول: {e}")
finally:
 cursor.close()
 pool.putconn(conn)
# اتصال را برگردان
   
# دریافت توکن تلگرام
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if TOKEN is None or TOKEN.strip() == "":
    raise ValueError("❌ توکن بات تنظیم نشده یا نامعتبر است! لطفاً آن را در محیط متغیرها تنظیم کنید.")

bot = telebot.TeleBot(TOKEN)
def handle_error(chat_id, error_message):
    print(f"❌ خطا رخ داد: {error_message}")  # لاگ خطا را چاپ کن
    bot.send_message(chat_id, "❌ مشکلی در اجرای درخواست شما پیش آمد. لطفاً بعداً دوباره تلاش کنید.")
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 شروع", "👀 مشاهده شرایط کاری", "📌 مشاهده موقعیت‌های شغلی", "📝 ثبت‌نام برای همکاری", "📞 ارتباط با ما")
    
    bot.send_message(
        message.chat.id,
        "سلام! 🌟 به بات استخدامی مرکز خرید گلستان خوش آمدید.\nما آماده‌ایم تا فرصت‌های شغلی جذابی را به شما معرفی کنیم!",
        reply_markup=markup
    )
# نمایش موقعیت‌های شغلی فعال
def show_jobs(message):
    conn = pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT job_interest FROM applicants")
        jobs = cursor.fetchall()
        job_list = "\n".join([f"{index + 1}. {job[0]}" for index, job in enumerate(jobs)])
        bot.send_message(message.chat.id, f"📌 فرصت‌های شغلی موجود:\n{job_list} 🎯 از فرصت‌های فوق‌العاده استفاده کنید!")
    except Exception as e:
        handle_error(message.chat.id, str(e))
    finally:
        cursor.close()  # ابتدا cursor را ببند
        pool.putconn(conn)  # سپس اتصال را برگردان
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
    conn = pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO applicants (full_name, age, education, phone) VALUES (%s, %s, %s, %s)",
                       (full_name, age, education, phone))
        conn.commit()
        bot.send_message(message.chat.id, "🎉 اطلاعات شما با موفقیت ذخیره شد! 🌟")
    except Exception as e:
        conn.rollback()
        handle_error(message.chat.id, str(e))
    finally:
        cursor.close()  # ابتدا cursor را ببند
        pool.putconn(conn)  # سپس اتصال را برگردان   
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
import atexit

@atexit.register
def close_connections():
    pool.closeall()
    print("✅ همه اتصال‌های پایگاه داده بسته شدند.")