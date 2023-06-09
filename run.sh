#!/bin/bash
put=/home/$USER/skytoolsbot

screen -LRR -dmS skycrypto -c /etc/screenrc $put/venv/bin/python $put/main.py
echo "Sky Tools Bot запущен в фоне!"