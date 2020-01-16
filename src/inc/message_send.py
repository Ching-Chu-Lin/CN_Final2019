import os
import sys
import json
import shutil

from inc.cryptography import *

def gen_path(a, b, c):
    buf = os.getcwd() + '/data/' + a + '/' + b + c
    return buf

def send_text(key, receiver, timestamp, content):

    max_length = 4096
    current_account = ''

    authorized = False
    receiver_found = False
    with open(os.getcwd() + '/data/user.json', 'r') as fp:
        data = json.load(fp)
        for tmp in data['user']:
            if tmp['key'] == key:
                current_account = tmp['account']
                authorized = True
            if tmp['account'] == receiver:
                receiver_found = True
        fp.close()


    if authorized and receiver_found:

        if not os.path.isfile(gen_path(receiver, current_account, '.json')):
            with open(gen_path(receiver, current_account, '.json'), 'w') as fp:
                fp.write('{"message": []}')
                fp.close()

        with open(gen_path(receiver, current_account, '.json'), 'r') as fp:
            data = json.load(fp)
            fp.close()

        if receiver == current_account:
            data['message'].append({
                'timestamp': timestamp,
                'content': content,
                'direction': 'self',
                'read': False
            })
        else:
            data['message'].append({
                'timestamp': timestamp,
                'content': content,
                'direction': ' in ',
                'read': False
            })

        with open(gen_path(receiver, current_account, '.json'), 'w') as fp:
            json.dump(data, fp)
            fp.close()

        #########################################################################
        if receiver != current_account:
            if not os.path.isfile(gen_path(current_account, receiver, '.json')):
                with open(gen_path(current_account, receiver, '.json'), 'w') as fp:
                    fp.write('{"message": []}')
                    fp.close()

            with open(gen_path(current_account, receiver, '.json'), 'r') as fp:
                    data = json.load(fp)
                    fp.close()

            data['message'].append({
                'timestamp': timestamp,
                'content': content,
                'direction': 'out ',
                'read': False
            })

            with open(gen_path(current_account, receiver, '.json'), 'w') as fp:
                json.dump(data, fp)
                fp.close()

        return 'done'

    else:
        if not authorized:
            return 'you have not logged in!'
        else:
            return 'receiver not found'

def send_file(key, receiver, timestamp, file_path, conn, bound, symmetricKey):

    max_length = 4096
    current_account = ''

    authorized = False
    receiver_found = False
    with open(os.getcwd() + '/data/user.json', 'r') as fp:
        data = json.load(fp)
        for tmp in data['user']:
            if tmp['key'] == key:
                current_account = tmp['account']
                authorized = True
            if tmp['account'] == receiver and tmp['online'] == True:
                receiver_found = True
        fp.close()

    if authorized and receiver_found:

        encrypt_send('ok', symmetricKey, conn)

        if not os.path.exists(gen_path(receiver, current_account, '/')):
            os.mkdir(gen_path(receiver, current_account, '/'))

        if os.path.isfile(gen_path(receiver, current_account, '/'+file_path)):
            for ic in range(1, 65536, 1):
                if not os.path.isfile(gen_path(receiver, current_account,
                    '/'+file_path.split('.')[0]+'('+str(ic)+').'+file_path.split('.')[1])):
                    file_path = file_path.split('.')[0]+'_'+str(ic)+'.'+file_path.split('.')[1]
                    break

        size_sum = 0
        with open(gen_path(receiver, current_account, '/'+file_path), 'wb') as fp:
            buf = conn.recv(max_length)
            #buf = receive_decode_byte(symmetricKey, conn, max_length)
            size_sum += len(buf)
            print('Bound: ', bound)
            while True:
                fp.write(buf)
                encrypt_send((str(size_sum) + ' '), symmetricKey, conn)
                if size_sum == bound:
                    break
                buf = conn.recv(max_length)
                #buf = receive_decode_byte(symmetricKey, conn, max_length)
                size_sum += len(buf)
            fp.close()

        if receiver != current_account:
            if not os.path.exists(gen_path(current_account, receiver, '/')):
                os.mkdir(gen_path(current_account, receiver, '/'))
            shutil.copyfile(gen_path(receiver, current_account, '/'+file_path),
                            gen_path(current_account, receiver, '/'+file_path))

        send_text(key, receiver, timestamp, '[file]' + file_path)

        return 'done'

    else:

        encrypt_send(('error'), symmetricKey, conn)

        if not authorized:
            return 'you have not logged in!'
        else:
            return 'receiver not found or not online'
