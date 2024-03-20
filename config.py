from dotenv import load_dotenv
from os import getenv
from secrets import token_hex

load_dotenv()

class Config:
    OPENAI_API_KEY = getenv("OPENAI_API_KEY", "")
    OPENAI_MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
    SECRET_KEY = token_hex(16)