**pip install aiogram -U --pre**
**pip install aiohttp[speedups] coloredlogs sqlalchemy[asyncio] python-dotenv ujson uvloop** chardet quickjs aiologger nodejs-bin

переименовать **config.example.py** в **config.py** и заполнить его

сохранить все пакеты pip в requirements.txt
**python -m pip freeze > requirements.txt**

удалить все пакеты pip, которые менялись в requirements.txt
**python -m pip uninstall -r requirements.txt**

обновить все пакеты
**sudo /home/bot/venv/bin/pip3 install -U $(/home/bot/venv/bin/pip3 freeze | cut -d '=' -f 1)**
**for i in $(/home/bot/venv/bin/pip3 list -o | awk 'NR > 2 {print $1}'); do /home/bot/venv/bin/pip3 install -U $i; done**