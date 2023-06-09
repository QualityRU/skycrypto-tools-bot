from asyncio import TimeoutError, create_task, gather, sleep

# from quickjs import Function as eval_js
# from os import path
from hashlib import md5
from logging import getLogger
from random import uniform
from re import compile
from urllib import parse

from aiohttp import (
    ClientConnectorError,
    ClientError,
    ClientSession,
    CookieJar,
    TCPConnector,
)

# from json import loads as json_loads
from ujson import loads as json_loads

import config


async def fetch(
    session,
    url,
    json=None,
    data=None,
    patch=False,
    result_text=True,
    verify_ssl=True,
):
    log_msg = 'None'

    if json and not patch or data and not patch:
        usession = session.post
    elif json and patch:
        usession = session.patch
    else:
        usession = session.get

    try:
        async with usession(
            url=url, json=json, data=data, verify_ssl=verify_ssl
        ) as response:
            if not response.ok:
                result = dict(
                    status='Error',
                    description=str(await response.json(loads=json_loads)),
                )
            else:
                if result_text:
                    result = await response.text()
                else:
                    result = await response.json(loads=json_loads)

                log_msg = '{url}:{port}, {status}, {method}'.format(
                    url=response.url,
                    port=response.url.port,
                    status=response.status,
                    method=response.method,
                )
                await session.close()
    except ClientConnectorError as e:
        result = dict(
            status='Error', description='ClientConnectorError: {e}'.format(e=e)
        )
    except ClientError as e:
        result = dict(
            status='Error', description='ClientError: {e}'.format(e=e)
        )
    except TimeoutError as e:
        result = dict(
            status='Error', description='TimeoutError: {e}'.format(e=e)
        )
    except Exception as e:
        result = dict(status='Error', description='Exception: {e}'.format(e=e))

    if config.SKYCRYPTO_DEBUG:
        getLogger(name=__name__).debug(msg=log_msg)
    return result


async def skycrypto(
    headers: dict,
    urls: list,
    json=None,
    data=None,
    patch=False,
    result_text=False,
):
    a, b = config.SKYCRYPTO_TIME_DELAY
    time_sleep = uniform(a=a, b=b)
    await sleep(time_sleep)

    async with ClientSession(
        headers=headers,
        connector=TCPConnector(ssl=config.SKYCRYPTO_SSL),
        cookie_jar=CookieJar(unsafe=True),
    ) as session:
        tasks = [
            create_task(
                fetch(
                    session=session,
                    url=url,
                    json=json,
                    data=data,
                    patch=patch,
                    result_text=result_text,
                    verify_ssl=config.SKYCRYPTO_SSL,
                )
            )
            for url in urls
        ]
        return await gather(*tasks)


async def auth_login(email: str, password: str, code: str = ''):
    headers = {'User-Agent': config.USER_AGENT}
    urls = [f'https://api.{config.SKYCRYPTO_URL}/rest/v1/auth/login']
    json = dict(email=email, password=password)
    if code:
        json['code'] = code
    return await skycrypto(headers=headers, urls=urls, json=json)


async def codedata(tokens: list):
    """
    function generateSecretKey(): string {
      if (secretKey) {
        return secretKey;
      }
      if (!codeData) {
        return '';
      }

      const needReverse = codeData['aKM'] === 'e';
      const md5 = new Md5();
      let codedataKeys = Object.keys(codeData).sort();
      needReverse && (codedataKeys = codedataKeys.reverse());

      const codedataValues = codedataKeys.map((key) => codeData?.[key]);
      const result = codedataValues.join('') + 'l';
      secretKey = md5.appendStr(result).end() as string;
      return secretKey;"""

    access_token = tokens[0].get('access')
    headers = {
        'Authorization': f'Bearer {access_token}',
        'User-Agent': config.USER_AGENT,
    }
    urls = [f'https://api.{config.SKYCRYPTO_URL}/rest/v1/codedata']

    codedata_dict = await skycrypto(headers=headers, urls=urls)
    need_reverse = codedata_dict[0].get('aKM') == 'e'
    codedata = dict(sorted(codedata_dict[0].items(), reverse=need_reverse))
    codedata = f'{"".join(codedata.values())}l'

    if not codedata:
        return ''

    authkey = md5(codedata.encode())
    return authkey.hexdigest()

    # code_js = open(f'{path.dirname(__file__)}/js_md5/md5.js').read()
    # result_md5 = eval_js(name='result_md5', code=code_js)
    # authkey = result_md5(codedata)
    # return authkey


async def auth_refresh(tokens: list):
    access_token = tokens[0].get('refresh')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }
    urls = [f'https://api.{config.SKYCRYPTO_URL}/rest/v1/auth/refresh']
    json = {'token': access_token}
    return await skycrypto(headers=headers, urls=urls, json=json)


async def recaptcha():
    anchor_data = ''
    for k, v in zip(
        config.RECAPCHA_ACHOR.keys(), config.RECAPCHA_ACHOR.values()
    ):
        anchor_data += f'{k}={v}&'

    headers = {'User-Agent': config.USER_AGENT}

    urls = [f'https://www.google.com/recaptcha/api2/anchor?{anchor_data}']
    recaptcha = await skycrypto(headers=headers, urls=urls, result_text=True)
    # recaptcha_token = findall(pattern=r'(id="recaptcha-token".*")', string=recaptcha[0], flags=IGNORECASE)
    # recaptcha_token = recaptcha_token[0].replace('id="recaptcha-token" value="', '').replace('"', '')
    recaptcha_regex = compile(
        pattern=r'<input type="hidden" id="recaptcha-token" value="([^"]+)">'
    )
    recaptcha_token = recaptcha_regex.search(recaptcha[0]).group(1)

    reload_data = ''
    for k, v in zip(
        config.RECAPCHA_REALOAD.keys(), config.RECAPCHA_REALOAD.values()
    ):
        reload_data += f'{k}={v}&'

    urls = [f'https://www.google.com/recaptcha/api2/reload?{reload_data}']
    data = {'reason': 'q', 'c': recaptcha_token}
    recaptcha_reload = await skycrypto(
        headers=headers, data=data, urls=urls, result_text=True
    )
    recaptcha_reload = recaptcha_reload[0]

    prefix = ")]}'"
    if recaptcha_reload.startswith(prefix):
        recaptcha_reload = recaptcha_reload[len(prefix) :]
    captcha_token = json_loads(recaptcha_reload)[1]

    return captcha_token


async def users(tokens: list, nickname: str):
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }
    urls = [f'https://api.{config.SKYCRYPTO_URL}/rest/v1/users/{nickname}']
    return await skycrypto(headers=headers, urls=urls)


async def users_accounts_join_status(tokens: list):
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }
    urls = [
        f'https://api.{config.SKYCRYPTO_URL}/rest/v1/users/accounts-join-status'
    ]
    return await skycrypto(headers=headers, urls=urls)


async def users_otp_auth(tokens: list):
    """{"otp_auth":"otpauth://totp/SKY%20CRYPTO:lenshinvladimir19%40gmail.com?secret=ODO5N42PVEQH6GAN&issuer=SKY%20CRYPTO","otp_secret":"ODO5N42PVEQH6GAN"}"""
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }
    urls = [f'https://api.{config.SKYCRYPTO_URL}/rest/v1/users/user-otp-auth']
    return await skycrypto(headers=headers, urls=urls)


async def settings(tokens: list):
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }
    urls = [f'https://api.{config.SKYCRYPTO_URL}/rest/v1/settings']
    return await skycrypto(headers=headers, urls=urls)


async def settings_settings_withdraw_commissions(tokens: list):
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }
    urls = [
        f'https://api.{config.SKYCRYPTO_URL}/rest/v1/settings/withdraw_commissions'
    ]
    return await skycrypto(headers=headers, urls=urls)


async def user_messages(tokens: list, with_user: str = 'SUPPORT'):
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }
    urls = [
        f'https://api.{config.SKYCRYPTO_URL}/rest/v1/user-messages?with_user={with_user}'
    ]
    return await skycrypto(headers=headers, urls=urls)


async def lots(
    tokens: list,
    market: bool = False,
    nickname: str = '',
    lot_type: str = 'sell',
    symbol: str = 'usdt',
    broker: str = '',
    currency: str = 'rub',
    limit: int = 15,
    offset: int = 0,
):
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }
    lot_type_list = ('sell', 'buy', 'all')
    urls = f'https://api.{config.SKYCRYPTO_URL}/rest/v1/lots'

    if market and not broker:
        if (
            symbol in config.SKYCRYPTO_SYMBOL_LIST
            and currency in config.SKYCRYPTO_CURRENCY_LIST
            and lot_type in lot_type_list
        ):
            urls = f'{urls}/market?symbol={symbol}&lot_type={lot_type}&currency={currency}&limit={limit}&offset={offset}'
    if market and broker:
        broker = parse.quote(broker)
        if (
            symbol in config.SKYCRYPTO_SYMBOL_LIST
            and currency in config.SKYCRYPTO_CURRENCY_LIST
            and lot_type in lot_type_list
        ):
            urls = f'{urls}/market?symbol={symbol}&lot_type={lot_type}&broker={broker}&currency={currency}&limit={limit}&offset={offset}'
    elif nickname:
        urls = f'{urls}/market?nickname{nickname}&limit={limit}'
    elif not market:
        if lot_type == 'all':
            urls = f'{urls}?currency={currency}'
        else:
            urls = f'{urls}?lot_type={lot_type}&currency={currency}'

    return await skycrypto(headers=headers, urls=[urls])


async def lots_post(
    tokens: list, id_lot=None, rate: float = 0.0, details: str = '-'
):
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    captcha_token = await recaptcha()
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }

    urls = [f'https://api.{config.SKYCRYPTO_URL}/rest/v1/lots/{id_lot}']
    json = {
        'id': id_lot,
        'rate': rate,
        'details': details,
        'captcha_token': captcha_token,
    }

    return await skycrypto(headers=headers, urls=urls, json=json, patch=True)


async def deals_get(
    tokens: list,
    symbol: str = 'usdt',
    offset: int = 0,
    limit: int = 15,
    currency: str = 'rub',
):
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }
    urls = f'https://api.{config.SKYCRYPTO_URL}/rest/v1/deals'
    if (
        symbol in config.SKYCRYPTO_SYMBOL_LIST
        and currency in config.SKYCRYPTO_CURRENCY_LIST
    ):
        urls = f'{urls}?symbol={symbol}&offset={offset}&limit={limit}&currency={currency}'
    return await skycrypto(headers=headers, urls=[urls])


# async def deals_patch(tokens: list, deal_id: str):
#     access_token = tokens[0].get('access')
#     authkey = await codedata(tokens=tokens)
#     headers = {'Accept': 'application/json, text/plain, */*',
#                'AuthKey': authkey,
#                'Authorization': f'Bearer {access_token}',
#                'Content-Type': 'application/json;charset=utf-8',
#                'User-Agent': config.USER_AGENT}
#     json = {'deal_id': deal_id}


async def currencies(tokens: list):
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }
    urls = [f'https://api.{config.SKYCRYPTO_URL}/rest/v1/currencies']
    return await skycrypto(headers=headers, urls=urls)


async def users_wallets(tokens: list):
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }
    urls = [f'https://api.{config.SKYCRYPTO_URL}/rest/v1/users/wallets']
    return await skycrypto(headers=headers, urls=urls)


async def rates(tokens: list):
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }
    urls = [f'https://api.{config.SKYCRYPTO_URL}/rest/v1/rates']
    return await skycrypto(headers=headers, urls=urls)


async def operations(
    tokens: list,
    func: str = 'updates',
    limit: int = 20,
    is_active: bool = True,
):
    access_token = tokens[0].get('access')
    authkey = await codedata(tokens=tokens)
    headers = {
        'AuthKey': authkey,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': config.USER_AGENT,
    }

    json = None
    patch = False
    func_list = ('offset', 'updates', 'total-balance', 'trading-status')
    urls = f'https://api.{config.SKYCRYPTO_URL}/rest/v1/operations'

    if func in func_list:
        if func == 'offset':
            urls = f'{urls}?offset=0&limit={limit}'
        elif func == 'updates':
            urls = f'{urls}/updates?limit={limit}'
        elif func == 'total-balance':
            urls = f'{urls}/total-balance'
        elif func == 'trading-status':
            urls = f'{urls}/trading-status'
            patch = True
            if is_active in [True, False]:
                json = {'is_active': is_active}

    return await skycrypto(
        headers=headers, urls=[urls], json=json, patch=patch
    )


async def page_wallet(
    tokens: list, user_email: str, user_currency: str = 'RUB'
):
    access_token = tokens[0].get('access')
    refresh_token = tokens[0].get('refresh')
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Cookie': f"""sky_refresh_token={refresh_token}; sky_token={access_token}; user_registered=true; user_email={user_email}; user_is_admin=false; user_currency={user_currency}""",
        'User-Agent': config.USER_AGENT,
    }
    urls = [f'https://{config.SKYCRYPTO_URL}/wallet']
    return await skycrypto(headers=headers, urls=urls, result_text=True)


async def result_not_error(result: list):
    # getLogger(name=__name__).debug(msg=result)
    r = result[0]
    # t = [{'status': 'Error', 'description': "{'detail': 'The precondition on the request for the URL failed positive evaluation.', 'status': 412, 'title': 'Precondition Failed', 'type': 'about:blank'}"}]

    if type(r) == list:
        return False, r

    if r.get('status') == 'Error':
        if r.get('description'):
            desc_result = (
                r.get('description').split("',")[0].replace("{'detail': '", '')
            )

            if (
                desc_result
                == 'The precondition on the request for the URL failed positive evaluation.'
            ):
                msg = 'Предварительное условие запроса URL-адреса не прошло положительную оценку.'
            if desc_result == 'Token expired':
                msg = 'Токен не действительный. Необходимо переавторизоваться!'
            else:
                msg = f"""{r.get('description')}"""
        else:
            msg = f'{r}'
        msg = f"""Ошибка:

{msg}

<b>РАЗБИРАЮСЬ ИЗ-ЗА ЧЕГО ПОЯВЛЯЮТСЯ ОШИБКИ
ПОПЫТАЙТЕСЬ ПОВТОРИТЬ КОМАНДУ И ПОЛЬЗОВАТЬСЯ БОТОМ ДАЛЬШЕ!</b>"""
        return True, msg
    return False, r
