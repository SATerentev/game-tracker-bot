import time
from pathlib import Path
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

MEASURES_FILE = Path(__file__).parent.parent / "Замеры.txt"

# Понятные названия для кнопок в замерах
CALLBACK_LABELS = {
    "gamelist_page_": "переключение страницы списка",
    "gamelist_filter": "открытие фильтра",
    "gamelist_sort": "открытие сортировки",
    "filter_": "применение фильтра",
    "sort_": "применение сортировки",
    "gameinfo_": "просмотр игры",
    "change_status_": "изменение статуса (начало)",
    "editgame_status_": "сохранение статуса",
    "change_rating_": "изменение оценки (начало)",
    "editgame_rating_": "сохранение оценки",
    "change_completion_": "изменение даты прохождения",
    "change_note_": "изменение комментария",
    "delete_game_": "удаление игры (начало)",
    "confirm_delete_": "подтверждение удаления",
    "cancel_delete_": "отмена удаления",
    "addgame_rawg_": "выбор игры из RAWG",
    "addgame_not_in_list": "игра не найдена в RAWG",
    "addgame_status_": "выбор статуса при добавлении",
    "addgame_rating_": "выбор оценки при добавлении",
    "addgame_skip_comment": "пропуск комментария",
    "report_last_12_months": "отчёт за 12 месяцев",
    "report_current_year": "отчёт за текущий год",
    "report_all_time": "отчёт за всё время",
}

MESSAGE_LABELS = {
    "Посмотреть список игр": "просмотр списка игр",
    "Добавить новую игру": "добавление игры (начало)",
    "Сформировать отчёт": "формирование отчёта (начало)",
    "/start": "регистрация / главное меню",
}


def _describe_callback(data: str) -> str:
    if data in CALLBACK_LABELS:
        return CALLBACK_LABELS[data]
    for prefix, label in CALLBACK_LABELS.items():
        if data.startswith(prefix):
            return f"{label} ({data})"
    return data


def _get_handler_name(data: dict[str, Any]) -> str:
    handler_obj = data.get("handler")
    if handler_obj and hasattr(handler_obj, "callback"):
        return handler_obj.callback.__name__
    return "unknown"


def _get_action_description(event: TelegramObject) -> str:
    if isinstance(event, CallbackQuery) and event.data:
        return _describe_callback(event.data)
    if isinstance(event, Message) and event.text:
        return MESSAGE_LABELS.get(event.text.strip(), event.text.strip())
    return ""


class TimingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        start = time.perf_counter()
        result = await handler(event, data)
        elapsed = time.perf_counter() - start

        func_name = _get_handler_name(data)
        action = _get_action_description(event)

        with open(MEASURES_FILE, "a", encoding="utf-8") as file:
            if action:
                file.write(f"{func_name} — {action}: {elapsed:.3f}s\n")
            else:
                file.write(f"{func_name}: {elapsed:.3f}s\n")

        return result
