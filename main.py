from asyncio import Runner, run
from logging import basicConfig, getLogger
from os import path
from sys import version_info

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat
from coloredlogs import install as color_install
from uvloop import install as uvloop_install
from uvloop import new_event_loop

import config
from handlers import include_router


async def set_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command='start', description='Стартовое меню'),
        BotCommand(command='login', description='Авторизация на сайте'),
        BotCommand(command='help', description='Помощь'),
    ]

    for chat_id in config.ACCESS_IDS:
        await bot.set_my_commands(
            commands=commands, scope=BotCommandScopeChat(chat_id=chat_id)
        )


async def main():
    bot = Bot(
        token=config.TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=config.PARSE_MODE),
    )
    dp = Dispatcher(storage=MemoryStorage())
    include_router(dp=dp)
    # await set_bot_commands(bot=bot)
    Logger.debug(msg='Starting bot')
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    basicConfig(filename=f'{path.dirname(__file__)}/dynamic/skycrypto.log')
    Logger = getLogger(name=__name__)
    color_install(
        level=config.LOG_LEVEL,
        level_styles=config.LOG_STYLE,
        fmt=config.LOG_FORMAT,
    )

    try:
        # run(main=main())
        if version_info >= (3, 11):
            with Runner(loop_factory=new_event_loop) as runner:
                runner.run(main())
        else:
            uvloop_install()
            run(main=main())
    except (KeyboardInterrupt, SystemExit):
        Logger.error(msg='Bot stopped!')
