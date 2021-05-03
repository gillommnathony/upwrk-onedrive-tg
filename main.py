import os
import logging
import time
import logging.config
import ntpath
from telebot import TeleBot, types
from dotenv import load_dotenv
from onedrive import OneDrive
from mongo import Mongo
from services import save_from_tg, create_keyboard
from settings import ONEDRIVE_USER, ONEDRIVE_FOLDER, LOGGING_CONF

logging.config.dictConfig(LOGGING_CONF)
logger = logging.getLogger(__name__)

load_dotenv()
current_mg_id = None
ondrv_folder = None

API_TOKEN = os.environ.get('BOT_TOKEN')
bot = TeleBot(API_TOKEN, parse_mode=None, threaded=False)
ondrv = OneDrive()
mongo = Mongo()

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

        res = mongo.add_user_chat(
            message.from_user.id,
            message.chat.id,
            message.chat.title
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

        res = mongo.delete_chat(
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


@bot.callback_query_handler(lambda query: True)
def query_text(query):
    if query.data.split('_')[0] == 'refresh':
        _, link_id = query.data.split('_')
        new_keyboard = create_keyboard(mongo, query.from_user.id, link_id)
        try:
            bot.edit_message_reply_markup(
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                reply_markup=new_keyboard
            )
        except Exception as e:
            logger.warning(e)

    else:
        chat_id, link_id = query.data.split('_')
        link = mongo.get_link(link_id)
        bot.send_message(chat_id, link)


def file_downloader(messages):
    logger.info('FileDownloader function.')
    global current_mg_id
    global ondrv_folder

    for message in messages:
        if message.chat.type == "private":
            folder_name = str(message.from_user.id) + str(message.date)

            if current_mg_id != message.media_group_id:
                if message.media_group_id is not None:
                    current_mg_id = message.media_group_id
                    ondrv_folder = ondrv.create_folder(
                        ONEDRIVE_USER, ONEDRIVE_FOLDER, folder_name)
                    link = ondrv.create_link(ONEDRIVE_USER, ondrv_folder)
                    link_id = mongo.add_user_link(link)

                    test_markup = create_keyboard(
                        mongo, message.from_user.id, link_id)
                    reply_msg = "Please, click button to send link to corresponding chat.\n"
                    reply_msg += "Click refresh button if you activated bot in new chats"

                    bot.send_message(
                        message.chat.id, reply_msg, reply_markup=test_markup)

            if message.media_group_id is not None:
                if message.content_type == 'photo':
                    logger.info('Photo message found.')
                    f_info = bot.get_file(message.json['photo'][-1]['file_id'])
                    f_info_name = ntpath.basename(f_info.file_path)
                    f_ext = f_info_name.split('.')[1]
                    f_title = f"{int(time.time())}_{f_info_name.split('.')[0]}"
                    f_name = f"{f_title}.{f_ext}"

                    f = save_from_tg(API_TOKEN, f_info)
                    ondrv.upload_file(
                        ONEDRIVE_USER,
                        ondrv_folder,
                        f_name,
                        f
                    )

                    logger.info('Photo message processed.')

                elif message.content_type == 'document':
                    logger.info('Document message found.')
                    f_info = bot.get_file(message.document.file_id)
                    f_name = message.document.file_name

                    f = save_from_tg(API_TOKEN, f_info)
                    ondrv.upload_file(
                        ONEDRIVE_USER,
                        ondrv_folder,
                        f_name,
                        f
                    )

                    logger.info('Document message processed.')


bot.set_update_listener(file_downloader)


def main(request):
    json_string = request.get_json()
    update = types.Update.de_json(json_string)

    bot.process_new_updates([update])
    return ''


if __name__ == "__main__":
    main()
