#!/usr/bin/python
import os
import sys
import json
import time
import signal
import socket
import getpass
import urllib.request

from inc.cryptography import *

server_ip = '127.0.0.1'
port = 12788
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
        encrypt_send( (current_key + ' logout'), u_publicKey, client)
        encrypt_send( (current_key + ' exit'), u_publicKey, client)
        client.close()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


#key generation
me_privateKey, me_publicKey = key_generation()
#public key exchange
u_public_string = ( client.recv( max_length))
u_publicKey = RSA.importKey( u_public_string)

client.send( me_publicKey.exportKey())

while True:
    
    print('>> ', end='')
    msg = input('')

    if msg.split()[0] == 'login':
        print('Username:', end='')
        msg = msg + ' ' + input('')
        msg = msg + ' ' + getpass.getpass(prompt='password:')

    network_availability = False

    while network_availability == False:
        try:
            #urllib.request.urlopen('https://google.com')
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
            print('Usage: [get] [text or file] [person] [content]')
            continue


    if msg.split()[0] == 'chg':
        if len(msg.split()) != 2:
            print('Usage: [chg] [account]')
            sendable = False
            continue
        else:
            msg = msg + ' ' + getpass.getpass(prompt='password:')
            confirmaion = getpass.getpass(prompt='password confirm:')
            if msg.split()[4] != confirmation:
                print('ERROR: Your password and confirmation password do not match. Request has been ignored.')
                sendable = False
                continue

    if sendable:
        encrypt_send( (current_key + ' ' + msg), u_publicKey, client)

    if msg.split()[0] == 'exit':
        print('bye')
        break


    elif msg.split()[0] == 'logout':
        current_key = 'none'

    elif msg.split()[0] == 'send' and (len(msg.split()) >= 2):
        if msg.split()[1] == 'file':
            for ic in range(3, len(msg.split()), 1):
                if os.path.isfile(msg.split()[ic]):
                    buf = receive_decode( me_privateKey, client, max_length)
                    bound = int(os.path.getsize(msg.split()[ic]))
                    encrypt_send( ('ok' + str(bound)), u_publicKey, client)
                    with open(msg.split()[ic], 'rb') as fp:
                        buf = receive_decode( me_privateKey, client, max_length)
                        if buf == 'ok':
                            buf = fp.read(max_length)
                            encrypte_send( buf, u_publicKey, client)
                            for j in range(bound):
                                tmp = receive_decode( me_privateKey, client, max_length)
                                is_end  = False
                                for k in tmp.split():
                                    print(k)
                                    if int(k) == bound:
                                        is_end = True
                                        break
                                if is_end:
                                    break
                                buf = fp.read(max_length)
                                encrypte_send( buf, u_publicKey, client)
                        fp.close()
                    buf = receive_decode( me_privateKey, client, max_length)
                    if ic != len(msg.split())-1:
                        encrypte_send( ('next'), u_publicKey, client)
                    print(buf)
                else:
                    if sendable:
                        buf = receive_decode( me_privateKey, client, max_length)
                        encrypte_send( ('error'), u_publicKey, client)
                    print(msg.split()[ic], ' not exists')
            continue

    elif msg.split()[0] == 'get' and (len(msg.split()) >= 2):
        if msg.split()[1] == 'file':
            for ic in range(3, len(msg.split()), 1):
                buf = receive_decode( me_privateKey, client, max_length)
                if buf.split()[0] == 'ok':
                    save_path = msg.split()[ic]
                    for index in range(1, 65536, 1):
                        if not os.path.isfile(save_path):
                            break;
                        save_path = msg.split()[ic].split('.')[0] \
                                + '(' + str(index) + ').' + msg.split()[ic].split('.')[1]
                        
                    encrypte_send( ('ok'), u_publicKey, client)
                    bound = int(buf.split()[1])
                    size_sum = 0
                    with open(save_path, 'wb') as fp:
                        buf = receive_decode( me_privateKey, client, max_length)
                        size_sum += len(buf)
                        while True:
                            fp.write(buf)
                            encrypte_send( (str(size_sum) + ' ' ), u_publicKey, client)
                            if size_sum == bound:
                                break
                            buf = receive_decode( me_privateKey, client, max_length)
                            size_sum += len(buf)
                        fp.close()
                buf = receive_decode( me_privateKey, client, max_length)
                if ic != len(msg.split())-1:
                    encrypte_send( ('next'), u_publicKey, client)
                print(buf)
            continue

    buf = receive_decode( me_privateKey, client, max_length)

    if msg.split()[0] == 'login' and len(buf) == 32:
        current_key = buf

    print(buf)

    

client.close()
