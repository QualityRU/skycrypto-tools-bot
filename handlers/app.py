from aiogram import F, Router

# from aiogram.enums.chat_action import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    FSInputFile,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

import config

router = Router()
access = F.from_user.id.in_(config.ACCESS_IDS)


@router.message(Command(commands=['app']), access)
async def cmd_app(message: Message, state: FSMContext):
    # result: bool = await bot.send_chat_action(
    #     chat_id=message.from_user.id, action=ChatAction.TYPING
    # )
    auth_data = await state.get_data()

    token_for_api = auth_data.get('token_for_api')

    ReplyKeyboardRemove()
    keyboard_markup = ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text='/menu')],
            [KeyboardButton(text='/relogin'), KeyboardButton(text='/help')],
        ],
    )

    agenda = FSInputFile(path=config.APP_ANDROID_FILE, filename='skysms.apk')
    await message.reply_document(document=agenda)
    msg = """Ваш временный токен для авторизации в приложении SKY SMS:
<tg-spoiler><code>{token}</code></tg-spoiler>

Вернуться в главное меню <b>/menu</b>""".format(
        token=token_for_api
    )
    await message.answer(text=msg, reply_markup=keyboard_markup)
