from aiogram import types, Router, F
from service import GameService, UserService, StateService
import keyboards

game_router = Router()

GAMES_PER_PAGE = 5


async def _show_game_list(target, user_id: int, telegram_id: int, page: int, edit: bool = False):
    settings = StateService.get_list_settings(telegram_id)
    StateService.set_list_page(telegram_id, page)

    filter_status = settings["filter_status"]
    sort_by = settings["sort_by"]

    games_count = GameService.get_user_games_count(user_id, filter_status)
    if games_count == 0:
        text = "У вас нет игр."
        if edit and hasattr(target, "edit_text"):
            await target.edit_text(text)
        else:
            await target.answer(text)
        return

    if page < 1:
        page = 1
        StateService.set_list_page(telegram_id, page)

    max_page = (games_count + GAMES_PER_PAGE - 1) // GAMES_PER_PAGE
    if page > max_page:
        page = max_page
        StateService.set_list_page(telegram_id, page)

    games = GameService.get_user_games(user_id, page, filter_status, sort_by)
    has_prev = page > 1
    has_next = page < max_page
    keyboard = keyboards.get_game_list_keyboard(games, page, has_prev, has_next)
    text = "Ваша библиотека:"

    if edit and hasattr(target, "edit_text"):
        await target.edit_text(text, reply_markup=keyboard)
    else:
        await target.answer(text, reply_markup=keyboard)


async def _show_game_info(
    target,
    game_id: int,
    edit: bool = False,
):
    game_result = GameService.get_game(game_id)
    if not game_result.result:
        text = "Игра не найдена"
        if edit and hasattr(target, "edit_text"):
            await target.edit_text(text)
        else:
            await target.answer(text)
        return

    game = game_result.value
    text = game.to_full_string()
    keyboard = keyboards.get_game_info_keyboard(game_id, game.status)

    if edit and hasattr(target, "edit_text"):
        await target.edit_text(text, reply_markup=keyboard)
    else:
        await target.answer(text, reply_markup=keyboard)


# --- Список игр ---

@game_router.message(F.text == "Посмотреть список игр")
async def gamelist(message: types.Message):
    user = UserService.get_user_id_by_telegram_id(message.from_user.id)
    if not user.result:
        await message.reply("Вы не зарегистрированы, введите /start для регистрации")
        return

    StateService.reset_list_settings(message.from_user.id)
    games_count = GameService.get_user_games_count(user.value)
    if games_count == 0:
        await message.reply("У вас нет игр.")
        return

    await _show_game_list(message, user.value, message.from_user.id, page=1)


@game_router.callback_query(F.data.startswith("gamelist_page_"))
async def gamelist_pagination(callback: types.CallbackQuery):
    user = UserService.get_user_id_by_telegram_id(callback.from_user.id)
    if not user.result:
        await callback.message.answer("Вы не зарегистрированы, введите /start для регистрации")
        await callback.answer()
        return

    page = int(callback.data.split("_")[2])
    settings = StateService.get_list_settings(callback.from_user.id)
    filter_status = settings["filter_status"]
    games_count = GameService.get_user_games_count(user.value, filter_status)
    max_page = max(1, (games_count + GAMES_PER_PAGE - 1) // GAMES_PER_PAGE)

    if page < 1 or page > max_page:
        await callback.answer()
        return

    await _show_game_list(callback.message, user.value, callback.from_user.id, page, edit=True)
    await callback.answer()


@game_router.callback_query(F.data == "gamelist_filter")
async def gamelist_filter(callback: types.CallbackQuery):
    keyboard = keyboards.get_filter_keyboard()
    await callback.message.edit_text("Выберите критерий фильтрации:", reply_markup=keyboard)
    await callback.answer()


@game_router.callback_query(F.data.startswith("filter_"))
async def apply_filter(callback: types.CallbackQuery):
    user = UserService.get_user_id_by_telegram_id(callback.from_user.id)
    if not user.result:
        await callback.message.answer("Вы не зарегистрированы, введите /start для регистрации")
        await callback.answer()
        return

    if callback.data == "filter_all":
        StateService.set_filter_status(callback.from_user.id, None)
    else:
        status = int(callback.data.split("_")[2])
        StateService.set_filter_status(callback.from_user.id, status)

    filter_status = StateService.get_list_settings(callback.from_user.id)["filter_status"]
    games_count = GameService.get_user_games_count(user.value, filter_status)
    if games_count == 0:
        await callback.message.edit_text("Игры по выбранному фильтру не найдены.")
        await callback.answer()
        return

    await _show_game_list(callback.message, user.value, callback.from_user.id, page=1, edit=True)
    await callback.answer()


@game_router.callback_query(F.data == "gamelist_sort")
async def gamelist_sort(callback: types.CallbackQuery):
    keyboard = keyboards.get_sort_keyboard()
    await callback.message.edit_text(keyboards.SORT_DESCRIPTIONS, reply_markup=keyboard)
    await callback.answer()


@game_router.callback_query(F.data.startswith("sort_"))
async def apply_sort(callback: types.CallbackQuery):
    user = UserService.get_user_id_by_telegram_id(callback.from_user.id)
    if not user.result:
        await callback.message.answer("Вы не зарегистрированы, введите /start для регистрации")
        await callback.answer()
        return

    sort_by = callback.data.split("_", 1)[1]
    StateService.set_sort_by(callback.from_user.id, sort_by)
    await _show_game_list(callback.message, user.value, callback.from_user.id, page=1, edit=True)
    await callback.answer()


# --- Просмотр игры (UC-6) ---

@game_router.callback_query(F.data.startswith("gameinfo_"))
async def gameinfo(callback: types.CallbackQuery):
    game_id = int(callback.data.split("_")[1])
    await _show_game_info(callback.message, game_id)
    await callback.answer()


# --- Редактирование игры (UC-7) ---

@game_router.callback_query(F.data.startswith("change_status_"))
async def change_status_start(callback: types.CallbackQuery):
    game_id = int(callback.data.split("_")[2])
    StateService.start_edit_status(callback.from_user.id, game_id)
    keyboard = keyboards.get_edit_status_keyboard(game_id)
    await callback.message.edit_text("Выберите новый статус игры:", reply_markup=keyboard)
    await callback.answer()


@game_router.callback_query(F.data.startswith("editgame_status_"))
async def change_status_save(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    game_id = int(parts[2])
    status = int(parts[3])

    if StateService.get_edit_state(callback.from_user.id) != StateService.STATE_EDIT_WAITING_STATUS:
        await callback.answer("Действие недоступно.")
        return

    game_result = GameService.get_game(game_id)
    if not game_result.result:
        await callback.message.edit_text("Игра не найдена")
        await callback.answer()
        return

    old_status = game_result.value.status

    if game_result.value.status == status:
        StateService.clear_edit_state(callback.from_user.id)
        await callback.answer("Такой статус уже выбран", show_alert=True)
        await _show_game_info(callback.message, game_id, edit=True)
        return

    if old_status in (2, 3) and status in (1, 4):
        StateService.start_edit_status_rating(callback.from_user.id, game_id, status)
        keyboard = keyboards.get_edit_rating_keyboard(game_id)
        await callback.message.edit_text("Выберите оценку игры:", reply_markup=keyboard)
        await callback.answer()
        return

    result = GameService.change_status(game_id, status)

    if not result.result:
        StateService.clear_edit_state(callback.from_user.id)
        if result.error_message == "Такой статус уже выбран":
            await callback.answer(result.error_message, show_alert=True)
            await _show_game_info(callback.message, game_id, edit=True)
        else:
            await callback.message.edit_text("Не удалось изменить статус: " + result.error_message)
        await callback.answer()
        return

    StateService.clear_edit_state(callback.from_user.id)
    await _show_game_info(callback.message, game_id, edit=True)
    await callback.answer()


@game_router.callback_query(F.data.startswith("change_rating_"))
async def change_rating_start(callback: types.CallbackQuery):
    game_id = int(callback.data.split("_")[2])
    keyboard = keyboards.get_edit_rating_keyboard(game_id)
    await callback.message.edit_text("Выберите новую оценку (от 1 до 10):", reply_markup=keyboard)
    await callback.answer()


@game_router.callback_query(F.data.startswith("editgame_rating_"))
async def change_rating_save(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    game_id = int(parts[2])
    rating = int(parts[3])

    edit_state = StateService.get_edit_state(callback.from_user.id)

    if edit_state == StateService.STATE_EDIT_WAITING_RATING_FOR_STATUS:
        if StateService.get_edit_game_id(callback.from_user.id) != game_id:
            await callback.answer("Действие недоступно.")
            return
        pending_status = StateService.get_pending_status(callback.from_user.id)
        result = GameService.change_status_with_rating(game_id, pending_status, rating)
        StateService.clear_edit_state(callback.from_user.id)
    else:
        result = GameService.change_rating(game_id, rating)

    if result.result:
        await _show_game_info(callback.message, game_id, edit=True)
    else:
        await callback.message.edit_text("Не удалось сохранить: " + result.error_message)
    await callback.answer()


@game_router.callback_query(F.data.startswith("change_completion_"))
async def change_completion_start(callback: types.CallbackQuery):
    game_id = int(callback.data.split("_")[2])
    StateService.start_edit_completion_date(callback.from_user.id, game_id)
    await callback.message.edit_text("Введите новую дату прохождения в формате YYYY.MM.DD:")
    await callback.answer()


@game_router.message(
    lambda msg: StateService.get_edit_state(msg.from_user.id) == StateService.STATE_EDIT_WAITING_COMPLETION_DATE
)
async def change_completion_save(message: types.Message):
    game_id = StateService.get_edit_game_id(message.from_user.id)
    date_result = GameService.validate_completion_date(message.text.strip())

    if not date_result.result:
        await message.reply(date_result.error_message)
        return

    result = GameService.change_completion_date(game_id, date_result.value)
    StateService.clear_edit_state(message.from_user.id)

    if result.result:
        await _show_game_info(message, game_id)
    else:
        await message.reply("Не удалось изменить дату: " + result.error_message)


@game_router.callback_query(F.data.startswith("change_note_"))
async def change_note_start(callback: types.CallbackQuery):
    game_id = int(callback.data.split("_")[2])
    StateService.start_edit_note(callback.from_user.id, game_id)

    game_result = GameService.get_game(game_id)
    text = "Введите новый комментарий:"
    if game_result.result and game_result.value.note:
        text = f"Старый комментарий: {game_result.value.note}\n\nВведите новый комментарий:"

    await callback.message.edit_text(text)
    await callback.answer()


@game_router.message(lambda msg: StateService.get_edit_state(msg.from_user.id) == StateService.STATE_EDIT_WAITING_NOTE)
async def change_note_save(message: types.Message):
    game_id = StateService.get_edit_game_id(message.from_user.id)
    note = message.text.strip()

    if not note:
        await message.reply("Комментарий не может быть пустым.")
        return

    result = GameService.edit_note(game_id, note)
    StateService.clear_edit_state(message.from_user.id)

    if result.result:
        await _show_game_info(message, game_id)
    else:
        await message.reply("Не удалось сохранить комментарий: " + result.error_message)


@game_router.callback_query(F.data.startswith("delete_game_"))
async def delete_game_start(callback: types.CallbackQuery):
    game_id = int(callback.data.split("_")[2])
    keyboard = keyboards.get_delete_confirmation_keyboard(game_id)
    await callback.message.edit_text("Вы уверены, что хотите удалить игру?", reply_markup=keyboard)
    await callback.answer()


@game_router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_game_confirm(callback: types.CallbackQuery):
    game_id = int(callback.data.split("_")[2])
    GameService.delete_game(game_id)
    await callback.message.edit_text("Игра удалена.")
    await callback.answer()


@game_router.callback_query(F.data.startswith("cancel_delete_"))
async def delete_game_cancel(callback: types.CallbackQuery):
    game_id = int(callback.data.split("_")[2])
    await _show_game_info(callback.message, game_id, edit=True)
    await callback.answer()


# --- Добавление новой игры ---

@game_router.message(F.text == "Добавить новую игру")
async def add_new_game(message: types.Message):
    user = UserService.get_user_id_by_telegram_id(message.from_user.id)
    if not user.result:
        await message.reply("Вы не зарегистрированы, введите /start для регистрации")
        return

    StateService.start_add_game(message.from_user.id, user.value)
    await message.reply("Введите название игры:")


@game_router.message(lambda msg: StateService.get_state(msg.from_user.id) == StateService.STATE_WAITING_NAME)
async def add_game_name(message: types.Message):
    game_name = message.text.strip()
    if not game_name:
        await message.reply("Название не может быть пустым. Введите название игры:")
        return

    search_result = await GameService.search_game_rawg(game_name)
    games = search_result.value if search_result.result else []

    StateService.save_game_name(message.from_user.id, game_name, games)

    if games:
        keyboard = keyboards.get_rawg_search_keyboard(games)
        await message.reply("Выберите игру из списка:", reply_markup=keyboard)
    else:
        keyboard = keyboards.get_rawg_search_keyboard([])
        await message.reply(
            "Игры не найдены в RAWG. Вы можете добавить игру вручную:",
            reply_markup=keyboard
        )


@game_router.callback_query(F.data.startswith("addgame_rawg_"))
async def add_game_rawg_selection(callback: types.CallbackQuery):
    if StateService.get_state(callback.from_user.id) != StateService.STATE_WAITING_RAWG_SELECTION:
        await callback.answer("Сначала начните добавление игры заново.")
        return

    index = int(callback.data.split("_")[2])
    data = StateService.get_data(callback.from_user.id)
    selected_game = data["rawg_games"][index]

    StateService.save_rawg_selection(callback.from_user.id, selected_game.name, selected_game.rawg_id)

    keyboard = keyboards.get_status_keyboard()
    await callback.message.edit_text("Выберите статус игры:", reply_markup=keyboard)
    await callback.answer()


@game_router.callback_query(F.data == "addgame_not_in_list")
async def add_game_manual_selection(callback: types.CallbackQuery):
    if StateService.get_state(callback.from_user.id) != StateService.STATE_WAITING_RAWG_SELECTION:
        await callback.answer("Сначала начните добавление игры заново.")
        return

    StateService.save_manual_name(callback.from_user.id)

    keyboard = keyboards.get_status_keyboard()
    await callback.message.edit_text("Выберите статус игры:", reply_markup=keyboard)
    await callback.answer()


@game_router.callback_query(F.data.startswith("addgame_status_"))
async def add_game_status(callback: types.CallbackQuery):
    if StateService.get_state(callback.from_user.id) != StateService.STATE_WAITING_STATUS:
        await callback.answer("Сначала начните добавление игры заново.")
        return

    status = int(callback.data.split("_")[2])
    StateService.save_status(callback.from_user.id, status)

    if status in (1, 4):
        StateService.go_to_rating(callback.from_user.id)
        keyboard = keyboards.get_rating_keyboard()
        await callback.message.edit_text("Выставьте оценку игре (от 1 до 10):", reply_markup=keyboard)
    else:
        StateService.go_to_comment(callback.from_user.id)
        keyboard = keyboards.get_skip_comment_keyboard()
        await callback.message.edit_text(
            "Введите комментарий к игре или нажмите «Не сейчас»:",
            reply_markup=keyboard
        )
    await callback.answer()


@game_router.callback_query(F.data.startswith("addgame_rating_"))
async def add_game_rating(callback: types.CallbackQuery):
    if StateService.get_state(callback.from_user.id) != StateService.STATE_WAITING_RATING:
        await callback.answer("Сначала начните добавление игры заново.")
        return

    rating = int(callback.data.split("_")[2])
    StateService.save_rating(callback.from_user.id, rating)

    await callback.message.edit_text("Введите дату прохождения игры в формате YYYY.MM.DD:")
    await callback.answer()


@game_router.message(lambda msg: StateService.get_state(msg.from_user.id) == StateService.STATE_WAITING_COMPLETION_DATE)
async def add_game_completion_date(message: types.Message):
    date_result = GameService.validate_completion_date(message.text.strip())

    if not date_result.result:
        await message.reply(date_result.error_message)
        return

    StateService.save_completion_date(message.from_user.id, date_result.value)

    keyboard = keyboards.get_skip_comment_keyboard()
    await message.reply(
        "Введите комментарий к игре или нажмите «Не сейчас»:",
        reply_markup=keyboard
    )


@game_router.message(lambda msg: StateService.get_state(msg.from_user.id) == StateService.STATE_WAITING_COMMENT)
async def add_game_comment(message: types.Message):
    await _finish_add_game(message.from_user.id, message, note=message.text.strip())


@game_router.callback_query(F.data == "addgame_skip_comment")
async def add_game_skip_comment(callback: types.CallbackQuery):
    if StateService.get_state(callback.from_user.id) != StateService.STATE_WAITING_COMMENT:
        await callback.answer("Сначала начните добавление игры заново.")
        return

    await _finish_add_game(callback.from_user.id, callback.message, note=None)
    await callback.answer()


async def _finish_add_game(telegram_id: int, message: types.Message, note: str | None):
    data = StateService.get_data(telegram_id)
    if data is None:
        await message.answer("Что-то пошло не так. Начните добавление заново.")
        return

    result = GameService.finish_add_game(
        user_id=data["user_id"],
        game_name=data["final_name"],
        status=data["status"],
        rawg_id=data["rawg_id"],
        rating=data["rating"],
        completion_date=data["completion_date"],
        note=note,
    )

    StateService.clear_state(telegram_id)

    if result.result:
        game = result.value
        keyboard = keyboards.get_game_info_keyboard(game.id, game.status)
        await message.answer(result.value.to_full_string(), reply_markup=keyboard)
    else:
        await message.answer("Не удалось сохранить игру: " + result.error_message)
