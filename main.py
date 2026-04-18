import os
import telebot
import yt_dlp
import time
from telebot import types
from flask import Flask
from threading import Thread

# --- زانیاریێن بۆتی ---
API_TOKEN = "8643259960:AAEizSJj1TgwJNXxnU5fY_GO8HUAjP-I-M4"
CHANNEL_ID = "@tech_ai_falah"  # ناڤێ کەناڵێ خۆ لێرە بنووسە
CHANNEL_URL = "https://t.me/tech_ai_falah"
bot = telebot.TeleBot(API_TOKEN)

# --- پشکا پشکنینا جوین بوونێ ---
def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# --- فەرمانا دەستپێکێ (Start) ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    if check_sub(user_id):
        bot.send_message(message.chat.id, f"سڵاو {name}! ئێستا دەتوانی لینکی ڤیدیۆ بنێری بۆ دانڵۆدکردن.")
    else:
        markup = types.InlineKeyboardMarkup()
        join_btn = types.InlineKeyboardButton("Join Channel / جوین بکە", url=CHANNEL_URL)
        check_btn = types.InlineKeyboardButton("I Joined / جوین بووم", callback_data="check")
        markup.add(join_btn)
        markup.add(check_btn)
        bot.send_message(message.chat.id, f"بەڕێز {name}، تکایە سەرەتا جوینی کەناڵەکەمان بکە بۆ ئەوەی بتوانی ڤیدیۆ دانڵۆد بکەی:\n{CHANNEL_URL}", reply_markup=markup)

# --- پشکنین دوای کلیک کردن لە دوگمەی "جوین بووم" ---
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "سوپاس! ئێستا دەتوانی بۆتەکە بەکاربێنی.")
        bot.edit_message_text("تۆ سەرکەوتووانە جوین بووی! ئێستا لینکی ڤیدیۆکە بنێرە:", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "تۆ هێشتا جوین نەبووی! تکایە سەرەتا جوین بکە.", show_alert=True)

# --- پشکا دانڵۆدکردنا ڤیدیۆیێ ---
@bot.message_handler(func=lambda m: True)
def handle_download(message):
    if not check_sub(message.from_user.id):
        start(message)
        return

    url = message.text
    if not url.startswith("http"): return
    
    msg = bot.reply_to(message, "⏳ چاوەڕێ بە... Tech AI یا ڤیدیۆیێ دانلۆد دکەت")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'vid_{int(time.time())}.%(ext)s',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="ڤیدیۆیا تە ئامادەیە ب ڕێکا Tech AI ✅")
        
        os.remove(filename)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"ئیشکالەک هەیە: {str(e)}", message.chat.id, msg.message_id)

# --- پشکا هشیار هێلانا بۆتی (Flask) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Running!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
