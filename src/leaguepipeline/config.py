import os
from dotenv import load_dotenv

load_dotenv()

RIOT_API_KEY = os.environ["RIOT_API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]