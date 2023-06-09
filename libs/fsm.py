from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    token_for_api = State()

    loggined = State()
    telegram_id = State()
    telegram_username = State()
    registered = State()
    nickname = State()
    email = State()
    password = State()
    code = State()
    gaf = State()

    tokens = State()
    authkey = State()

    recapcha_achor = State()
    recapcha_reload = State()

    lots_my_change = State()
    lots_my = State()

    lots_market_change = State()
    lots_market = State()

    deals_change = State()
    deals_last = State()
    lots_market_massive = State()

    operations_change = State()
    operations_last = State()

    task_lots = State()
    my_banks = State()
    rate_buy_usdt = State()
    rate_buy_btc = State()
    rate_buy_eth = State()
    limit_to_buy = State()
