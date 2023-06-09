from asyncio import create_task, sleep
from logging import getLogger
from random import uniform

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import config
import libs.skycrypto as skycrypto

Logger = getLogger(name=__name__)


def translate_process(deal: str):
    status_dict = {
        'confirmed': '⏳Сделка ожидает оплату',
        'proposed': '🆕 Новая сделка',
        'paid': '⏰ Сделка помечена оплаченной',
        'closed': '✅ Сделка закрыта',
    }
    if deal in status_dict:
        return status_dict[deal]
    return deal


async def process_task(func, time_sleep, *arg):
    await sleep(time_sleep)
    create_task(coro=func(*arg), name=func.__name__)


async def refresh_tokens_coro(state: FSMContext):
    auth_state = await state.get_data()
    if not auth_state.get('loggined'):
        return

    tokens = await skycrypto.auth_refresh(tokens=[auth_state.get('tokens')])

    if tokens[0].get('access') and tokens[0].get('refresh'):
        await state.update_data(tokens=tokens[0])

    a, b = config.SKYCRYPTO_REFRESH_TOKEN
    time_sleep = uniform(a=a * 60, b=b * 60)
    create_task(
        coro=process_task(refresh_tokens_coro, time_sleep, state),
        name='refresh_tokens_coro',
    )


async def lots_answer_message(message: Message, state: FSMContext):
    auth_state = await state.get_data()

    if not auth_state.get('loggined'):
        return

    tokens = auth_state.get('tokens')
    lots_my = auth_state.get('lots_my')
    lots_market_massive = list()

    if not lots_my:
        await state.update_data(lots_my=lots_my)
        return

    if lots_my[0]:
        return

    for lot in lots_my[1]:
        a, b = config.SKYCRYPTO_REFRESH_GET_LOTS_MARKET
        time_sleep = uniform(a=a, b=b)
        await sleep(time_sleep)

        is_active = lot.get('is_active')
        broker = lot.get('broker').get('name')
        symbol = lot.get('symbol')
        currency = lot.get('currency')
        lot_type = lot.get('type')

        if not is_active:
            continue

        lots_market = await skycrypto.lots(
            tokens=[tokens],
            market=True,
            symbol=symbol,
            lot_type=lot_type,
            currency=currency,
            broker=broker,
            limit=15,
            offset=0,
        )
        lots_market = lots_market[0]
        if lots_market:
            if type(lots_market) == dict:
                continue
            for lot_market in lots_market:
                if type(lot_market) == str:
                    continue
                lots_market_massive.append(lot_market)

    spred = 1.0
    limit_to = 15000  # auth_state.get('limit_to_buy')
    lots_my = auth_state.get('lots_my')
    lots_update = list()
    brokers_added = list()
    rate_market_dict = dict()

    for lot in lots_my[1]:
        if not lot:
            continue
        broker_id = lot.get('broker').get('id')
        bank = lot.get('broker').get('name')
        id_lot = lot.get('id')
        symbol = lot.get('symbol')
        rate = lot.get('rate')
        typ = lot.get('type')
        # limit_to = lot.get('limit_to')
        is_active = lot.get('is_active')

        for lot_m in lots_market_massive:
            bank_market = lot_m.get('broker').get('name')
            id_lot_market = lot_m.get('id')
            symbol_market = lot_m.get('symbol')
            rate_market = lot_m.get('rate')
            type_market = lot_m.get('type')
            limit_to_market = lot_m.get('limit_to')
            verified_market = lot_m.get('user').get('verified')

            if not bank == bank_market:
                continue

            if (
                is_active
                and verified_market
                and id_lot != id_lot_market
                and symbol == symbol_market
                and type_market == typ
                and limit_to_market >= limit_to
                and rate != rate_market
            ):
                if symbol not in rate_market_dict:
                    rate_market_dict[symbol] = dict()
                if bank not in rate_market_dict[symbol]:
                    rate_market_dict[symbol][bank] = list()

                rate_market_dict[symbol][bank].append(rate_market)

                if broker_id in brokers_added:
                    continue

                lots_update.append(lot)
                brokers_added.append(broker_id)

    print(rate_market_dict)
    # print(lots_update)

    if lots_update and rate_market_dict:
        tokens = auth_state.get('tokens')

        for lot in lots_update:
            a, b = config.SKYCRYPTO_REFRESH_SET_DEALS
            time_sleep = uniform(a=a, b=b)

            bank = lot.get('broker').get('name')
            id_lot = lot.get('id')
            rate = lot.get('rate')
            details = lot.get('details')
            symbol = lot.get('symbol')
            currency = lot.get('currency')

            if symbol == 'usdt':
                rate_buy = auth_state.get('rate_buy_usdt')
                rate_buy_plus_spread = rate_buy + (rate_buy * spred / 100)
            elif symbol == 'btc':
                rate_buy = auth_state.get('rate_buy_btc')
                rate_buy_plus_spread = rate_buy + (rate_buy * spred / 100)
            elif symbol == 'eth':
                rate_buy = auth_state.get('rate_buy_eth')
                rate_buy_plus_spread = rate_buy + (rate_buy * spred / 100)
            else:
                raise 'Нет такой криптовалюты'

            if symbol in rate_market_dict:
                if bank not in rate_market_dict[symbol]:
                    continue
            else:
                continue

            if rate_buy_plus_spread <= min(rate_market_dict[symbol][bank]):
                rate_new = min(rate_market_dict[symbol][bank])
            else:
                rate_new = rate_buy_plus_spread

            result = await skycrypto.lots_post(
                tokens=[tokens], id_lot=id_lot, rate=rate_new, details=details
            )
            result = result[0]

            if result.get('success'):
                result_msg = result.get('success').replace(
                    'lot updated', '♻️ Лот обновлен'
                )
                bank = '{bank} {color}'.format(
                    color=config.SKYCRYPTO_BANKS_DICT.get(bank), bank=bank
                )
                msg = """{result} /l{id_lot}
Направление: {symbol} → {bank}
Изменение: {rate} → {rate_new} {currency}
Предельная цена: купил {rate_buy} + {spred} % = {rate_buy_plus_spread:.2f}
""".format(
                    result=result_msg,
                    id_lot=id_lot,
                    bank=bank,
                    symbol=symbol.upper(),
                    rate=rate,
                    rate_new=rate_new,
                    rate_buy=rate_buy,
                    spred=spred,
                    rate_buy_plus_spread=rate_buy_plus_spread,
                    currency=currency.upper(),
                )
                await message.answer(text=msg)
                await sleep(time_sleep)


async def lots_coro(message: Message, state: FSMContext):
    auth_state = await state.get_data()
    tokens = auth_state.get('tokens')

    if not auth_state.get('loggined'):
        return
    lots_my = await skycrypto.lots(
        tokens=[tokens], lot_type='sell', currency='rub'
    )
    lots_my = await skycrypto.result_not_error(result=lots_my)
    if lots_my[0]:
        lots_my = auth_state.get('lots_my')
        await state.update_data(lots_my=lots_my)
    else:
        await state.update_data(lots_my=lots_my)

    # Logger.debug(msg=f'lots_my:\n{lots_my}')
    await lots_answer_message(message=message, state=state)

    time_sleep = config.SKYCRYPTO_REFRESH_LOTS
    create_task(
        coro=process_task(lots_coro, time_sleep, state), name='lots_coro'
    )


async def deals_answer_message(
    deals_source, message: Message, state: FSMContext
):
    auth_state = await state.get_data()

    if not auth_state.get('loggined'):
        return

    deals_last = auth_state.get('deals_last')

    if not deals_last:
        await state.update_data(deals_last=deals_source)
        return

    if deals_source[0] or deals_last[0]:
        return

    deals_change = list()
    id_list_last = list()

    for deal_new in deals_source[1]:
        id_new = deal_new.get('id')
        status_new = deal_new.get('state')

        for deal_last in deals_last[1]:
            id_last = deal_last.get('id')
            id_list_last.append(id_last)
            state_last = deal_last.get('state')

            if id_last == id_new and state_last != status_new:
                deals_change.append(deal_new)

    print(deals_change)
    msg = ''

    if deals_change:
        for deal in deals_change:
            bank = deal.get('broker').get('name')
            bank = '{bank} {color}'.format(
                color=config.SKYCRYPTO_BANKS_DICT.get(bank), bank=bank
            )

            msg = """{stat} [{bank}]
ID: /d{i}
Сумма ({currency}): {amount_cur}
Сумма ({symbol}): {amount}
Отправитель: /u{opponent}""".format(
                stat=translate_process(deal.get('state')),
                bank=bank,
                i=deal.get('id'),
                currency=deal.get('currency').upper(),
                amount_cur=deal.get('amount_currency'),
                symbol=deal.get('symbol').upper(),
                amount=deal.get('amount'),
                opponent=deal.get('opponent'),
            )
            await message.answer(text=msg)
            await sleep(0.5)

    await state.update_data(deals_last=deals_source)


async def deals_coro(message: Message, state: FSMContext):
    auth_state = await state.get_data()
    if not auth_state.get('loggined'):
        return
    deals_source = await skycrypto.deals_get(
        tokens=[auth_state.get('tokens')],
        symbol='usdt',
        offset=0,
        limit=15,
        currency='rub',
    )
    deals_source = await skycrypto.result_not_error(result=deals_source)
    if deals_source[0]:
        deals_source = auth_state.get('deals_last')
        await state.update_data(deals_last=deals_source)
    else:
        await state.update_data(deals_last=deals_source)

    # Logger.debug(msg=f'deals_last:\n{deals_source}')
    await deals_answer_message(
        deals_source=deals_source, message=message, state=state
    )
    time_sleep = config.SKYCRYPTO_REFRESH_DEALS
    create_task(
        coro=process_task(deals_coro, time_sleep, state), name='deals_coro'
    )


async def operations_coro(state: FSMContext):
    auth_state = await state.get_data()
    if not auth_state.get('loggined'):
        return
    operations_last = await skycrypto.operations(
        tokens=[auth_state.get('tokens')], func='updates', limit=20
    )
    operations_last = await skycrypto.result_not_error(result=operations_last)
    if operations_last[0]:
        operations_last = auth_state.get('operations_last')
        await state.update_data(operations_last=operations_last)
    else:
        await state.update_data(operations_last=operations_last)

    # Logger.debug(msg=f'operations_last:\n{operations_last}')
    time_sleep = config.SKYCRYPTO_REFRESH_OPERATIONS
    create_task(
        coro=process_task(operations_coro, time_sleep, state),
        name='operations_coro',
    )


async def rates_coro(state: FSMContext):
    auth_state = await state.get_data()
    if not auth_state.get('loggined'):
        return
    rates_last = await skycrypto.rates(tokens=[auth_state.get('tokens')])
    rates_last = await skycrypto.result_not_error(result=rates_last)
    if rates_last[0]:
        rates_last = auth_state.get('rates_last')
        await state.update_data(rates_last=rates_last)
    else:
        await state.update_data(rates_last=rates_last)

    # Logger.debug(msg=f'rates_last:\n{rates_last}')
    time_sleep = config.SKYCRYPTO_REFRESH_RATES
    create_task(
        coro=process_task(rates_coro, time_sleep, state), name='rates_coro'
    )
