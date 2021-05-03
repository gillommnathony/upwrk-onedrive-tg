import os
import requests
from telebot import types


def save_from_tg(token, f_info):
    res = requests.get(
        f"https://api.telegram.org/file/bot{token}/{f_info.file_path}"
    )

    return res.content


def create_keyboard(sqlite, user_id, link_id):
    chats = sqlite.get_user_chats(user_id)

    test_markup = types.InlineKeyboardMarkup(row_width=5)
    callback_data = f"refresh_{link_id}"
    test_markup.add(
        types.InlineKeyboardButton(
            text="🔄 Refresh",
            callback_data=callback_data,
        )
    )

    inline_buttons = []
    for chat in chats:
        callback_data = f"{chat['chat_id']}_{link_id}"
        inline_buttons.append(
            types.InlineKeyboardButton(
                text=chat['chat_name'],
                callback_data=callback_data
            )
        )
    test_markup.add(*inline_buttons)

    return test_markup
