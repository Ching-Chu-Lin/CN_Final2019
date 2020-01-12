#!/usr/bin/python
import os
import sys
import json
import time
import signal
import socket
import getpass
import urllib.request

server_ip = '140.112.30.125'
port = 12789
max_length = 4096
wait_second = 10

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    client.connect((server_ip, port))
except:
    print('network is unreachable')
    exit(0)

current_key = 'none'

def signal_handler(sig, frame):
        client.send((current_key + ' logout').encode())
        client.send((current_key + ' exit').encode())
        client.close()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

while True:
    
    print('>> ', end='')
    msg = input('')

    if msg.split()[0] == 'login':
        print('Username:', end=' ')
        msg = msg + ' ' + input('')
        msg = msg + ' ' + getpass.getpass(prompt='password')

    network_availability = False

    while network_availability == False:
        try:
            urllib.request.urlopen('https://google.com')
            network_availability = True
        except urllib.request.URLError as err:
            print('network is unreachable...')
            network_availability = False
            time.sleep(wait_second)
            print('......')

    sendable = True
    if msg == '':
        continue

    if msg.split()[0] == 'send' and len(msg.split()) >= 4:
        if msg.split()[1] == 'file':
            sendable = False
            for ic in range(3, len(msg.split()), 1):
                if os.path.isfile(msg.split()[ic]):
                    sendable = True

    if msg.split()[0] == 'get':
        if len(msg.split()) < 4:
            print('[get] [text or file] [person] [content]')
            continue

    if sendable:
        client.send((current_key + ' ' + msg).encode())

    if msg.split()[0] == 'exit':
        print('bye')
        break

    elif msg.split()[0] == 'logout':
        current_key = 'none'

    elif msg.split()[0] == 'send' and (len(msg.split()) >= 2):
        if msg.split()[1] == 'file':
            for ic in range(3, len(msg.split()), 1):
                if os.path.isfile(msg.split()[ic]):
                    buf = (client.recv(max_length)).decode()
                    bound = int(os.path.getsize(msg.split()[ic]))
                    client.send(('ok ' + str(bound)).encode())
                    with open(msg.split()[ic], 'rb') as fp:
                        buf = (client.recv(max_length)).decode()
                        if buf == 'ok':
                            buf = fp.read(max_length)
                            client.send(buf)
                            for j in range(bound):
                                tmp = (client.recv(max_length)).decode()
                                is_end  = False
                                for k in tmp.split():
                                    print(k)
                                    if int(k) == bound:
                                        is_end = True
                                        break
                                if is_end:
                                    break
                                buf = fp.read(max_length)
                                client.send(buf)
                        fp.close()
                    buf = (client.recv(max_length)).decode()
                    if ic != len(msg.split())-1:
                        client.send(('next').encode())
                    print(buf)
                else:
                    if sendable:
                        buf = (client.recv(max_length)).decode()
                        client.send(('error').encode())
                    print(msg.split()[ic], ' not exists')
            continue

    elif msg.split()[0] == 'get' and (len(msg.split()) >= 2):
        if msg.split()[1] == 'file':
            for ic in range(3, len(msg.split()), 1):
                buf = (client.recv(max_length)).decode()
                if buf.split()[0] == 'ok':
                    save_path = msg.split()[ic]
                    for index in range(1, 65536, 1):
                        if not os.path.isfile(save_path):
                            break;
                        save_path = msg.split()[ic].split('.')[0] \
                                + '(' + str(index) + ').' + msg.split()[ic].split('.')[1]
                        
                    client.send(('ok').encode())
                    bound = int(buf.split()[1])
                    size_sum = 0
                    with open(save_path, 'wb') as fp:
                        buf = client.recv(max_length)
                        size_sum += len(buf)
                        while True:
                            fp.write(buf)
                            client.send((str(size_sum) + ' ').encode())
                            if size_sum == bound:
                                break
                            buf = client.recv(max_length)
                            size_sum += len(buf)
                        fp.close()
                buf = (client.recv(max_length)).decode()
                if ic != len(msg.split())-1:
                    client.send(('next').encode())
                print(buf)
            continue

    buf = (client.recv(max_length)).decode()

    if msg.split()[0] == 'login' and len(buf) == 32:
        current_key = buf

    print(buf)

    

client.close()
