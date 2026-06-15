import psycopg2
import os
import datetime
import logging
from functools import wraps

from entity.Game import GameDTO
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

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


def log_db_errors(operation_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except psycopg2.Error as e:
                logger.error("DB error in %s: %s", operation_name, e, exc_info=True)
                raise
        return wrapper
    return decorator


def _DB_connection():
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
    except psycopg2.Error as e:
        logger.error("DB connection error: %s", e, exc_info=True)
        raise

@log_db_errors("save_base_game")
def save_base_game(user_id: int, game_name: str, game_status: int, date_added: datetime.date) -> int:
    connection = _DB_connection()
    with connection.cursor() as cursor:
        cursor.execute('''
            INSERT INTO games(
                user_id,
                game_name,
                game_status,
                date_added
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
        ''', (user_id, game_name, game_status, date_added))
        game_id = cursor.fetchone()[0]
    connection.commit()
    return game_id

@log_db_errors("add_external_id")
def add_external_id(game_id: int, external_id: int):
    connection = _DB_connection()
    with connection.cursor() as cursor:
        cursor.execute('''
            UPDATE games 
            SET external_game_id = %s
            WHERE id = %s
        ''', (external_id, game_id))
    connection.commit()
    connection.close()

@log_db_errors("change_status")
def change_status(game_id: int, status: int):
    connection = _DB_connection()
    with connection.cursor() as cursor:
        cursor.execute('''
            UPDATE games 
            SET game_status = %s
            WHERE id = %s
        ''', (status, game_id))
    connection.commit()
    connection.close()

@log_db_errors("change_user_rating")
def change_user_rating(game_id: int, user_rating: int):
    connection = _DB_connection()
    with connection.cursor() as cursor:
        cursor.execute('''
            UPDATE games 
            SET user_rating = %s
            WHERE id = %s
        ''', (user_rating, game_id))
    connection.commit()
    connection.close()

@log_db_errors("edit_note")
def edit_note(game_id: int, note: str):
    connection = _DB_connection()
    with connection.cursor() as cursor:
        cursor.execute('''
            UPDATE games 
            SET note = %s
            WHERE id = %s
        ''',(note, game_id))
    connection.commit()
    connection.close()

@log_db_errors("change_completion_date")
def change_completion_date (game_id: int, completion_date: datetime.date):
    connection = _DB_connection()
    with connection.cursor() as cursor:
        cursor.execute('''
            UPDATE games 
            SET completion_date = %s
            WHERE id = %s
        ''', (completion_date, game_id))
    connection.commit()
    connection.close()

@log_db_errors("clear_completion_date")
def clear_completion_date(game_id: int) -> None:
    connection = _DB_connection()
    with connection.cursor() as cursor:
        cursor.execute('''
            UPDATE games
            SET completion_date = NULL
            WHERE id = %s
        ''', (game_id,))
    connection.commit()
    connection.close()

@log_db_errors("get_completed_games_for_period")
def get_completed_games_for_period(
    user_id: int,
    date_from: datetime.date | None = None,
    date_to: datetime.date | None = None,
) -> list[GameDTO]:
    connection = _DB_connection()
    result = []
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT *
            FROM games
            WHERE user_id = %s
              AND game_status = 1
              AND (%s IS NULL OR completion_date >= %s)
              AND (%s IS NULL OR completion_date <= %s)
            ORDER BY completion_date DESC
        ''', (user_id, date_from, date_from, date_to, date_to))
        data = cursor.fetchall()
        if data:
            for row in data:
                result.append(GameDTO(*row))
    connection.close()
    return result

_SORT_COLUMNS = {
    "date_added": "date_added DESC",
    "name": "game_name ASC",
    "rating": "user_rating DESC NULLS LAST",
    "status": "game_status ASC",
}

@log_db_errors("get_user_games")
def get_user_games(user_id: int, page: int, filter_status: int | None = None, sort_by: str = "date_added") -> list[GameDTO]:
    connection = _DB_connection()
    result = []
    order_by = _SORT_COLUMNS.get(sort_by, _SORT_COLUMNS["date_added"])
    with connection.cursor() as cursor:
        if filter_status is None:
            cursor.execute(
                f'''
                SELECT *
                FROM games
                WHERE user_id = %s
                ORDER BY {order_by}
                LIMIT 5
                OFFSET %s
                ''',
                (user_id, (page - 1) * 5))
        else:
            cursor.execute(
                f'''
                SELECT *
                FROM games
                WHERE user_id = %s AND game_status = %s
                ORDER BY {order_by}
                LIMIT 5
                OFFSET %s
                ''',
                (user_id, filter_status, (page - 1) * 5))

        data = cursor.fetchall()

        if data is None:
            return []

        for row in data:
            game = GameDTO(*row)
            result.append(game)
    connection.close()
    return result

@log_db_errors("get_game")
def get_game(game_id: int) -> GameDTO | None:
    connection = _DB_connection()
    game = None
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT * 
            FROM games 
            WHERE id = %s
        ''', (game_id,))
        data = cursor.fetchone()
        if data is None:
            return None
        game = GameDTO(*data)
    connection.close()
    return game

@log_db_errors("get_user_games_count")
def get_user_games_count(user_id: int, filter_status: int | None = None) -> int:
    with _DB_connection() as connection:
        with connection.cursor() as cursor:
            if filter_status is None:
                cursor.execute('''
                    SELECT COUNT(*)
                    FROM games
                    WHERE user_id = %s
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT COUNT(*)
                    FROM games
                    WHERE user_id = %s AND game_status = %s
                ''', (user_id, filter_status))
            data = cursor.fetchone()
            if data is None:
                return 0
            result = data[0]
    return result

@log_db_errors("delete_game")
def delete_game(game_id: int) -> None:
    connection = _DB_connection()
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM games WHERE id = %s', (game_id,))
    connection.commit()
    connection.close()