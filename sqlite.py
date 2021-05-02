import sqlite3


class SQLite:
    def __init__(self):
        with sqlite3.connect('db.sqlite') as sc:
            cursor = sc.cursor()
            query = """CREATE TABLE IF NOT EXISTS accesses
            (
                user_id TEXT NOT NULL,
                chat_id TEXT NOT NULL,
                chat_name TEXT NOT NULL
            )
            """
            cursor.execute(query)
            query = """CREATE TABLE IF NOT EXISTS links
            (
                link TEXT NOT NULL
            )
            """
            cursor.execute(query)
            cursor.close()

    def add_user_chat(self, user_id, chat_id, chat_name):
        with sqlite3.connect('db.sqlite') as sc:
            cursor = sc.cursor()
            query = f"""SELECT rowid
            FROM accesses 
            WHERE user_id='{user_id}' and chat_id='{chat_id}'"""
            cursor.execute(query)
            record = cursor.fetchone()
            cursor.close()

            if record is not None:
                return record[0]

            cursor = sc.cursor()
            user = str(user_id)
            chat = str(chat_id)
            query = f"""INSERT INTO accesses
            VALUES ('{user}','{chat}','{chat_name}')"""
            cursor.execute(query)
            record_id = cursor.lastrowid
            cursor.close()

        return record_id

    def add_user_link(self, link):
        with sqlite3.connect('db.sqlite') as sc:
            cursor = sc.cursor()
            query = f"""SELECT rowid
            FROM links 
            WHERE link='{link}'"""
            cursor.execute(query)
            record = cursor.fetchone()
            cursor.close()

            if record is not None:
                return record[0]

            cursor = sc.cursor()
            query = f"""INSERT INTO links 
            (link) VALUES ('{link}')"""
            cursor.execute(query)
            record_id = cursor.lastrowid
            cursor.close()

        return record_id

    def get_user_chats(self, user_id):
        with sqlite3.connect('db.sqlite') as sc:
            cursor = sc.cursor()
            query = f"SELECT * FROM accesses WHERE user_id='{user_id}'"
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()

            if len(records) <= 0:
                return {}

            data = []
            for user_id, chat_id, chat_name in records:
                data.append(
                    {
                        "chat_id": chat_id,
                        "chat_name": chat_name
                    }
                )

        return data

    def get_link(self, link_id):
        with sqlite3.connect('db.sqlite') as sc:
            cursor = sc.cursor()
            query = f"""SELECT rowid, *
            FROM links 
            WHERE rowid='{link_id}'"""
            cursor.execute(query)
            record = cursor.fetchone()
            cursor.close()

            if record is None:
                return False

        return record[1]

    def delete_chat(self, user_id, chat_id):
        with sqlite3.connect('db.sqlite') as sc:
            cursor = sc.cursor()
            query = f"""DELETE FROM accesses 
            WHERE user_id='{user_id}' and chat_id='{chat_id}'"""
            cursor.execute(query)
            cursor.close()

        return True
