from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from entity.Game import GameDTO

SORT_DESCRIPTIONS = (
    "Выберите критерий сортировки:\n\n"
    "• По дате добавления — сначала недавно добавленные игры\n"
    "• По названию — в алфавитном порядке (А → Я)\n"
    "• По оценке — сначала игры с высокой оценкой\n"
    "• По статусу — сначала «Пройдена», затем «В процессе», «Планируется», «Брошена»"
)

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    keyboard = [
        [KeyboardButton(text="Посмотреть список игр")],
        [KeyboardButton(text="Добавить новую игру")],
        [KeyboardButton(text="Сформировать отчёт")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_game_list_keyboard(games: list[GameDTO], page: int, has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    buttons = []
    for game in games:
        buttons.append([InlineKeyboardButton(text=game.name, callback_data=f"gameinfo_{game.id}")])

    nav_buttons = []
    if has_prev:
        nav_buttons.append(InlineKeyboardButton(text="<=", callback_data=f"gamelist_page_{page - 1}"))
    if has_next:
        nav_buttons.append(InlineKeyboardButton(text="=>", callback_data=f"gamelist_page_{page + 1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton(text="Фильтр", callback_data="gamelist_filter")])
    buttons.append([InlineKeyboardButton(text="Сортировка", callback_data="gamelist_sort")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_filter_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Все игры", callback_data="filter_all")],
        [InlineKeyboardButton(text="Пройдена", callback_data="filter_status_1")],
        [InlineKeyboardButton(text="В процессе", callback_data="filter_status_2")],
        [InlineKeyboardButton(text="Планируется", callback_data="filter_status_3")],
        [InlineKeyboardButton(text="Брошена", callback_data="filter_status_4")],
    ])

def get_sort_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="По дате добавления (сначала новые)", callback_data="sort_date_added")],
        [InlineKeyboardButton(text="По названию (А → Я)", callback_data="sort_name")],
        [InlineKeyboardButton(text="По оценке (сначала высокие)", callback_data="sort_rating")],
        [InlineKeyboardButton(text="По статусу (Пройдена → Брошена)", callback_data="sort_status")],
    ])

def get_game_info_keyboard(game_id: int, status: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Изменить статус", callback_data=f"change_status_{game_id}")],
        [InlineKeyboardButton(text="Изменить оценку", callback_data=f"change_rating_{game_id}")],
    ]
    if status == 1 or status == 4:
        buttons.append([InlineKeyboardButton(
            text="Изменить дату прохождения",
            callback_data=f"change_completion_{game_id}"
        )])
    buttons.append([InlineKeyboardButton(text="Изменить комментарий", callback_data=f"change_note_{game_id}")])
    buttons.append([InlineKeyboardButton(text="Удалить игру", callback_data=f"delete_game_{game_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_edit_status_keyboard(game_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пройдена", callback_data=f"editgame_status_{game_id}_1")],
        [InlineKeyboardButton(text="В процессе", callback_data=f"editgame_status_{game_id}_2")],
        [InlineKeyboardButton(text="Планируется", callback_data=f"editgame_status_{game_id}_3")],
        [InlineKeyboardButton(text="Брошена", callback_data=f"editgame_status_{game_id}_4")],
    ])

def get_rawg_search_keyboard(games: list) -> InlineKeyboardMarkup:
    buttons = []
    for index, game in enumerate(games):
        buttons.append([InlineKeyboardButton(
            text=game.name,
            callback_data=f"addgame_rawg_{index}"
        )])
    buttons.append([InlineKeyboardButton(
        text="Игры нет в списке",
        callback_data="addgame_not_in_list"
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_status_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пройдена", callback_data="addgame_status_1")],
        [InlineKeyboardButton(text="В процессе", callback_data="addgame_status_2")],
        [InlineKeyboardButton(text="Планируется", callback_data="addgame_status_3")],
        [InlineKeyboardButton(text="Брошена", callback_data="addgame_status_4")],
    ])

def get_edit_rating_keyboard(game_id: int) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for rating in range(1, 11):
        row.append(InlineKeyboardButton(
            text=str(rating),
            callback_data=f"editgame_rating_{game_id}_{rating}"
        ))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_rating_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for rating in range(1, 11):
        row.append(InlineKeyboardButton(text=str(rating), callback_data=f"addgame_rating_{rating}"))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_skip_comment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Не сейчас", callback_data="addgame_skip_comment")]
    ])

def get_delete_confirmation_keyboard(game_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, удалить игру", callback_data=f"confirm_delete_{game_id}")],
        [InlineKeyboardButton(text="Нет, оставить игру", callback_data=f"cancel_delete_{game_id}")],
    ])

def get_report_period_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отчёт за последние 12 месяцев", callback_data="report_last_12_months")],
        [InlineKeyboardButton(text="Отчёт за текущий год", callback_data="report_current_year")],
        [InlineKeyboardButton(text="Отчёт за всё время", callback_data="report_all_time")],
    ])
