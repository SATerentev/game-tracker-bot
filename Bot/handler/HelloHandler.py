from aiogram import types, Router
from aiogram.filters import CommandStart
from service import UserService, StateService
import keyboards

hello_router = Router()

@hello_router.message(CommandStart())
async def cmd_start(message: types.Message):
    if not message.from_user.username:
        StateService.start_username_input(message.from_user.id)
        await message.answer("У вас отсутствует username в Telegram.\nВпишите желаемое имя пользователя для бота:")
        return
    UserService.register_user(message.from_user.username, message.from_user.id)
    await message.answer("Добро пожаловать!", reply_markup=keyboards.get_main_menu_keyboard())

@hello_router.message(lambda message: StateService.get_state(message.from_user.id) == StateService.STATE_WAITING_USERNAME)
async def username_input(message: types.Message):
    username = message.text.strip()
    result = UserService.check_username(message.from_user.id, username)
    if not result.result:
        await message.answer(result.message)
        return
    UserService.register_user(username, message.from_user.id)
    StateService._user_states.pop(message.from_user.id, None)
    await message.answer(f"Ваше имя пользователя для бота установлено как: {username}.\nДобро пожаловать!", reply_markup=keyboards.get_main_menu_keyboard())