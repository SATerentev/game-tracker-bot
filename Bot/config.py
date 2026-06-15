import os
from pathlib import Path
from dotenv import load_dotenv

# \/ при запуске в докере, закомментировать \/
root_dir = Path(__file__).parent.parent
dotenv_path = root_dir / '.env'
load_dotenv(dotenv_path)
# /\ при запуске в докере, закомменитровать /\

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
API_KEY = os.getenv("RAWG_API_KEY")
BOT_TOKEN = os.getenv('BOT_TOKEN')