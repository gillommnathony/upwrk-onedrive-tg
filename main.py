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
from sqlite import SQLite
from services import save_from_tg
from settings import SECRET_PATH, ONEDRIVE_USER, ONEDRIVE_FOLDER, LOGGING_CONF


logging.config.dictConfig(LOGGING_CONF)
logger = logging.getLogger(__name__)

load_dotenv()

token = os.environ.get('BOT_TOKEN')
bot = TeleBot(token, parse_mode=None, threaded=False)
ondrv = OneDrive()
sqlite = SQLite()

S_SEND_LINK = 'Send link to photos.'
send_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
send_markup.add(types.KeyboardButton(S_SEND_LINK))


@bot.message_handler(commands=['start'])
def start(message):
    logger.info('Start function.')
    if message.chat.type == "private":
        logger.info('Private message.')
        reply_msg = "Hello\n"
        reply_msg += "Send your photos to me and I save them to One Drive."
        bot.reply_to(message, reply_msg, reply_markup=None)

    elif message.chat.type == "group":
        logger.info('Group message.')

        res = sqlite.add_user_chat(
            message.from_user.id,
            message.chat.id
        )

        if res:
            reply_msg = "Hello\n"
            reply_msg += "I will send a link to One Drive here."
        else:
            reply_msg = "Some error occurred."

        logger.info(f'User chats updated with.')

        bot.reply_to(message, reply_msg, reply_markup=None)


@bot.message_handler(commands=['stop'])
def stop(message):
    logger.info('Stop function.')
    if message.chat.type == "group":

        res = sqlite.delete_chat(
            message.from_user.id,
            message.chat.id
        )

        if res:
            reply_msg = "Goodbye\n"
            reply_msg += "Links won't be sent to that chat anymore."
        else:
            reply_msg = "Some error occurred."

        logger.info(f'User chats updated with.')

        bot.reply_to(message, reply_msg)


@bot.message_handler(func=lambda m: m.text == S_SEND_LINK)
def send(message):
    logger.info('Send function.')
    chats = sqlite.get_user_chats(message.from_user.id)

    if chats:
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

        for chat_id in chats:
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
    mg_id = None
    mg_chat_id = None
    ondrv_folder = None

    for message in messages:
        print(message.date)
        if message.chat.type == "private":
            folder_name = str(message.from_user.id) + str(message.date)
            dp = os.path.join("temp", folder_name)
            if not os.path.exists(dp):
                os.makedirs(dp)

            if message.media_group_id is not None:
                mg_chat_id = message.chat.id
                if mg_id != message.media_group_id:
                    mg_id = message.media_group_id
                    folder_name = str(message.from_user.id) +\
                        str(message.date)
                    ondrv_folder = ondrv.create_folder(
                        ONEDRIVE_USER, ONEDRIVE_FOLDER, folder_name)

            if message.content_type == 'photo':
                logger.info('Photo message found.')
                f_info = bot.get_file(message.json['photo'][-1]['file_id'])
                f_info_name = ntpath.basename(f_info.file_path)
                f_ext = f_info_name.split('.')[1]
                f_title = f"{int(time())}_{f_info_name.split('.')[0]}"
                f_name = f"{f_title}.{f_ext}"

                fp = save_from_tg(token, f_info, f_name, dp)
                ondrv.upload_file(
                    ONEDRIVE_USER,
                    ondrv_folder,
                    fp
                )

                logger.info('Photo message processed.')

            elif message.content_type == 'document':
                logger.info('Document message found.')
                f_info = bot.get_file(message.document.file_id)
                f_name = message.document.file_name

                fp = save_from_tg(token, f_info, f_name, dp)
                ondrv.upload_file(
                    ONEDRIVE_USER,
                    ondrv_folder,
                    fp
                )

                logger.info('Document message processed.')

    if mg_chat_id is not None:
        bot.send_message(mg_chat_id, "hello")


logger.info('Bot successfully started.')
bot.set_update_listener(file_downloader)
bot.polling()
