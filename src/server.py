import os
import sys
import json
import socket
import signal
import datetime
import shlex
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from inc.account import create_user
from inc.account import change_password
from inc.account import log_in
from inc.account import log_out
from inc.account import chgcolor
from inc.message_send import send_text
from inc.message_send import send_file
from inc.message_get import show_all
from inc.message_get import get_text
from inc.message_get import get_file
from inc.super_user import sudo
from inc.cryptography import *

listen_ip = '0.0.0.0'
port = 12789
max_length = 4096
max_client = 64
clien_cnt = 0

#create socket
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((listen_ip, port))
server.listen(max_client)

def signal_handler(sig, frame):
        server.close()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

while True:

    conn, addr = server.accept()
    clien_cnt += 1
    print(conn, addr)

    if os.fork() == 0:

        #key generation
        me_privateKey, me_publicKey = asymmetric_key_generation()
        conn.send( me_publicKey.exportKey())
        #asymmetric key exchange
        #save key class
        data = conn.recv( max_length)
        cipher = PKCS1_OAEP.new( me_privateKey)
        symmetricKey = cipher.decrypt( data)
        print('sym at server:', symmetricKey)



        while True:

            buf = receive_decode( symmetricKey, conn, max_length)

            print('-==================================')
            print('-', buf, '-')

            if len(buf.split()) < 2:
                continue;
            if buf.split()[1] == 'exit':
                tmp = log_out(buf.split()[0])
                clien_cnt -= 1
                break

            if buf.split()[1] == 'sudo':
                msg = sudo(buf)
            elif buf.split()[1] == 'reg':
                if len(buf.split()) < 4:
                    msg = 'Usage: [reg] [account] [password]'
                else:
                    msg = create_user(buf.split()[2], buf.split()[3])
            elif buf.split()[1] == 'chg':
                if len(buf.split()) < 5: 
                    msg = 'Usage: [chg] [account] [pasword] [new password] [new password confirm]'
                else:
                    msg = change_password(buf.split()[2], buf.split()[3], buf.split()[4])
            elif buf.split()[1] == 'login':
                if len(buf.split()) < 4:
                    msg = 'Usage: [login] [account] [password]'
                else:
                    msg = log_in(buf.split()[2], buf.split()[3])
            elif buf.split()[1] == 'logout':
                msg = log_out(buf.split()[0])
            elif buf.split()[1] == 'show':
                msg = show_all(buf.split()[0])
            elif buf.split()[1] == 'send':
                if len(buf.split()) < 5 or (buf.split()[2] != 'text' and buf.split()[2] != 'file'):
                    msg = 'Usage: [send] [text] [receiver] [content]\n[send] [file] [receiver] [content1] [content2]...'
                else:
                    if buf.split()[2] == 'text':
                        msg = send_text(buf.split()[0], buf.split()[3], str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), shlex.split(buf)[4])
                    else:
                        for ic in range(4, len(shlex.split(buf)), 1):
                            encrypt_send( ('ok'), symmetricKey, conn)
                            tmp = ( receive_decode( symmetricKey, conn, max_length))
                            if tmp.split()[0] == 'ok':
                                msg = send_file(buf.split()[0], buf.split()[3], str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), shlex.split(buf)[ic], conn, int(tmp.split()[1]), symmetricKey)
                                print('msg:\n', msg)
                                encrypt_send( msg, symmetricKey, conn)
                                if ic != len(shlex.split(buf))-1:
                                    tmp = ( receive_decode( symmetricKey, conn, max_length))
                        continue
            elif buf.split()[1] == 'get':
                if len(buf.split()) < 5:
                    msg = 'Usage: [get] [text or file] [person] [ret_type]'
                else:
                    if buf.split()[2] == 'text':
                        msg = get_text(buf.split()[0], buf.split()[3], buf.split()[4])
                    else:
                        for ic in range(4, len(buf.split()), 1):
                            msg = get_file(buf.split()[0], buf.split()[3], buf.split()[ic], conn, symmetricKey)
                            print('msg:\n', msg)
                            encrypt_send( msg, symmetricKey, conn)
                            if ic != len(buf.split())-1:
                                tmp = ( receive_decode( symmetricKey, conn, max_length))
                        continue
            elif buf.split()[1] == 'color':
                if len(buf.split()) < 3:
                    msg = 'Usage: [color] [grey/red/green/yellow/blue/magenta/cyan/white]'
                else:
                    msg = chgcolor(buf.split()[0],buf.split()[2])
            else:
                msg = 'Error: undefined command!'

            print('msg:\n', msg)
            encrypt_send( msg, symmetricKey, conn)
    conn.close()
