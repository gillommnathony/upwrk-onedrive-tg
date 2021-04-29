from telebot import TeleBot, types
from dotenv import load_dotenv
from os import environ

load_dotenv()

bot = TeleBot(environ.get('BOT_TOKEN'), parse_mode=None)


send_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
send_btn = types.KeyboardButton('Send link to photos.')
send_markup.add(send_btn)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.chat.type == "private":
        reply_msg = "Hello\n"
        reply_msg += "Send your photos to me and I save them to One Drive."
        bot.reply_to(message, reply_msg, reply_markup=send_markup)
    if message.chat.type == "group":
        print(message)
        reply_msg = "Hello\n"
        reply_msg += "I will send a link to One Drive when I will be ready."
        bot.reply_to(message, reply_msg)


@bot.message_handler(func=lambda m: m == "Send link to photos.")
def echo_all(message):
    print(message)
    bot.send_message(-529328422, "Hello")
    reply_msg = "Link sent successfully!"
    bot.reply_to(message, reply_msg)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.send_message(-529328422, "Hello")
    bot.reply_to(message, message.text)


bot.polling()
