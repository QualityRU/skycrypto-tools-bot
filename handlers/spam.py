from aiogram import F, Router

# from aiogram.enums.chat_action import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

import config
import libs.skycrypto as skycrypto

router = Router()
access = F.from_user.id.in_(config.ACCESS_IDS)


@router.message(Command(commands=['spam']), access)
async def cmd_spam(message: Message, state: FSMContext):
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

    lots_my = await skycrypto.lots(
        tokens=tokens, lot_type='sell', currency='rub'
    )
    lots_my = await skycrypto.result_not_error(result=lots_my)
    lots_dict = dict()
    for lot in lots_my[1]:
        bank = lot.get('broker').get('name')
        symbol = lot.get('symbol')
        if symbol not in lots_dict:
            lots_dict[symbol] = list()
        if bank not in lots_dict.get(symbol):
            lots_dict.get(symbol).append(bank)

    msg = """<b>Выберите направление которое спамить.</b>
Внимание! Данный раздел формируется на основании включенных лотов в ЛК!

Вернуться в главное меню <b>/menu</b>"""
    inline_keyboard = list()
    for bank in sorted(lots_dict.keys()):
        inline_keyboard.append(
            [InlineKeyboardButton(text=bank.upper(), callback_data=bank)]
        )

    inline_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    await message.answer(
        text=msg,
        reply_markup=inline_markup,
    )
    # await message.answer(text=msg, reply_markup=keyboard_markup)
