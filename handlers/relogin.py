from aiogram import F, Router
from aiogram.enums.chat_action import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
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
    # result: bool = await bot.send_chat_action(
    #     chat_id=message.from_user.id, action=ChatAction.TYPING
    # )
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
        msg = """⛔️ Вы вышли с сайта SKYCRYPTO
Вернуться в главное меню: <b>/menu</b>"""
        await message.answer(text=msg, reply_markup=keyboard_markup)

    await state.update_data(tokens=False)
    await state.update_data(nickname=False)
    await state.update_data(email=False)
    await state.update_data(password=False)
    await state.update_data(task_lots=False)
    await state.update_data(code=None)

    msg = """'↪️ Авторизация на сайте SKYCRYPTO.
Приготовьтесь вводить E-mail и пароль.
Если установлен код из Google Authentificator!"""
    await message.answer(text=msg)
    msg = 'Введите Ваш E-mail:'
    await message.answer(text=msg)
    await state.set_state(state=AuthStates.email)
