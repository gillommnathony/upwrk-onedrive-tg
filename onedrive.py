import os
import logging
import requests
import msal
import ntpath


class OneDrive:
    def __init__(self):
        self.client_id = os.environ.get('CLIENT_ID')
        self.authority = os.environ.get('AUTHORITY')
        self.secret = os.environ.get('SECRET')
        self.scope = ["https://graph.microsoft.com/.default"]
        self.access_token = False

    def auth(self):
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
        else:
            print(result.get("error"))
            print(result.get("error_description"))
            print(result.get("correlation_id"))

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

    def upload_file(self, user_id, folder_id, fp):
        self.auth()

        file_name = ntpath.basename(fp)
        file_size = os.stat(fp).st_size
        file_data = open(fp, 'rb')

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
                }).json()

            with open(fp, 'rb') as f:
                total_size = os.path.getsize(fp)
                chunk_size = 4100000
                chunk_num = total_size // chunk_size
                chunk_leftover = total_size - chunk_size * chunk_num
                i = 0
                while True:
                    chunk_data = f.read(chunk_size)
                    start_index = i * chunk_size
                    end_index = start_index + chunk_size
                    # If end of file, break
                    if not chunk_data:
                        break
                    if i == chunk_num:
                        end_index = start_index + chunk_leftover
                    # Setting the header with the appropriate
                    # chunk data location in the file
                    headers = {
                        "Content-Length": str(chunk_size),
                        "Content-Range":
                            f"bytes {start_index}-{end_index-1}/{total_size}",
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.access_token}"
                    }
                    # Upload one chunk at a time
                    chunk_res = requests.put(
                        res['uploadUrl'], data=chunk_data,
                        headers=headers)
                    print(chunk_res.json())
                    i = i + 1

        file_data.close()

        return res
