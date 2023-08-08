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
import libs.skycrypto as skycrypto

router = Router()
access = F.from_user.id.in_(config.ACCESS_IDS)


@router.message(Command(commands=['info']), access)
async def cmd_info(message: Message, state: FSMContext):
    # result: bool = await bot.send_chat_action(
    #     chat_id=message.from_user.id, action=ChatAction.TYPING
    # )
    auth_data = await state.get_data()
    nickname = auth_data.get('nickname')
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

    wallets = await skycrypto.result_not_error(
        await skycrypto.operations(tokens=tokens, func='total-balance')
    )
    if wallets[0]:
        msg = wallets[1]
        await message.answer(text=msg)
        return
    wallets = wallets[1]

    user_wallets = await skycrypto.result_not_error(
        await skycrypto.users_wallets(tokens=tokens)
    )
    if user_wallets[0]:
        msg = user_wallets[1]
        await message.answer(text=msg)
        return
    user_wallets = user_wallets[1]
    msg_user_wallet = ''
    for wallet in user_wallets:
        msg_user_wallet += """ * {symbol}: {balance} , заморожено: {frozen}
    * Адрес: <code>{address}</code>
""".format(
            symbol=wallet.get('symbol').upper(),
            balance=wallet.get('balance'),
            frozen=wallet.get('frozen'),
            address=wallet.get('address'),
        )

    users = await skycrypto.result_not_error(
        await skycrypto.users(tokens=tokens, nickname=nickname)
    )
    if users[0]:
        msg = users[1]
        await message.answer(text=msg)
        return
    users = users[1]

    msg = """<b>ИНФОРМАЦИЯ ОБ АККАУНТЕ</b>
<b>БАЛАНС</b>
- Сумма: {currency} {symbol}
{msg_user_wallet}
<b>СДЕЛКИ</b>
- Прокручено всего: {amount_currency} {symbol}
- Завершенно сделок всего: {deals}
- Рейтинг: {rating} (👍 {likes} / 👎 {dislikes})
- Регистрация: {registered} дней назад
- Верификация: {verified}
- Почта: <code>{email}</code>
- Ник: <code>/u{nickname}</code>""".format(
        currency=int(wallets.get(users.get('currency'))),
        symbol=users.get('currency').upper(),
        msg_user_wallet=msg_user_wallet,
        amount_currency=int(users.get('deals').get('amount_currency')),
        deals=users.get('deals').get('deals'),
        rating=users.get('rating'),
        likes=users.get('deals').get('likes'),
        nickname=users.get('nickname'),
        dislikes=users.get('deals').get('dislikes'),
        email=users.get('email'),
        registered=users.get('registered'),
        verified=users.get('verified'),
    )

    await message.answer(text=msg, reply_markup=keyboard_markup)
