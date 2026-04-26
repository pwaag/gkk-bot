import requests
import os

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

data = {
    "content": "Dags att städa!",
    "username": "Städis",  # override webhook name
    "avatar_url": "https://raw.githubusercontent.com/pwaag/gkk-bot/main/avatar.png"  # optional
}

response = requests.post(WEBHOOK_URL, json=data)

if response.status_code != 204:
    raise Exception(f"Request failed: {response.status_code}, {response.text}")
