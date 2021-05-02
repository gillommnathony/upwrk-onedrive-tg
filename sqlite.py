import sqlite3


class SQLite:
    def __init__(self):
        with sqlite3.connect('db.sqlite') as sc:
            cursor = sc.cursor()
            query = """CREATE TABLE IF NOT EXISTS accesses
            (
                user_id TEXT NOT NULL,
                chat_id TEXT NOT NULL
            )
            """
            cursor.execute(query)
            cursor.close()

    def add_user_chat(self, user_id, chat_id):
        with sqlite3.connect('db.sqlite') as sc:
            cursor = sc.cursor()
            query = f"""SELECT * 
            FROM accesses 
            WHERE user_id='{user_id}' and chat_id='{chat_id}'"""
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()

            if len(records) > 0:
                return True

            cursor = sc.cursor()
            user = str(user_id)
            chat = str(chat_id)
            query = f"INSERT INTO accesses VALUES ('{user}','{chat}')"
            cursor.execute(query)
            cursor.close()

        return True

    def get_user_chats(self, user_id):
        with sqlite3.connect('db.sqlite') as sc:
            cursor = sc.cursor()
            query = f"SELECT * FROM accesses WHERE user_id='{user_id}'"
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()

            if len(records) <= 0:
                return set()

            data = set()
            for user_id, chat_id in records:
                data.add(chat_id)

        return data

    def delete_chat(self, user_id, chat_id):
        with sqlite3.connect('db.sqlite') as sc:
            cursor = sc.cursor()
            query = f"""DELETE FROM accesses 
            WHERE user_id='{user_id}' and chat_id='{chat_id}'"""
            cursor.execute(query)
            cursor.close()

        return True
