#!/bin/bash
put=/home/$USER/skycrypto-tools-bot

screen -LRR -dmS skycrypto -c /etc/screenrc $put/venv/bin/python $put/main.py
echo "Skycrypto Tools Bot запущен в фоне!"