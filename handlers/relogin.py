from aiogram import F, Router
from aiogram.enums.chat_action import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendChatAction
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

import config
from libs.fsm import AuthStates

router = Router()
access = F.from_user.id.in_(config.ACCESS_IDS)


@router.message(Command(commands=['relogin']), access)
async def cmd_relogin(message: Message, state: FSMContext):
    await SendChatAction(
        chat_id=message.from_user.id, action=ChatAction.TYPING
    )
    auth_data = await state.get_data()

    ReplyKeyboardRemove()
    keyboard_markup = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text='/login')],
            [KeyboardButton(text='/help')],
        ],
    )
    if auth_data.get('loggined'):
        await state.update_data(loggined=False)
        await state.update_data(task_lots=False)
        await state.update_data(code=None)
        msg = """⛔️ Вы вышли с сайта SKYCRYPTO
Вернуться в главное меню: <b>/menu</b>"""
        await message.answer(text=msg, reply_markup=keyboard_markup)

    msg = """'↪️ Авторизация на сайте SKYCRYPTO.
Приготовьтесь вводить ник, E-mail, пароль.
Если установлен код из Google Authentificator!"""
    await message.answer(text=msg)
    msg = 'Введите Ваш ник в SKYCRYPTO (начинается с /u):'
    await message.answer(text=msg)
    await state.set_state(state=AuthStates.nickname)
