import logging
import logging.config
from telebot import TeleBot, types
from dotenv import load_dotenv
import os
import json


load_dotenv()

bot = TeleBot(os.environ.get('BOT_TOKEN'), parse_mode=None)
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
            reply_msg += "I will send a link to One Drive when I will be ready."
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
        if message.content_type == 'photo':
            print(message.json['photo'][0]['file_id'])
            # Document has name
            # Photo hasn't
        elif message.content_type == 'document':
            print(message.document)


bot.polling()
