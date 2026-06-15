import psycopg2
import os
import datetime

from entity.User import UserDTO
from pathlib import Path
from dotenv import load_dotenv
from entity.Result import Result

# \/ при запуске в докере, закомментировать \/
root_dir = Path(__file__).parent.parent.parent
dotenv_path = root_dir / '.env'
load_dotenv(dotenv_path)
# /\ при запуске в докере, закомменитровать /\

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')

def DB_connection():
    return psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    dbname=DB_NAME
)

def get_all_users() -> list[UserDTO]:
    result = []
    with DB_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('''
            SELECT * 
            FROM users
            ''')
            data = cursor.fetchall()

            if data is None:
                return []

            for row in data:
                user = UserDTO(*row)
                result.append(user)
    return result

def get_user(user_id: int) -> UserDTO | None:
    with DB_connection() as connection:
        result = None
        with connection.cursor() as cursor:
            cursor.execute('''
            SELECT * 
            FROM users 
            WHERE id=%s
            ''', (user_id,))
            data = cursor.fetchone()
            if data is None:
                return None
            result = UserDTO(*data)
    return result

def get_user_id_by_telegram_id(telegram_id: int) -> int | None:
    with DB_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('''
            SELECT id 
            FROM users 
            WHERE telegram_id=%s
            ''', (telegram_id,))
            data = cursor.fetchone()
            if data is None:
                return None
            result = data[0]
    return result

def save_user(username: str, telegram_id: int, registration_date: datetime.date, last_active_date: datetime.date):
    with DB_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO users (
                    username,
                    telegram_id,
                    register_date,
                    last_active
                )
                VALUES (%s, %s, %s, %s)
            ''', (username, telegram_id, registration_date, last_active_date))
        connection.commit()

def is_username_exists(username: str) -> bool:
    with DB_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT COUNT(*) 
                FROM users 
                WHERE username = %s
            ''', (username,))
            data = cursor.fetchone()
            if data is None:
                return False
            count = data[0]
    return count > 0