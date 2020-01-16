#!/usr/bin/python
import os
import sys
import json
import time
import signal
import socket
import getpass
import urllib.request
from prettytable import PrettyTable
from Crypto.Cipher import PKCS1_OAEP
from cryptography.fernet import Fernet
from Crypto.PublicKey import RSA

from inc.cryptography import *

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
        encrypt_send( (current_key + ' logout'), symmetricKey, client)
        encrypt_send( (current_key + ' exit'), symmetricKey, client)
        client.close()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


#asymmetric key exchange
#get your public key
u_publicKey = RSA.importKey( client.recv( max_length))
#save key class
#send fernet key
symmetricKey = Fernet.generate_key()
cipher = PKCS1_OAEP.new( u_publicKey)
encrypted = cipher.encrypt( symmetricKey)
client.send( encrypted)
print('sym at client:', symmetricKey)

while True:

    print('>> ', end='')
    msg = input('')

    if msg.split()[0] == 'reg':
        print('Register\nUsername:', end='')
        msg = msg + ' ' + input('')
        msg = msg + ' ' + getpass.getpass(prompt='password:')

    if msg.split()[0] == 'login':
        print('Login\nUsername:', end='')
        msg = msg + ' ' + input('')
        msg = msg + ' ' + getpass.getpass(prompt='password:')

    if msg.split()[0] == 'chg':
        if len(msg.split()) != 2:
            print('Usage: [chg] [account]')
            sendable = False
            continue
        else:
            print('Change Password\n')
            msg = msg + ' ' + getpass.getpass(prompt='password:')

            msg = msg + ' ' + getpass.getpass(prompt='new password:')
            new_confirmation = getpass.getpass(prompt='new password confirm:')
            if msg.split()[3] != new_confirmation:
                print('ERROR: New password and confirmation password do not match. Request has been ignored.')
                sendable = False
                continue

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
            print('Usage: [get] [text or file] [person] [content]')
            continue

    if sendable:
        encrypt_send( (current_key + ' ' + msg), symmetricKey, client)

    if msg.split()[0] == 'exit':
        print('bye')
        break


    elif msg.split()[0] == 'logout':
        current_key = 'none'

    elif msg.split()[0] == 'send' and (len(msg.split()) >= 2):
        if msg.split()[1] == 'file':
            for ic in range(3, len(msg.split()), 1):
                if os.path.isfile(msg.split()[ic]):
                    buf = receive_decode( symmetricKey, client, max_length)
                    bound = int(os.path.getsize(msg.split()[ic]))
                    encrypt_send( ('ok ' + str(bound)), symmetricKey, client)
                    with open(msg.split()[ic], 'rb') as fp:
                        buf = receive_decode( symmetricKey, client, max_length)
                        if buf == 'ok':
                            buf = fp.read(max_length)
                            client.send(buf)
                            #encrypt_send_byte( buf, symmetricKey, client)
                            for j in range(bound):
                                tmp = receive_decode( symmetricKey, client, max_length)
                                is_end  = False
                                for k in tmp.split():
                                    if int(k) == bound:
                                        is_end = True
                                        break
                                if is_end:
                                    break
                                buf = fp.read(max_length)
                                client.send(buf)
                                #encrypt_send_byte( buf, symmetricKey, client)
                        fp.close()
                    buf = receive_decode( symmetricKey, client, max_length)
                    if ic != len(msg.split())-1:
                        encrypt_send( ('next'), symmetricKey, client)
                    print(buf)
                else:
                    if sendable:
                        buf = receive_decode( symmetricKey, client, max_length)
                        encrypt_send( ('error'), symmetricKey, client)
                    print(msg.split()[ic], ' not exists')
            continue

    elif msg.split()[0] == 'get' and (len(msg.split()) >= 2):
        if msg.split()[1] == 'file':
            for ic in range(3, len(msg.split()), 1):
                buf = receive_decode( symmetricKey, client, max_length)
                if buf.split()[0] == 'ok':
                    save_path = msg.split()[ic]
                    for index in range(1, 65536, 1):
                        if not os.path.isfile(save_path):
                            break;
                        save_path = msg.split()[ic].split('.')[0] \
                                + '_' + str(index) + '.' + msg.split()[ic].split('.')[1]

                    encrypt_send( ('ok'), symmetricKey, client)
                    bound = int(buf.split()[1])
                    size_sum = 0
                    with open(save_path, 'wb') as fp:
                        buf = client.recv(max_length)
                        #buf = receive_decode_byte( symmetricKey, client, max_length)
                        size_sum += len(buf)
                        while True:
                            fp.write(buf)
                            encrypt_send( (str(size_sum) + ' ' ), symmetricKey, client)
                            if size_sum == bound:
                                break
                            buf = client.recv(max_length)
                            #buf = receive_decode_byte( symmetricKey, client, max_length)
                            size_sum += len(buf)
                        fp.close()
                buf = receive_decode( symmetricKey, client, max_length)
                if ic != len(msg.split())-1:
                    encrypt_send( ('next'), symmetricKey, client)
                print(buf)
            continue

    buf = receive_decode( symmetricKey, client, max_length)

    if msg.split()[0] == 'login' and len(buf) == 32:
        current_key = buf

    print(buf)



client.close()
