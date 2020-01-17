#!/usr/bin/python
import os
import sys
import json
import time
import signal
import socket
import getpass
import urllib.request
from termcolor import colored, cprint
from prettytable import PrettyTable
from Crypto.Cipher import PKCS1_OAEP
from cryptography.fernet import Fernet
from Crypto.PublicKey import RSA

from inc.cryptography import *

server_ip = '140.112.30.125'
port = 12789
max_length = 4096
wait_second = 10
current_key = 'none'
current_color='white'

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    client.connect((server_ip, port))
except:
    cprint('network is unreachable', current_color)
    exit(0)

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
#print('sym at client:', symmetricKey)

while True:

    cprint('>> ', current_color, end='')
    msg = input('')

    if msg == '':
        continue

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
            cprint('network is unreachable...', current_color)
            network_availability = False
            time.sleep(wait_second)
            cprint('......', current_color)

    sendable = True

    if msg.split()[0] == 'send' and len(msg.split()) >= 4:
        if msg.split()[1] == 'file':
            sendable = False
            for ic in range(3, len(msg.split()), 1):
                if os.path.isfile(msg.split()[ic]):
                    sendable = True

    if current_key == 'none' and (msg.split()[0] != 'login' \
                                  and msg.split()[0] != 'exit' \
                                  and msg.split()[0] != 'reg' \
                                  and msg.split()[0] != 'chg'\
                                  ):
        cprint('you have not logged in!', current_color)
        continue

    validcolor=0
    colorlist=['grey','red','green','yellow','blue','magenta','cyan','white']
    if msg.split()[0] =='color':
        if len(msg.split())< 2:
            sendable = False
            cprint('Usage: [color] [choice]', current_color)
            continue
        for choice in colorlist:
            if msg.split()[1]==choice:
                validcolor=1
                current_color=msg.split()[1]
                break
        if validcolor==0:
            cprint('invalid color!!', current_color)
            continue

    if msg.split()[0] == 'get':
        if len(msg.split()) < 4:
            cprint('Usage: [get] [text or file] [person] [content]',current_color)
            continue

    if sendable:
        encrypt_send( (current_key + ' ' + msg), symmetricKey, client)

    if msg.split()[0] == 'exit':
        cprint('bye', current_color)
        break


    elif msg.split()[0] == 'logout':
        current_key = 'none'
        current_color='white'

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
                            client.sendall(buf)
                            #encrypt_send_byte( buf, symmetricKey, client)
                            for j in range(bound):
                                tmp = receive_decode( symmetricKey, client, max_length)
                                is_end  = False
                                for k in tmp.split():
                                    if k == 'done':
                                        buf = 'done'
                                        is_end = True
                                        break
                                    if int(k) == bound:
                                        buf = receive_decode( symmetricKey, client, max_length)
                                        is_end = True
                                        break
                                if is_end:
                                    break
                                buf = fp.read(max_length)
                                client.sendall(buf)
                                #encrypt_send_byte( buf, symmetricKey, client)
                        else:
                            buf = receive_decode( symmetricKey, client, max_length)
                        fp.close()
                    if ic != len(msg.split())-1:
                        encrypt_send( ('next'), symmetricKey, client)
                    cprint(buf,current_color)
                else:
                    if sendable:
                        buf = receive_decode( symmetricKey, client, max_length)
                        encrypt_send( ('error'), symmetricKey, client)
                    cprint(msg.split()[ic]+' not exists',current_color)
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
                cprint(buf,current_color)
            continue
    if msg.split()[0] == 'login':
        buf = receive_decode( symmetricKey, client, max_length)
        current_color =buf.split('/')[1]
        buf=buf.split('/')[0]

    else:
        buf = receive_decode( symmetricKey, client, max_length)

    if msg.split()[0] == 'login' and len(buf) == 32:
        current_key = buf

    cprint(buf,current_color)

client.close()
