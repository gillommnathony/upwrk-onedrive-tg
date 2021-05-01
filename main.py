import logging
import logging.config
import ntpath
import requests
from telebot import TeleBot, types
from dotenv import load_dotenv
import os
import json


load_dotenv()

token = os.environ.get('BOT_TOKEN')
bot = TeleBot(token, parse_mode=None)
allowed_users = os.environ.get('ALLOWED_USERS').split(':')
secret_path = "secret.json"

S_SEND_LINK = 'Send link to photos.'


send_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
send_markup.add(types.KeyboardButton(S_SEND_LINK))


@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.username in allowed_users:
        if message.chat.type == "private":
            reply_msg = "Hello\n"
            reply_msg += "Send your photos to me and I save them to One Drive."
            bot.reply_to(message, reply_msg, reply_markup=send_markup)

        elif message.chat.type == "group":
            allowed_chats = False
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    allowed_chats = json.loads(f.read())['chat_ids']

            ids = []
            if allowed_chats:
                ids.extend(allowed_chats)
            if message.chat.id not in set(ids):
                ids.append(message.chat.id)

            access = {"chat_ids": ids}
            with open(secret_path, 'w') as f:
                f.write(json.dumps(access))

            reply_msg = "Hello\n"
            reply_msg += "I will send a link to One Drive here."
            bot.reply_to(message, reply_msg, reply_markup=None)


@bot.message_handler(commands=['stop'])
def stop(message):
    if message.from_user.username in allowed_users:
        if message.chat.type == "group":
            allowed_chats = False
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    allowed_chats = json.loads(f.read())['chat_ids']

            ids = []
            if allowed_chats:
                ids.extend(allowed_chats)
            if message.chat.id in set(ids):
                ids.remove(message.chat.id)

            access = {"chat_ids": ids}
            with open(secret_path, 'w') as f:
                f.write(json.dumps(access))

            reply_msg = "Goodbye\n"
            reply_msg += "Links won't be sent to that chat anymore."
            bot.reply_to(message, reply_msg)


@bot.message_handler(func=lambda m: m.text == S_SEND_LINK)
def send(message):
    if message.from_user.username in allowed_users:
        if os.path.exists(secret_path):
            with open(secret_path, 'r') as f:
                allowed_chats = json.loads(f.read())['chat_ids']

            for chat_id in allowed_chats:
                onedrive_link = "https://onedrive.com"
                bot.send_message(chat_id, onedrive_link)

            reply_msg = "Link sent successfully!"

        else:
            reply_msg = "You have no chats to send photos to.\n"
            reply_msg += "Please, add bot to any group first."

        bot.reply_to(message, reply_msg)


@bot.message_handler(content_types=['document', 'photo'])
def files(message):
    if message.from_user.username in allowed_users:
        d_name = 'temp'
        if not os.path.exists(d_name):
            os.makedirs(d_name)

        if message.content_type == 'photo':
            f_info = bot.get_file(message.json['photo'][-1]['file_id'])
            f_ext = ntpath.basename(f_info.file_path).split('.')[1]
            f_name = f"{message.date}.{f_ext}"

            res = requests.get(
                f'https://api.telegram.org/file/bot{token}/{f_info.file_path}')

            fp = os.path.join(d_name, f_name)
            with open(fp, 'wb') as f:
                f.write(res.content)

        elif message.content_type == 'document':
            f_info = bot.get_file(message.document.file_id)
            f_name = message.document.file_name

            res = requests.get(
                f"https://api.telegram.org/file/bot{token}/{f_info.file_path}")

            fp = os.path.join(d_name, f_name)
            with open(fp, 'wb') as f:
                f.write(res.content)


bot.polling()
