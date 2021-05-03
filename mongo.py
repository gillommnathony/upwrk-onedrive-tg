import os
import pymongo
from bson.objectid import ObjectId


class Mongo:
    def __init__(self):
        self.client = pymongo.MongoClient(os.environ.get("MONGO_DB"))
        self.db = self.client.main

    def add_user_chat(self, user_id, chat_id, chat_name):
        accesses = self.db.accesses
        access = {
            "user_id": user_id,
            "chat_id": chat_id,
            "chat_name": chat_name
        }
        access_id = accesses.insert_one(access).inserted_id

        return access_id

    def get_user_chats(self, user_id):
        accesses = self.db.accesses
        chats = accesses.find({"user_id": user_id})

        data = []
        for chat in chats:
            data.append(
                {
                    "chat_id": chat['chat_id'],
                    "chat_name": chat['chat_name']
                }
            )

        return data

    def delete_chat(self, user_id, chat_id):
        accesses = self.db.accesses
        accesses.delete_many({
            "user_id": user_id,
            "chat_id": chat_id
        })

        return True

    def add_user_link(self, link):
        links = self.db.links
        link = {
            "link": link
        }
        link_id = links.insert_one(link).inserted_id

        return link_id

    def get_link(self, link_id):
        links = self.db.links
        link_res = links.find_one({"_id": ObjectId(link_id)})
        link = link_res['link']

        return link
