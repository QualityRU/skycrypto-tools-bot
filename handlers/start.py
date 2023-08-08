from aiogram import F, Router

# from aiogram.enums.chat_action import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

import config

router = Router()
access = F.from_user.id.in_(config.ACCESS_IDS)


@router.message(Command(commands=['start']), access)
async def cmd_start(message: Message):
    # result: bool = await bot.send_chat_action(
    #     chat_id=message.from_user.id, action=ChatAction.TYPING
    # )
    ReplyKeyboardRemove()
    keyboard_markup = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text='/login')],
            [KeyboardButton(text='/help')],
        ],
    )

    msg = """Это стартовое меню бота!

Для авторизации нажмите кнопку: <b>/login</b>
<i>Если ранее был произведен вход - то бот зайдет сам, используя успешно введенный E-mail и пароль. Если есть Google Auth, спросит его!</i>

Твой TG ID: <code>{tgid}</code>
Для вызова помощи - <b>/help</b>""".format(
        tgid=message.from_user.id
    )
    await message.answer(text=msg, reply_markup=keyboard_markup)


@router.message(Command(commands=['menu']), access)
async def cmd_menu(message: Message, state: FSMContext):
    # result: bool = await bot.send_chat_action(
    #     chat_id=message.from_user.id, action=ChatAction.TYPING
    # )
    auth_data = await state.get_data()

    tokens = [auth_data.get('tokens')]

    if not tokens[0]:
        ReplyKeyboardRemove()
        keyboard_markup = ReplyKeyboardMarkup(
            one_time_keyboard=True,
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text='/login')],
                [KeyboardButton(text='/help')],
            ],
        )
        msg = '🚫 Вы не авторизованы! Для авторизации нажмите: <b>/login</b>'
        await message.answer(text=msg, reply_markup=keyboard_markup)
        return

    ReplyKeyboardRemove()
    keyboard_markup = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text='/stakan'), KeyboardButton(text='/spam')],
            [KeyboardButton(text='/deals'), KeyboardButton(text='/info')],
            [
                KeyboardButton(text='/relogin'),
                KeyboardButton(text='/restakan'),
                KeyboardButton(text='/settings'),
                KeyboardButton(text='/help'),
            ],
        ],
    )
    msg = """Меню бота"""
    await message.answer(text=msg, reply_markup=keyboard_markup)
