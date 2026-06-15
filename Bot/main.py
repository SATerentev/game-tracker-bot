import os
import asyncio

from config import BOT_TOKEN
from aiogram import Bot, Dispatcher
from handler import HelloHandler, GameHandler, StatsHandler
from logging_config import setup_logging
from middleware.TimingMiddleware import TimingMiddleware

BOT_TOKEN = os.getenv('BOT_TOKEN')


async def main():
    setup_logging()

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.message.middleware(TimingMiddleware())
    dp.callback_query.middleware(TimingMiddleware())
    dp.include_router(HelloHandler.hello_router)
    dp.include_router(GameHandler.game_router)
    dp.include_router(StatsHandler.stats_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
