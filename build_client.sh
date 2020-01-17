#!/bin/sh
cd src
if [ ! -f testdata/ ]; then
    wget http://csie.ntu.edu.tw/~b08902009/cn_testdata.zip
    unzip cn_testdata.zip; rm -rf cn_testdata.zip
fi
if [ ! -f env/ ]; then
    wget http://csie.ntu.edu.tw/~b08902009/env.zip
    unzip env.zip; rm -rf env.zip
fi
source env/bin/activate
export "CFLAGS=-I/usr/local/include -L/usr/local/lib"
export DYLD_LIBRARY_PATH=/usr/local/opt/openssl/lib:$DYLD_LIBRARY_PATH
python3 client.py
