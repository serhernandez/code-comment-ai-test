from dotenv import load_dotenv
from os import getenv
from secrets import token_hex

load_dotenv()

class Config:
    OPENAI_API_KEY = getenv("OPENAI_API_KEY", "")
    SECRET_KEY = token_hex(16)