import requests
import os

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

data = {
    "content": "👋 Hello! This is your biweekly automated message.",
    "username": "My Custom Bot",  # override webhook name
    # "avatar_url": "https://example.com/avatar.png"  # optional
}

response = requests.post(WEBHOOK_URL, json=data)

if response.status_code != 204:
    raise Exception(f"Request failed: {response.status_code}, {response.text}")
