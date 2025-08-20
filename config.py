# config.py

import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_IDS = list(map(int, os.environ.get("6041675516", "").split(",")))
DB_URL = os.environ.get("DB_URL", "sqlite:///veo_bot.db")
PORT = int(os.environ.get("PORT", 5000))
