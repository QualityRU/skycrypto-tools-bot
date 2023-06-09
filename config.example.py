VERSION = '0.3.05 pre-beta'
PARSE_MODE = 'HTML'  # MarkdownV2, HTML, None
"""------------------------------------------------------------------------"""
# SKY TOOLS BOT
TELEGRAM_TOKEN = ''

"""------------------------------------------------------------------------"""
ADMIN_ID = 1234
ACCESS_IDS = (ADMIN_ID,)
"""------------------------------------------------------------------------"""
DB_AUTH = ''
APP_ANDROID_FILE = ''
SKYCRYPTO_URL = 'skycrypto.me'
SKYCRYPTO_SSL = False  # True
SKYCRYPTO_DEBUG = True  # False
SKYCRYPTO_TIME_DELAY = (0.3, 0.6)  # seconds
SKYCRYPTO_REFRESH_TOKEN = (9, 12)  # minutes
SKYCRYPTO_REFRESH_GET_LOTS_MARKET = (1.5, 3)  # seconds
SKYCRYPTO_REFRESH_SET_DEALS = (1.5, 3)  # seconds
SKYCRYPTO_REFRESH_DEALS = 25  # seconds
SKYCRYPTO_REFRESH_LOTS = 300  # seconds
SKYCRYPTO_REFRESH_OPERATIONS = 60  # seconds
SKYCRYPTO_REFRESH_RATES = 60  # seconds
SKYCRYPTO_SYMBOL_LIST = ('btc', 'eth', 'usdt')
SKYCRYPTO_CURRENCY_LIST = ('byn', 'kzt', 'rub', 'uah', 'usd')
SKYCRYPTO_BANKS_DICT = {
    'QIWI': '🟠',
    'Сбербанк': '🟢',
    'Тинькофф': '🟡',
    'С карты на карту': '⚪️',
    'Яндекс.Деньги': '🟣',
    'Любой банк РФ': '🔘',
    'Пополнение телефона': '🟤',
    'Mastercard': '🔘',
    'Альфа-Банк': '🔴',
    'ВТБ 24': '🔵',
    'VISA': '🔘',
    'Райффайзен': '🟡',
    'МТС-банк': '🔴',
    'PAYEER': '🟢',
    'Почта банк': '🔵',
    'WebMoney': '🔵',
    'Промсвязьбанк': '🟣',
    'Другие способы': '⚫️',
    'Наличные в ATM': '⚫️',
    'МИР': '🟢',
    'СБП (банк-банк)': '🟢',
    'Росбанк': '🔴',
}
RECAPCHA_ACHOR = {
    'ar': '1',
    'k': '6LeiCBkiAAAAAOEk8F5o15xMGWy-wqhXH654jV5s',
    'co': 'aHR0cHM6Ly9za3ljcnlwdG8ubWU6NDQz',
    'hl': 'ru',
    'v': 'zmiYzsHi8INTJBWt2QZC9aM5',
    'size': 'invisible',
}
RECAPCHA_REALOAD = {'k': '6LeiCBkiAAAAAOEk8F5o15xMGWy-wqhXH654jV5s'}
"""------------------------------------------------------------------------"""
LOG_LEVEL = 'DEBUG'  # DEBUG
LOG_STYLE = {
    'critical': {'bold': True, 'color': 'red'},
    'debug': {'color': 'magenta'},
    'error': {'color': 'red'},
    'info': {'bold': True, 'color': 'green'},
    'notice': {'color': 'magenta'},
    'spam': {'color': 'green', 'faint': True},
    'success': {'bold': True, 'color': 'green'},
    'verbose': {'color': 'blue'},
    'warning': {'color': 'yellow'},
}
LOG_FORMAT = (
    '%(asctime)s,%(msecs)03d %(filename)+13s (%(name)s)'
    '[ LINE:%(lineno)-4s] %(levelname)s %(message)s'
)
"""------------------------------------------------------------------------"""
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/114.0.0.0 Safari/537.36'
)
