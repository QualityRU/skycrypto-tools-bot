from logging import getLogger
from secrets import token_hex

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
import jwt

import config
import libs.db as db
import libs.process as process
import libs.skycrypto as skycrypto
from handlers.start import cmd_menu
from libs.fsm import AuthStates

router = Router()
access = F.from_user.id.in_(config.ACCESS_IDS)
Logger = getLogger(name=__name__)


@router.message(Command(commands=['login']), access)
async def cmd_login(message: Message, state: FSMContext):
    await SendChatAction(
        chat_id=message.from_user.id, action=ChatAction.TYPING
    )
    if message.from_user.username:
        username = f'@{message.from_user.username}'
    else:
        username = message.from_user.first_name
    auth_data_dynamic = await state.get_data()

    if auth_data_dynamic.get('loggined'):
        ReplyKeyboardRemove()
        keyboard_markup = ReplyKeyboardMarkup(
            one_time_keyboard=True,
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text='/menu')],
                [
                    KeyboardButton(text='/relogin'),
                    KeyboardButton(text='/help'),
                ],
            ],
        )
        msg = """🚫 Вы уже авторизированы! Повторная авторизация не требуется!
Для входа в меню нажмите: <b>/menu</b>"""
        await message.answer(text=msg, reply_markup=keyboard_markup)
        return

    auth_data = await db.auth_get(telegram_id=message.from_user.id)

    if type(auth_data) == dict and not auth_data_dynamic.get('loggined'):
        await state.update_data(telegram_id=auth_data.get('telegram_id'))
        await state.update_data(telegram_username=username)
        await state.update_data(email=auth_data.get('email'))
        await state.update_data(password=auth_data.get('password'))
        await state.update_data(nickname=auth_data.get('nickname'))
        await state.update_data(gaf=auth_data.get('gaf'))

        msg = """Вы ранее успешно авторизовывались на сайте SKYCRYPTO.
Поэтому для удобства я запомнил Вас."""
        await message.answer(text=msg)
        await process_login(message=message, state=state)
        return

    msg = """↪️ Авторизация на сайте SKYCRYPTO.
Приготовьтесь вводить E-mail и пароль.
Если установлен код из Google Authentificator!"""
    await message.answer(text=msg)
    msg = 'Введите Ваш E-mail:'
    await message.answer(text=msg)
    await state.set_state(state=AuthStates.email)


@router.message(AuthStates.email, access)
async def ask_login_email(message: Message, state: FSMContext):
    await SendChatAction(
        chat_id=message.from_user.id, action=ChatAction.TYPING
    )
    if message.from_user.username:
        username = f'@{message.from_user.username}'
    else:
        username = message.from_user.first_name
    email = message.text.split('@')

    if len(email) != 2:
        msg = """❗️ Почта должна содержать имя пользователя, собаку и домен!
Пример: user@mail.ru.
Введите заново E-mail:"""
        await message.answer(text=msg)
        return

    email = message.text

    await state.update_data(email=email)
    msg = 'Введите Ваш пароль:'
    await message.answer(text=msg)
    await state.update_data(telegram_username=username)
    await state.update_data(telegram_id=message.from_user.id)
    await state.set_state(state=AuthStates.password)


@router.message(AuthStates.password, access)
async def ask_login_password(message: Message, state: FSMContext):
    await SendChatAction(
        chat_id=message.from_user.id, action=ChatAction.TYPING
    )
    password = message.text

    if len(password) < 8:
        msg = '❗️ Пароль слишком короткий. Введите заново пароль:'
        await message.answer(text=msg)
        return

    await state.update_data(password=password)
    await state.update_data(gaf=False)
    await process_login(message=message, state=state)


@router.message(AuthStates.code, access)
async def ask_login_code(message: Message, state: FSMContext):
    await SendChatAction(
        chat_id=message.from_user.id, action=ChatAction.TYPING
    )
    code = message.text

    if not code.isdigit():
        msg = '❗️ Код может состоять только из цифр! Введите заново 2FA:'
        await message.answer(text=msg)
        return
    await state.update_data(code=code)
    await state.update_data(gaf=True)
    await process_login(message=message, state=state)


async def process_login(message: Message, state: FSMContext):
    await SendChatAction(
        chat_id=message.from_user.id, action=ChatAction.TYPING
    )
    auth_data = await state.get_data()

    telegram_id = auth_data.get('telegram_id')
    email = auth_data.get('email')
    password = auth_data.get('password')
    code = auth_data.get('code')

    if not email and not password:
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

    tokens = await skycrypto.auth_login(
        email=email, password=password, code=code
    )

    if tokens[0].get('request_code'):
        msg = """Введите код из Google Authentificator
для {email}:""".format(
            email=email
        )
        await message.answer(text=msg)
        await state.set_state(state=AuthStates.code)
        return

    if tokens[0].get('status') == 'Error':
        if tokens[0].get('description'):
            description = tokens[0].get('description').split("',")
            detail = description[0].replace("{'detail': '", '')
            Logger.debug(msg=description)
            if detail == 'No such login and password':
                msg = '❗️ Ошибка! Указанное логина и пароля не найдено в системе.'
                await state.update_data(email=None)
                await state.update_data(password=None)
                await state.update_data(code=None)
            elif detail == 'Wrong 2fa code':
                msg = '❗️ Ошибка! Не верный 2fa код!'
                await state.update_data(code=None)
            else:
                await state.update_data(code=None)
                msg = tokens[0].get('description')
        else:
            msg = str(tokens[0])
        msg = f'{msg}\n\nВведите заново Ваш email:'
        await message.answer(text=msg)
        await state.set_state(state=AuthStates.email)
        return

    if tokens[0].get('access') and tokens[0].get('refresh'):
        await state.update_data(tokens=tokens[0])

    jwt_decode = jwt.decode(
        jwt=tokens[0].get('access'),
        algorithms=['HS256'],
        options={'verify_signature': False},
    )
    await state.update_data(nickname=jwt_decode.get('nickname'))

    msg = '✅ Успешная авторизация! Загружаю данные!'
    await message.answer(text=msg)
    await state.update_data(loggined=True)

    auth_data = await db.auth_get(telegram_id=telegram_id)
    if not type(auth_data) == dict:
        await db.auth_set(state=state)

    await cmd_menu(message=message, state=state)
    token_for_api = token_hex(16)
    await state.update_data(token_for_api=token_for_api)
    #     msg = '''Ваш временный токен для авторизации в приложении SKY SMS:
    # <code><tg-spoiler>{token}</tg-spoiler></code>

    # Скачать приложение для считывания СМС: <b>/app</b>
    # '''.format(token=token_for_api)

    # await process.deals_coro(message=message, state=state)
    await process.refresh_tokens_task(state=state)
