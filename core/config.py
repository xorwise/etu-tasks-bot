import logging
import os


DATABASE_URL = 'mongodb://127.0.0.1:27017'
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

logging.basicConfig(level=logging.INFO)