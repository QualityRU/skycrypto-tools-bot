from aiogram import Dispatcher

from .app import router as app
from .deals import router as deals
from .help import router as help
from .info import router as info
from .login import router as login
from .relogin import router as relogin
from .settings import router as settings
from .spam import router as spam
from .stakan import router as stakan
from .start import router as start


def include_router(dp: Dispatcher):
    dp.include_router(router=start)
    dp.include_router(router=deals)
    dp.include_router(router=help)
    dp.include_router(router=info)
    dp.include_router(router=relogin)
    dp.include_router(router=settings)
    dp.include_router(router=app)
    dp.include_router(router=spam)
    dp.include_router(router=stakan)

    # FSM в конец
    dp.include_router(router=login)
