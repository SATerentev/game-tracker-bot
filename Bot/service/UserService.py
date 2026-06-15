import datetime
from entity.Result import Result
from infrastructure import UserRepository

def register_user(telegram_username: str, telegram_id: int) -> None:
    if UserRepository.get_user_id_by_telegram_id(telegram_id) is not None:
        return
    UserRepository.save_user(telegram_username, telegram_id, datetime.date.today(), datetime.date.today())

def check_username(telegram_id: int, username: str) -> Result:
    if not username or username == "" or len(username) > 32 or len(username) < 3:
        return Result(None, False, "Имя пользователя должно быть от 3 до 32 символов")
    if UserRepository.is_username_exists(username):
        return Result(None, False, "Такое имя пользователя уже существует")
    return Result(None, True, "")

def get_user_id_by_telegram_id(telegram_id: int) -> Result:
    user_id = UserRepository.get_user_id_by_telegram_id(telegram_id)
    if user_id is None:
        return Result(None, False, "User not found")
    else:
        return Result(user_id, True, "")