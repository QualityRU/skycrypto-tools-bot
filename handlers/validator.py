from aiogram.fsm.context import FSMContext
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


async def login_required(state: FSMContext):
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
