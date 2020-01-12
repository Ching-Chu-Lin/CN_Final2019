import os
import sys
import json
import socket
import signal
import datetime
import shlex

from inc.account import create_user
from inc.account import change_password
from inc.account import log_in
from inc.account import log_out
from inc.message_send import send_text
from inc.message_send import send_file
from inc.message_get import show_all
from inc.message_get import get_text
from inc.message_get import get_file
from inc.super_user import sudo

listen_ip = '0.0.0.0'
port = 12789
max_length = 4096
max_client = 64
clien_cnt = 0

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
        while True:

            buf = (conn.recv(max_length)).decode()

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
                    msg = '[reg] [account] [password]'
                else:
                    msg = create_user(buf.split()[2], buf.split()[3])
            elif buf.split()[1] == 'chg':
                if len(buf.split()) < 5:
                    msg = '[chg] [account] [pasword] [new password]'
                else:
                    msg = change_password(buf.split()[2], buf.split()[3], buf.split()[4])
            elif buf.split()[1] == 'login':
                if len(buf.split()) < 4:
                    msg = '[login] [account] [password]'
                else:
                    msg = log_in(buf.split()[2], buf.split()[3])
            elif buf.split()[1] == 'logout':
                msg = log_out(buf.split()[0])
            elif buf.split()[1] == 'show':
                msg = show_all(buf.split()[0])
            elif buf.split()[1] == 'send':
                if len(buf.split()) < 5 or (buf.split()[2] != 'text' and buf.split()[2] != 'file'):
                    msg = '[send] [text] [receiver] [content]\n[send] [file] [receiver] [content1] [content2]...'
                else:
                    if buf.split()[2] == 'text':
                        msg = send_text(buf.split()[0], buf.split()[3], str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), shlex.split(buf)[4])
                    else:
                        for ic in range(4, len(shlex.split(buf)), 1):
                            conn.send(('ok').encode())
                            tmp = (conn.recv(max_length)).decode()
                            if tmp.split()[0] == 'ok':
                                msg = send_file(buf.split()[0], buf.split()[3], str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), shlex.split(buf)[ic], conn, int(tmp.split()[1]))
                                print('msg:\n', msg)
                                conn.send(msg.encode())
                                if ic != len(shlex.split(buf))-1:
                                    tmp = (conn.recv(max_length)).decode()
                        continue
            elif buf.split()[1] == 'get':
                if len(buf.split()) < 5:
                    msg = '[get] [text or file] [person] [ret_type]'
                else:
                    if buf.split()[2] == 'text':
                        msg = get_text(buf.split()[0], buf.split()[3], buf.split()[4])
                    else:
                        for ic in range(4, len(buf.split()), 1):
                            msg = get_file(buf.split()[0], buf.split()[3], buf.split()[ic], conn)
                            print('msg:\n', msg)
                            conn.send(msg.encode())
                            if ic != len(buf.split())-1:
                                tmp = (conn.recv(max_length)).decode()
                        continue
            else:
                msg = 'undefined command!'

            print('msg:\n', msg)
            conn.send(msg.encode())
    conn.close()
