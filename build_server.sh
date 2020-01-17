#!/bin/sh
cd src
if [ ! -f env/ ]; then
    wget http://csie.ntu.edu.tw/~b08902009/env-server.zip
    unzip env-server.zip; rm -rf env-server.zip
fi
source env-server/bin/activate
python3 server.py
