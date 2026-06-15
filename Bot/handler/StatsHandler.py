from aiogram import types, Router, F
from service import UserService, StatsService
import keyboards

stats_router = Router()

REPORT_PERIODS = {
    "report_last_12_months": StatsService.PERIOD_LAST_12_MONTHS,
    "report_current_year": StatsService.PERIOD_CURRENT_YEAR,
    "report_all_time": StatsService.PERIOD_ALL_TIME,
}


@stats_router.message(F.text == "Сформировать отчёт")
async def report_menu(message: types.Message):
    user = UserService.get_user_id_by_telegram_id(message.from_user.id)
    if not user.result:
        await message.reply("Вы не зарегистрированы, введите /start для регистрации")
        return

    keyboard = keyboards.get_report_period_keyboard()
    await message.answer("Выберите период для отчёта:", reply_markup=keyboard)


@stats_router.callback_query(F.data.in_(REPORT_PERIODS.keys()))
async def report_generate(callback: types.CallbackQuery):
    user = UserService.get_user_id_by_telegram_id(callback.from_user.id)
    if not user.result:
        await callback.message.answer("Вы не зарегистрированы, введите /start для регистрации")
        await callback.answer()
        return

    period = REPORT_PERIODS[callback.data]
    result = StatsService.get_user_stats(user.value, period)

    if result.result:
        await callback.message.answer(result.value)
    else:
        await callback.message.answer("Не удалось сформировать отчёт: " + result.error_message)

    await callback.answer()
