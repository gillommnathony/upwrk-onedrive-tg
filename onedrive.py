import os
import json
import logging
from dotenv import load_dotenv
import requests
import msal


load_dotenv()

# Optional logging
# logging.basicConfig(level=logging.DEBUG)

config = {
    "client_id": os.environ.get('CLIENT_ID'),
    "authority": os.environ.get('AUTHORITY'),
    "secret": os.environ.get('SECRET'),
    "scope": ["https://graph.microsoft.com/.default"],
}

# Gets user ID
# url = "https://graph.microsoft.com/v1.0/users"
# Gets root children
# url = "https://graph.microsoft.com/v1.0/users/<user_id>/drive/root/children"


url = "https://graph.microsoft.com/v1.0/users/<user_id>/drive/items/<folder_id>/createLink"
# Create a preferably long-lived app instance which maintains a token cache.
app = msal.ConfidentialClientApplication(
    config["client_id"],
    authority=config["authority"],
    client_credential=config["secret"],
)

# The pattern to acquire a token looks like this.
result = None

result = app.acquire_token_silent(config["scope"], account=None)

if not result:
    logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
    result = app.acquire_token_for_client(scopes=config["scope"])

if "access_token" in result:
    # Calling graph using the access token
    # graph_data = requests.get(  # Use token to call downstream service
    #     url,
    #     # data=json.dumps({
    #     #     "type": "view",
    #     #     "scope": "anonymous"
    #     # }),
    #     headers={
    #         # "Content-Type": "application/json",
    #         'Authorization': 'Bearer ' + result['access_token']
    #     }
    # ).json()
    graph_data = requests.post(  # Use token to call downstream service
        url,
        data=json.dumps({
            "type": "view",
            "scope": "anonymous"
        }),
        headers={
            "Content-Type": "application/json",
            'Authorization': 'Bearer ' + result['access_token']
        }
    ).json()
    print("Graph API call result: ")
    print(json.dumps(graph_data, indent=2))
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug

