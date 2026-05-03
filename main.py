import telebot
from telebot import types
import requests
import os
from flask import Flask
from threading import Thread

# 1. Render port xatosini oldini olish (Flask)
app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Bot sozlamalari
TOKEN = '8742839052:AAE7G3VeexHvZ_ulCrOrJXK6boorJaNz98Y'
bot = telebot.TeleBot(TOKEN)

# 3. Serverni yoqish
keep_alive()

strings = {
    'uz': {
        'welcome': "👋 Assalomu alaykum! Instagram video yuklovchi botga xush kelibsiz.\n\n✅ Link yuboring, video va musiqasini yuklab beraman!",
        'choose_lang': "🇺🇿 Tilni tanlang:",
        'ask_link': "📥 Instagram linkini yuboring!",
        'not_found': "❌ Video topilmadi yoki link xato!",
        'music_btn': "🎵 Video musiqasi",
        'wait': "⏳ Video tayyorlanmoqda..."
    },
    'ru': {
        'welcome': "👋 Привет! Я бот для скачивания видео из Instagram.\n\n✅ Пришлите ссылку!",
        'choose_lang': "🇷🇺 Выберите язык:",
        'ask_link': "📥 Пришлите ссылку на Instagram!",
        'not_found': "❌ Видео не найдено!",
        'music_btn': "🎵 Музыка из видео",
        'wait': "⏳ Видео готовится..."
    },
    'en': {
        'welcome': "👋 Hello! Instagram video downloader bot.\n\n✅ Send a link!",
        'choose_lang': "🇺🇸 Choose a language:",
        'ask_link': "📥 Send an Instagram link!",
        'not_found': "❌ Video not found!",
        'music_btn': "🎵 Video music",
        'wait': "⏳ Preparing video..."
    }
}

user_lang = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("O'zbek tili 🇺🇿", callback_data='lang_uz'),
        types.InlineKeyboardButton("Русский язык 🇷🇺", callback_data='lang_ru'),
        types.InlineKeyboardButton("English 🇺🇸", callback_data='lang_en')
    )
    bot.send_message(message.chat.id, f"{strings['uz']['welcome']}\n\n{strings['uz']['choose_lang']}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_lang(call):
    lang = call.data.split('_')[1]
    user_lang[call.message.chat.id] = lang
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, strings[lang]['ask_link'])

@bot.message_handler(func=lambda message: "instagram.com" in message.text)
def download(message):
    lang = user_lang.get(message.chat.id, 'uz')
    bot.send_message(message.chat.id, strings[lang]['wait'])
    try:
        # Kuchaytirilgan API so'rovi
        res = requests.post("https://api.cobalt.tools/api/json", 
                            json={
                                "url": message.text.strip(), 
                                "vQuality": "720",
                                "isNoTTWatermark": True
                            },
                            headers={
                                "Accept": "application/json", 
                                "Content-Type": "application/json",
                                "Referer": "https://cobalt.tools/"
                            })
        video_url = res.json().get('url')
        if video_url:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(strings[lang]['music_btn'], callback_data=f"music_{video_url}"))
            bot.send_video(message.chat.id, video_url, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, strings[lang]['not_found'])
    except:
        bot.send_message(message.chat.id, strings[lang]['not_found'])

@bot.callback_query_handler(func=lambda call: call.data.startswith('music_'))
def get_audio(call):
    bot.send_audio(call.message.chat.id, call.data.replace("music_", ""))

bot.polling(none_stop=True)
