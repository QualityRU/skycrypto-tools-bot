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
import libs.process as process
from libs.fsm import AuthStates

router = Router()
access = F.from_user.id.in_(config.ACCESS_IDS)


@router.message(Command(commands=['restakan']), access)
async def cmd_restakan(message: Message, state: FSMContext):
    # result: bool = await bot.send_chat_action(
    #     chat_id=message.from_user.id, action=ChatAction.TYPING
    # )
    auth_data = await state.get_data()
    tokens = [auth_data.get('tokens')]
    task_lots = auth_data.get('task_lots')

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

    if not task_lots:
        ReplyKeyboardRemove()
        keyboard_markup = ReplyKeyboardMarkup(
            one_time_keyboard=True,
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text='/stakan')],
                [KeyboardButton(text='/menu')],
                [KeyboardButton(text='/help')],
            ],
        )
        msg = 'Сканирование не было стаканов запущено!'
        await message.answer(text=msg, reply_markup=keyboard_markup)
        return

    await state.update_data(task_lots=True)
    msg = """🔄🚫 Cканирование стаканов по BTC и USDT остановлено!

Вернуться в главное меню: <b>/menu</b>"""
    await message.answer(text=msg)


@router.message(Command(commands=['stakan']), access)
async def cmd_stakan(message: Message, state: FSMContext):
    # result: bool = await bot.send_chat_action(
    #     chat_id=message.from_user.id, action=ChatAction.TYPING
    # )
    auth_data = await state.get_data()
    tokens = [auth_data.get('tokens')]
    task_lots = auth_data.get('task_lots')

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

    if task_lots:
        ReplyKeyboardRemove()
        keyboard_markup = ReplyKeyboardMarkup(
            one_time_keyboard=True,
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text='/restakan')],
                [KeyboardButton(text='/menu')],
                [KeyboardButton(text='/help')],
            ],
        )
        msg = 'Сканирование стаканов уже запущено!'
        await message.answer(text=msg, reply_markup=keyboard_markup)
        return

    msg = '💵 Введите цену покупки <u>BTC</u>. Вводить через точку десятичные!'
    await message.answer(text=msg)
    await state.set_state(state=AuthStates.rate_buy_btc)


@router.message(AuthStates.rate_buy_btc, access)
async def ask_rate_buy_btc(message: Message, state: FSMContext):
    # result: bool = await bot.send_chat_action(
    #     chat_id=message.from_user.id, action=ChatAction.TYPING
    # )
    try:
        rate_buy_btc = float(message.text)
    except Exception:
        msg = """❗️ Введите например <u>1818187.40</u>, где знак десятичных - точка."""
        await message.answer(text=msg)
        return

    await state.update_data(rate_buy_btc=rate_buy_btc)
    await state.set_state(state=AuthStates.rate_buy_usdt)

    msg = '💵 Введите цену покупки <u>USDT</u>. Вводить через точку десятичные!'
    await message.answer(text=msg)


@router.message(AuthStates.rate_buy_usdt, access)
async def ask_rate_buy_usdt(message: Message, state: FSMContext):
    # result: bool = await bot.send_chat_action(
    #     chat_id=message.from_user.id, action=ChatAction.TYPING
    # )
    ReplyKeyboardRemove()
    keyboard_markup = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text='/menu')],
            [
                KeyboardButton(text='/restakan'),
                KeyboardButton(text='/relogin'),
                KeyboardButton(text='/help'),
            ],
        ],
    )
    try:
        rate_buy_usdt = float(message.text)
    except Exception:
        msg = """❗️ Введите например 72.4, где знак десятичных - точка."""
        await message.answer(text=msg)
        return

    # spred = 1.0
    # spred_buy_usdt = rate_buy_usdt + (rate_buy_usdt * spred / 100)

    await state.update_data(rate_buy_usdt=rate_buy_usdt)
    await state.update_data(task_lots=True)

    msg = """🔄 Запукаю сканирование стаканов по BTC и USDT!

Вернуться в главное меню: <b>/menu</b>"""
    await message.answer(text=msg, reply_markup=keyboard_markup)
    await process.lots_coro(message=message, state=state)
