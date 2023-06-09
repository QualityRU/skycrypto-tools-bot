from logging import getLogger

from aiogram.fsm.context import FSMContext
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    select,
)

import config

Logger = getLogger(name=__name__)
create_auth = create_engine(f'sqlite:////{config.DB_AUTH}')
meta = MetaData()

auth = Table(
    'auth',
    meta,
    Column('id', Integer, primary_key=True),
    Column('telegram_id', Integer, nullable=False),
    Column('telegram_username', String),
    Column('registered', DateTime),
    Column('email', String, nullable=False),
    Column('password', String, nullable=False),
    Column('nickname', String, nullable=False),
    Column('gaf', Boolean),
)
meta.create_all(create_auth)


async def auth_set(state: FSMContext):
    auth_data = await state.get_data()

    conn = create_auth.connect()
    # result = conn.execute(ins)
    ins = conn.execute(auth.insert(), [auth_data])
    conn.close()


async def auth_get(telegram_id):
    conn = create_auth.connect()
    s = select(auth)
    result = conn.execute(s)

    for row in result:
        row = dict(row)
        if telegram_id == row.get('telegram_id'):
            conn.close()
            return row
    conn.close()
    return None
