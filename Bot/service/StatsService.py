import datetime

from entity.Result import Result
from infrastructure import UserRepository, GameRepository

PERIOD_LAST_12_MONTHS = "last_12_months"
PERIOD_CURRENT_YEAR = "current_year"
PERIOD_ALL_TIME = "all_time"


def _build_report(user, games: list, period_title: str) -> Result:
    header = f"Пользователь {user.telegram_username}.\nСтатистика за {period_title}.\n"

    if not games:
        return Result(header + "Пройдено 0 игр", True, "")

    lines = []
    for game in games:
        if game.rating:
            lines.append(f"Игра {game.name} | Оценка {game.rating}\n")
        else:
            lines.append(f"Игра {game.name} | Оценка не поставлена\n")

    text = header + f"Пройдено игр: {len(lines)}.\n\n" + "".join(lines)
    return Result(text, True, "")


def get_user_stats(user_id: int, period: str) -> Result:
    user = UserRepository.get_user(user_id)
    if not user:
        return Result("", False, "User not found")

    today = datetime.date.today()

    if period == PERIOD_LAST_12_MONTHS:
        date_from = today - datetime.timedelta(days=365)
        date_to = today
        period_title = "последние 12 месяцев"
    elif period == PERIOD_CURRENT_YEAR:
        date_from = datetime.date(today.year, 1, 1)
        date_to = today
        period_title = f"текущий год ({today.year})"
    elif period == PERIOD_ALL_TIME:
        date_from = None
        date_to = None
        period_title = "всё время"
    else:
        return Result("", False, "Unknown period")

    games = GameRepository.get_completed_games_for_period(user_id, date_from, date_to)
    return _build_report(user, games, period_title)


def get_user_stats_for_last_year(user_id: int) -> Result:
    return get_user_stats(user_id, PERIOD_LAST_12_MONTHS)
