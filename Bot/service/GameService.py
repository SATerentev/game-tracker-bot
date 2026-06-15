import datetime

from entity.Game import GameDTO
from entity.Result import Result
from infrastructure import GameRepository, API_gateway_RAWG

# TODO все магические числа в константы закинуть

def get_user_games(
    user_id: int,
    page: int,
    filter_status: int | None = None,
    sort_by: str = "date_added",
) -> list[GameDTO]:
    if user_id is None or user_id < 1:
        raise Exception("Invalid user_id")
    return GameRepository.get_user_games(user_id, page, filter_status, sort_by)

def get_user_games_count(user_id: int, filter_status: int | None = None) -> int:
    if user_id is None or user_id < 1:
        raise Exception("Invalid user_id")
    return GameRepository.get_user_games_count(user_id, filter_status)

def validate_rating(rating_str: str) -> Result:
    if rating_str is None or not rating_str.isdigit():
        return Result(None, False, "Оценка должна быть числом от 1 до 10")
    rating = int(rating_str)
    if rating < 1 or rating > 10:
        return Result(None, False, "Оценка должна быть числом от 1 до 10")
    return Result(rating, True, "")

def delete_game(game_id: int) -> Result:
    if game_id is None or game_id < 1:
        raise Exception("Invalid game_id")
    GameRepository.delete_game(game_id)
    return Result(None, True, "")

def get_game(game_id: int) -> Result:
    if game_id is None or game_id < 1: raise Exception("Invalid game_id")
    game = GameRepository.get_game(game_id)
    if game is None:
        return Result(None, False, "Game not found")
    else:
        return Result(game, True, "")

def add_game(user_id: int, game_name: str, game_status: int) -> Result:
    if user_id is None or user_id < 1: raise Exception("Invalid user_id")
    if game_name is None or game_name == "": return Result(None, False, "Invalid name")
    if game_status is None or game_status < 1 or game_status > 4: return Result(None, False, "Invalid status")
    date_added = datetime.date.today()
    return Result(GameRepository.save_base_game(user_id, game_name, game_status, date_added), True, "")

async def search_game_rawg(game_name: str) -> Result:
    if game_name is None or game_name == "":
        return Result(None, False, "Invalid game_name")
    return await API_gateway_RAWG.search_game(game_name)

def validate_completion_date(date_str: str) -> Result:
    if date_str is None or date_str.count(".") != 2:
        return Result(None, False, "Дата должна быть в формате YYYY.MM.DD")
    parts = date_str.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        return Result(None, False, "Дата должна быть в формате YYYY.MM.DD")
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])
    try:
        date = datetime.date(year, month, day)
    except ValueError:
        return Result(None, False, "Некорректная дата. Введите дату в формате YYYY.MM.DD")
    if date > datetime.date.today():
        return Result(None, False, "Дата прохождения не может быть позже сегодняшней")
    return Result(date, True, "")

def finish_add_game(
    user_id: int,
    game_name: str,
    status: int,
    rawg_id: int | None = None,
    rating: int | None = None,
    completion_date: datetime.date | None = None,
    note: str | None = None,
) -> Result:
    if user_id is None or user_id < 1:
        raise Exception("Invalid user_id")
    if game_name is None or game_name == "":
        return Result(None, False, "Invalid name")
    if status is None or status < 1 or status > 4:
        return Result(None, False, "Invalid status")

    date_added = datetime.date.today()
    game_id = GameRepository.save_base_game(user_id, game_name, status, date_added)

    if rawg_id is not None:
        GameRepository.add_external_id(game_id, rawg_id)
    if rating is not None:
        GameRepository.change_user_rating(game_id, rating)
    if completion_date is not None:
        GameRepository.change_completion_date(game_id, completion_date)
    if note is not None and note != "":
        GameRepository.edit_note(game_id, note)

    game = GameRepository.get_game(game_id)
    return Result(game, True, "")

def add_external_id(game_id: int, external_id: int) -> Result:
    if game_id is None or game_id < 1: raise Exception("Invalid game_id")
    if external_id is None or external_id < 0: return Result(None, False, "Invalid RAWG id")
    GameRepository.add_external_id(game_id, external_id)
    return Result(None, True, "")

def change_rating(game_id: int, user_rating: int) -> Result:
    if game_id is None or game_id < 1: raise Exception("Invalid game_id")
    if user_rating is None or user_rating > 10 or user_rating < 1: return Result(None, False, "Invalid user rating")
    GameRepository.change_user_rating(game_id, user_rating)
    return Result(None, True, "")

def edit_note(game_id: int, note: str) -> Result:
    if game_id is None or game_id < 1: raise Exception("Invalid game_id")
    if note is None or note == "": return Result(None, False, "Invalid note")
    GameRepository.edit_note(game_id, note)
    return Result(None, True, "")

def change_completion_date(game_id: int, completion_date: datetime.date) -> Result:
    if game_id is None or game_id < 1:
        raise Exception("Invalid game_id")
    if completion_date is None:
        return Result(None, False, "Invalid completion date")
    if completion_date > datetime.date.today():
        return Result(None, False, "Дата прохождения не может быть позже сегодняшней")
    GameRepository.change_completion_date(game_id, completion_date)
    return Result(None, True, "")

def change_status(game_id: int, status: int) -> Result:
    if game_id is None or game_id < 1:
        raise Exception("Invalid game_id")
    if status is None or status < 1 or status > 4:
        return Result(None, False, "Invalid status")

    game = GameRepository.get_game(game_id)
    if game is None:
        return Result(None, False, "Game not found")
    if game.status == status:
        return Result(None, False, "Такой статус уже выбран")

    GameRepository.change_status(game_id, status)

    if status in (1, 4):
        GameRepository.change_completion_date(game_id, datetime.date.today())
    elif status in (2, 3):
        GameRepository.clear_completion_date(game_id)

    return Result(None, True, "")

def change_status_with_rating(game_id: int, status: int, rating: int) -> Result:
    if game_id is None or game_id < 1:
        raise Exception("Invalid game_id")
    if status is None or status < 1 or status > 4:
        return Result(None, False, "Invalid status")
    if rating is None or rating < 1 or rating > 10:
        return Result(None, False, "Invalid user rating")

    game = GameRepository.get_game(game_id)
    if game is None:
        return Result(None, False, "Game not found")
    if game.status == status:
        return Result(None, False, "Такой статус уже выбран")

    GameRepository.change_status(game_id, status)
    GameRepository.change_user_rating(game_id, rating)

    if status in (1, 4):
        GameRepository.change_completion_date(game_id, datetime.date.today())
    elif status in (2, 3):
        GameRepository.clear_completion_date(game_id)

    return Result(None, True, "")