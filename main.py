import os
import json
import logging
import logging.config
import ntpath
import requests
from time import time
from telebot import TeleBot, types
from dotenv import load_dotenv
from onedrive import OneDrive
from settings import SECRET_PATH, ONEDRIVE_USER, ONEDRIVE_FOLDER, LOGGING_CONF


logging.config.dictConfig(LOGGING_CONF)
logger = logging.getLogger(__name__)

load_dotenv()

token = os.environ.get('BOT_TOKEN')
allowed_users = os.environ.get('ALLOWED_USERS').split(':')
bot = TeleBot(token, parse_mode=None, threaded=False)
ondrv = OneDrive()

S_SEND_LINK = 'Send link to photos.'

send_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
send_markup.add(types.KeyboardButton(S_SEND_LINK))


@bot.message_handler(commands=['start'])
def start(message):
    logger.info('Start function.')
    if message.from_user.username in allowed_users:
        logger.info(f'Access for {message.from_user.username} granted')
        if message.chat.type == "private":
            logger.info('Private message.')
            reply_msg = "Hello\n"
            reply_msg += "Send your photos to me and I save them to One Drive."
            bot.reply_to(message, reply_msg, reply_markup=send_markup)

        elif message.chat.type == "group":
            logger.info('Group message.')
            allowed_chats = False
            if os.path.exists(SECRET_PATH):
                with open(SECRET_PATH, 'r') as f:
                    allowed_chats = json.loads(f.read())['chat_ids']
                    logger.info('Allowed chats exist.')

            ids = []
            if allowed_chats:
                ids.extend(allowed_chats)
            if message.chat.id not in set(ids):
                ids.append(message.chat.id)

            access = {"chat_ids": ids}
            with open(SECRET_PATH, 'w') as f:
                f.write(json.dumps(access))

            logger.info(f'Allowed chats updated with {ids}.')

            reply_msg = "Hello\n"
            reply_msg += "I will send a link to One Drive here."
            bot.reply_to(message, reply_msg, reply_markup=None)


@bot.message_handler(commands=['stop'])
def stop(message):
    logger.info('Stop function.')
    if message.from_user.username in allowed_users:
        logger.info(f'Access for {message.from_user.username} granted')
        if message.chat.type == "group":
            allowed_chats = False
            if os.path.exists(SECRET_PATH):
                with open(SECRET_PATH, 'r') as f:
                    allowed_chats = json.loads(f.read())['chat_ids']

            ids = []
            if allowed_chats:
                ids.extend(allowed_chats)
            if message.chat.id in set(ids):
                ids.remove(message.chat.id)

            access = {"chat_ids": ids}
            with open(SECRET_PATH, 'w') as f:
                f.write(json.dumps(access))

            logger.info(f'Allowed chats updated with {ids}.')

            reply_msg = "Goodbye\n"
            reply_msg += "Links won't be sent to that chat anymore."
            bot.reply_to(message, reply_msg)


@bot.message_handler(func=lambda m: m.text == S_SEND_LINK)
def send(message):
    logger.info('Send function.')
    if message.from_user.username in allowed_users:
        logger.info(f'Access for {message.from_user.username} granted')

        allowed_chats = False
        if os.path.exists(SECRET_PATH):
            with open(SECRET_PATH, 'r') as f:
                allowed_chats = json.loads(f.read())['chat_ids']

        if allowed_chats and len(allowed_chats) > 0:
            logger.info('Chats found.')
            for f_name in os.listdir('temp'):
                fp = os.path.join('temp', f_name)
                img = ondrv.upload_file(
                    ONEDRIVE_USER,
                    ONEDRIVE_FOLDER,
                    fp
                )
                os.remove(fp)
                logger.info(f'Photo {f_name} uploaded and removed.')

            for chat_id in allowed_chats:
                link = ondrv.create_link(
                    ONEDRIVE_USER,
                    ONEDRIVE_FOLDER,
                )
                bot.send_message(chat_id, link)
                logger.info(f'Link sent to chat with id={chat_id}')

            reply_msg = "Link sent successfully!"
        else:
            logger.info('No chats found.')

            reply_msg = "You have no chats to send photos to.\n"
            reply_msg += "Please, at first add bot to any group "
            reply_msg += "and write /start command."

        bot.reply_to(message, reply_msg)


def file_downloader(messages):
    logger.info('FileDownloader function.')
    for message in messages:
        if (message.from_user.username in allowed_users and
                message.chat.type == "private"):
            logger.info(f'Access for {message.from_user.username} granted')
            d_name = 'temp'
            if not os.path.exists(d_name):
                os.makedirs(d_name)

            if message.content_type == 'photo':
                logger.info('Photo message found.')
                f_info = bot.get_file(message.json['photo'][-1]['file_id'])
                f_info_name = ntpath.basename(f_info.file_path)
                f_ext = f_info_name.split('.')[1]
                f_title = f"{int(time())}_{f_info_name.split('.')[0]}"
                f_name = f"{f_title}.{f_ext}"

                res = requests.get(
                    f'https://api.telegram.org/file/bot{token}/{f_info.file_path}'
                )

                fp = os.path.join(d_name, f_name)
                with open(fp, 'wb') as f:
                    f.write(res.content)

                logger.info('Photo message processed.')

            elif message.content_type == 'document':
                logger.info('Document message found.')
                f_info = bot.get_file(message.document.file_id)
                f_name = message.document.file_name

                res = requests.get(
                    f"https://api.telegram.org/file/bot{token}/{f_info.file_path}"
                )

                fp = os.path.join(d_name, f_name)
                with open(fp, 'wb') as f:
                    f.write(res.content)

                logger.info('Document message processed.')


logger.info('Bot successfully started.')
bot.set_update_listener(file_downloader)
bot.polling()
