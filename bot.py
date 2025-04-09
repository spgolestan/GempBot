import telebot
from flask import Flask, request

TOKEN = '7528058827:AAF8uaUentzGSGUCa_DvjEuwal6ew7tbUd0'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "عکس شما دریافت شد!")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام! ربات آماده است.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
