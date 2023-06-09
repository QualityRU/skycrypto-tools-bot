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
import libs.skycrypto as skycrypto

router = Router()
access = F.from_user.id.in_(config.ACCESS_IDS)


@router.message(Command(commands=['deals']), access)
async def cmd_deals(message: Message, state: FSMContext):
    await SendChatAction(
        chat_id=message.from_user.id, action=ChatAction.TYPING
    )
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
            [KeyboardButton(text='/menu')],
            [KeyboardButton(text='/relogin'), KeyboardButton(text='/help')],
        ],
    )

    if message.text == '/deals on':
        deals = await skycrypto.result_not_error(
            await skycrypto.operations(
                tokens=tokens, func='trading-status', is_active=True
            )
        )
        msg = '✅ Сделки включены!'
    elif message.text == '/deals off':
        deals = await skycrypto.result_not_error(
            await skycrypto.operations(
                tokens=tokens, func='trading-status', is_active=False
            )
        )
        msg = '⛔️ Сделки выключены!'
    else:
        msg = """🚫 Чтобы управлять включением и выключением сделок используйте:
/deals on
/deals off"""
    await message.answer(text=msg, reply_markup=keyboard_markup)
