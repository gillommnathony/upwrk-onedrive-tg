import os
import sys
import json
import logging
import requests
import msal
import ntpath

logger = logging.getLogger(__name__)


class OneDrive:
    def __init__(self):
        self.client_id = os.environ.get('CLIENT_ID')
        self.authority = os.environ.get('AUTHORITY')
        self.secret = os.environ.get('SECRET')
        self.scope = ["https://graph.microsoft.com/.default"]
        self.access_token = False

    def auth(self):
        logger.info("Authentication.")
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.secret,
        )
        result = None
        result = app.acquire_token_silent(self.scope, account=None)
        if not result:
            logging.info("No token in cache. Let's get a new one from AAD.")
            result = app.acquire_token_for_client(scopes=self.scope)

        if "access_token" in result:
            self.access_token = result['access_token']
            logger.info("Access token granted.")
        else:
            logger.error(result.get("error"))
            logger.error(result.get("error_description"))
            logger.error(result.get("correlation_id"))

    def get_users(self):
        self.auth()

        url = "https://graph.microsoft.com/v1.0/users"

        res = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {self.access_token}"
            }
        ).json()

        return res

    def get_folders(self, user_id):
        self.auth()

        url = "https://graph.microsoft.com/v1.0/users/"
        url += f"{user_id}/drive/root/children"

        res = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {self.access_token}"
            }
        ).json()

        return res

    def get_folder_content(self, user_id, folder_id):
        self.auth()

        url = "https://graph.microsoft.com/v1.0/users/"
        url += f"{user_id}/drive/items/{folder_id}/children"

        res = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {self.access_token}"
            }
        ).json()

        return res

    def create_folder(self, user_id, folder_id, name):
        logger.info("Creating folder.")
        self.auth()

        url = "https://graph.microsoft.com/v1.0/users/"
        url += f"{user_id}/drive/items/{folder_id}/children"

        res = requests.post(
            url,
            data=json.dumps({
              "name": name,
              "folder": {},
              "@microsoft.graph.conflictBehavior": "rename"
            }),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
        ).json()

        data = False
        if "error" not in res:
            data = res['id']
            logger.info("Folder created successfully.")
        else:
            logger.error(res)

        return data

    def upload_file(self, user_id, folder_id, file_name, file_data):
        logger.info("Uploading.")
        self.auth()

        file_size = sys.getsizeof(file_data)

        if file_size < 4100000:
            # Perform is simple upload to the API
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}"
            url += f"/drive/items/{folder_id}:/{file_name}:/content"
            res = requests.put(
                url,
                data=file_data, headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.access_token}"
                }).json()
        else:
            # Creating an upload session
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}"
            url += f"/drive/items/{folder_id}:/{file_name}:/createUploadSession"
            res = requests.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.access_token}"
                }
            ).json()

            chunk_size = 4100000
            chunk_num = file_size // chunk_size
            chunk_leftover = file_size - chunk_size * chunk_num
            i = 0
            while True:
                start_index = i * chunk_size
                end_index = start_index + chunk_size - 1
                # If end of file, break
                if i == chunk_num:
                    end_index = start_index + chunk_leftover
                elif i > chunk_num:
                    break

                chunk_data = file_data[start_index:end_index]

                # Setting the header with the appropriate
                # chunk data location in the file
                headers = {
                    "Content-Length": str(chunk_size),
                    "Content-Range":
                        f"bytes {start_index}-{end_index-1}/{file_size}",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.access_token}"
                }
                # Upload one chunk at a time
                chunk_res = requests.put(
                    res['uploadUrl'], data=chunk_data,
                    headers=headers)
                logger.info(chunk_res.json())
                i = i + 1

        if "error" in res:
            logger.error(res)
        else:
            logger.info("Data sent successfully.")

        return res

    def create_link(self, user_id, folder_id):
        logger.info("Link creation.")
        self.auth()

        url = "https://graph.microsoft.com/v1.0/users/"
        url += f"{user_id}/drive/items/{folder_id}/createLink"

        res = requests.post(
            url,
            data=json.dumps({
                "type": "view",
                "scope": "anonymous"
            }),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }
        ).json()

        data = False
        if "error" not in res:
            data = res['link']['webUrl']
            logger.info("Link got successfully.")
        else:
            logger.error(res)

        return data
