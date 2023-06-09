from aiogram import F, Router
from aiogram.enums.chat_action import ChatAction
from aiogram.filters import Command
from aiogram.methods import SendChatAction
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

import config

router = Router()
access = F.from_user.id.in_(config.ACCESS_IDS)


@router.message(Command(commands=['help']), access)
async def cmd_help(message: Message):
    await SendChatAction(
        chat_id=message.from_user.id, action=ChatAction.TYPING
    )

    ReplyKeyboardRemove()
    keyboard_markup = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text='/menu')],
            [KeyboardButton(text='/relogin'), KeyboardButton(text='/help')],
        ],
    )
    msg = """
Версия бота: <b>{version}</b>
<pre>Это бот, который автоматизирует работу трейдера на сайте {url}.

Информация будет дополняться по мере написания бота</pre>

Скачать приложение для считывания СМС: <b>/app</b>
Вернуться в главное меню: /menu""".format(
        version=config.VERSION, url=config.SKYCRYPTO_URL
    )
    await message.answer(text=msg, reply_markup=keyboard_markup)
