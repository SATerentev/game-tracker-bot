# Состояние процесса ввода username пользователем, если у него отсутствует username в Telegram
STATE_WAITING_USERNAME = "waiting_username"

# Состояния процесса добавления игры
STATE_WAITING_NAME = "waiting_name"
STATE_WAITING_RAWG_SELECTION = "waiting_rawg_selection"
STATE_WAITING_STATUS = "waiting_status"
STATE_WAITING_RATING = "waiting_rating"
STATE_WAITING_COMPLETION_DATE = "waiting_completion_date"
STATE_WAITING_COMMENT = "waiting_comment"

# Состояния редактирования игры
STATE_EDIT_WAITING_STATUS = "edit_waiting_status"
STATE_EDIT_WAITING_RATING = "edit_waiting_rating"
STATE_EDIT_WAITING_NOTE = "edit_waiting_note"
STATE_EDIT_WAITING_COMPLETION_DATE = "edit_waiting_completion_date"
STATE_EDIT_WAITING_RATING_FOR_STATUS = "edit_waiting_rating_for_status"

SORT_DATE_ADDED = "date_added"
SORT_NAME = "name"
SORT_RATING = "rating"
SORT_STATUS = "status"

_user_states: dict[int, dict] = {}
_edit_states: dict[int, dict] = {}
_list_settings: dict[int, dict] = {}


# --- Ввод username пользователем, если у него отсутствует username в Telegram ---
def start_username_input(telegram_id: int) -> None:
    _user_states[telegram_id] = {"state": STATE_WAITING_USERNAME, "username": None}

# --- Добавление игры ---

def start_add_game(telegram_id: int, user_id: int) -> None:
    _user_states[telegram_id] = {
        "state": STATE_WAITING_NAME,
        "user_id": user_id,
        "game_name": None,
        "rawg_games": None,
        "rawg_id": None,
        "final_name": None,
        "status": None,
        "rating": None,
        "completion_date": None,
    }


def get_state(telegram_id: int) -> str | None:
    data = _user_states.get(telegram_id)
    if data is None:
        return None
    return data["state"]


def get_data(telegram_id: int) -> dict | None:
    return _user_states.get(telegram_id)


def save_game_name(telegram_id: int, game_name: str, rawg_games: list) -> None:
    _user_states[telegram_id]["game_name"] = game_name
    _user_states[telegram_id]["rawg_games"] = rawg_games
    _user_states[telegram_id]["state"] = STATE_WAITING_RAWG_SELECTION


def save_rawg_selection(telegram_id: int, final_name: str, rawg_id: int) -> None:
    _user_states[telegram_id]["final_name"] = final_name
    _user_states[telegram_id]["rawg_id"] = rawg_id
    _user_states[telegram_id]["state"] = STATE_WAITING_STATUS


def save_manual_name(telegram_id: int) -> None:
    data = _user_states[telegram_id]
    data["final_name"] = data["game_name"]
    data["rawg_id"] = None
    data["state"] = STATE_WAITING_STATUS


def save_status(telegram_id: int, status: int) -> None:
    _user_states[telegram_id]["status"] = status


def save_rating(telegram_id: int, rating: int) -> None:
    _user_states[telegram_id]["rating"] = rating
    _user_states[telegram_id]["state"] = STATE_WAITING_COMPLETION_DATE


def save_completion_date(telegram_id: int, completion_date) -> None:
    _user_states[telegram_id]["completion_date"] = completion_date
    _user_states[telegram_id]["state"] = STATE_WAITING_COMMENT


def go_to_comment(telegram_id: int) -> None:
    _user_states[telegram_id]["state"] = STATE_WAITING_COMMENT


def go_to_rating(telegram_id: int) -> None:
    _user_states[telegram_id]["state"] = STATE_WAITING_RATING


def clear_state(telegram_id: int) -> None:
    _user_states.pop(telegram_id, None)


def is_adding_game(telegram_id: int) -> bool:
    return telegram_id in _user_states


# --- Список игр (фильтр и сортировка) ---

def reset_list_settings(telegram_id: int) -> None:
    _list_settings[telegram_id] = {
        "filter_status": None,
        "sort_by": SORT_DATE_ADDED,
        "page": 1,
    }


def get_list_settings(telegram_id: int) -> dict:
    if telegram_id not in _list_settings:
        reset_list_settings(telegram_id)
    return _list_settings[telegram_id]


def set_list_page(telegram_id: int, page: int) -> None:
    get_list_settings(telegram_id)["page"] = page


def set_filter_status(telegram_id: int, filter_status: int | None) -> None:
    settings = get_list_settings(telegram_id)
    settings["filter_status"] = filter_status
    settings["page"] = 1


def set_sort_by(telegram_id: int, sort_by: str) -> None:
    settings = get_list_settings(telegram_id)
    settings["sort_by"] = sort_by
    settings["page"] = 1


# --- Редактирование игры ---

def start_edit_status(telegram_id: int, game_id: int) -> None:
    _edit_states[telegram_id] = {"state": STATE_EDIT_WAITING_STATUS, "game_id": game_id}


def start_edit_status_rating(telegram_id: int, game_id: int, pending_status: int) -> None:
    _edit_states[telegram_id] = {
        "state": STATE_EDIT_WAITING_RATING_FOR_STATUS,
        "game_id": game_id,
        "pending_status": pending_status,
    }


def get_pending_status(telegram_id: int) -> int | None:
    data = _edit_states.get(telegram_id)
    if data is None:
        return None
    return data.get("pending_status")


def start_edit_rating(telegram_id: int, game_id: int) -> None:
    _edit_states[telegram_id] = {"state": STATE_EDIT_WAITING_RATING, "game_id": game_id}


def start_edit_note(telegram_id: int, game_id: int) -> None:
    _edit_states[telegram_id] = {"state": STATE_EDIT_WAITING_NOTE, "game_id": game_id}


def start_edit_completion_date(telegram_id: int, game_id: int) -> None:
    _edit_states[telegram_id] = {"state": STATE_EDIT_WAITING_COMPLETION_DATE, "game_id": game_id}


def get_edit_state(telegram_id: int) -> str | None:
    data = _edit_states.get(telegram_id)
    if data is None:
        return None
    return data["state"]


def get_edit_game_id(telegram_id: int) -> int | None:
    data = _edit_states.get(telegram_id)
    if data is None:
        return None
    return data["game_id"]


def clear_edit_state(telegram_id: int) -> None:
    _edit_states.pop(telegram_id, None)
