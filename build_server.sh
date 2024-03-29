#!/bin/sh
cd src
if [ ! -d env-server/ ]; then
    wget http://csie.ntu.edu.tw/~b08902009/env-server.zip || curl -OL http://csie.ntu.edu.tw/~b08902009/env-server.zip
    unzip env-server.zip; rm -rf env-server.zip
    source env-server/bin/activate
else
    source env-server/bin/activate
fi

python3 server.py
