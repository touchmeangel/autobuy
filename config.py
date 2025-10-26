import dotenv
import os

dotenv.load_dotenv()

api_id = os.getenv("TG_API_ID")
api_hash = os.getenv("TG_API_HASH")
logger_token = os.getenv("LOGGER_TOKEN")
logger_chat_id = os.getenv("LOGGER_CHAT_ID")