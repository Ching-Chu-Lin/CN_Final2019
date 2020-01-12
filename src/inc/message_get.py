import os
import sys
import json

from .account import md5_encode

def gen_path(a, b, c):
    buf = os.getcwd() + '/data/' + a + '/' + b + c
    return buf

def show_all(key):

    ret = ''
    max_length = 4096
    current_account = ''
    authorized = False
    with open(os.getcwd() + '/src/data/user.json', 'r') as fp:
        data = json.load(fp)
        for tmp in data['user']:
            if tmp['key'] == key:
                current_account = tmp['account']
                authorized = True
        fp.close()
    if authorized:
        for f in os.listdir(gen_path(current_account, '', '')):
            print(f)
            if f.endswith(".json"):
                with open(gen_path(current_account, f, ''), 'r') as fp:
                    data = json.load(fp)
                    length = len(data['message'])
                    tmp = data['message'][length-1]
                    ret = ret + f.split('.')[0] + ' '
                    ret = ret + '[' + tmp['direction'] + '] '
                    ret = ret + tmp['timestamp'] + ' '
                    if tmp['read']:
                        ret = ret + '( read ):' + ' '
                    else:
                        ret = ret + '(unread):' + ' '
                    ret = ret + tmp['content'] + '\n'
                    fp.close()
        return ret
    else:
        return 'you have not logged in!'

def get_text(key, person, search):

    max_length = 4096
    current_account = ''

    authorized = False
    person_found = False
    with open(os.getcwd() + '/src/data/user.json', 'r') as fp:
        data = json.load(fp)
        for tmp in data['user']:
            if tmp['key'] == key:
                current_account = tmp['account']
                authorized = True
            if tmp['account'] == person:
                person_found = True
        fp.close()

    if authorized and person_found:

        if os.path.isfile(gen_path(current_account, person, '.json')) == False:
            return 'record is empty'

        if search == 'all':
            search = ''

        buf = 'Message History:\n'
        with open(gen_path(current_account, person, '.json'), 'r') as fp:
            data = json.load(fp)
            for tmp in data['message']:
                if tmp['content'].find(search) != -1:
                    buf = buf + '[' + tmp['direction'] + '] '
                    buf = buf + tmp['timestamp'] + ' '
                    if tmp['read'] == True:
                        buf = buf + '( read ):'
                    else:
                        buf = buf + '(unread):'
                    buf = buf + tmp['content'] + '\n'
                    if tmp['direction'] == ' in ' or tmp['direction'] == 'self':
                        tmp['read'] = True
            fp.close()

        with open(gen_path(current_account, person, '.json'), 'w') as fp:
            json.dump(data, fp)
            fp.close()

        with open(gen_path(person, current_account, '.json'), 'r') as fp:
            data = json.load(fp)
            for tmp in data['message']:
                if tmp['content'].find(search) != -1 and tmp['direction'] == 'out ':
                    tmp['read'] = True
            fp.close()

        with open(gen_path(person, current_account, '.json'), 'w') as fp:
            json.dump(data, fp)
            fp.close()

        return buf

    else:
        if not authorized:
            return 'you have not logged in!'
        else:
            return 'person not found'

def get_file(key, person, file_path, conn):

    max_length = 4096
    current_account = ''

    authorized = False
    person_found = False
    file_found = False
    with open(os.getcwd() + '/src/data/user.json', 'r') as fp:
        data = json.load(fp)
        for tmp in data['user']:
            if tmp['key'] == key:
                current_account = tmp['account']
                authorized = True
            if tmp['account'] == person and tmp['online'] == True:
                person_found = True
        fp.close()

    if authorized and person_found:

        with open(gen_path(current_account, person, '.json'), 'r') as fp:
            data = json.load(fp)
            for tmp in data['message']:
                if tmp['content'] == '[file]' + file_path:
                    tmp['content'] = '[received]' + file_path
                    file_found = True
            fp.close()

        if file_found:

            bound = int(os.path.getsize(gen_path(current_account, person, '/' + file_path)))
            conn.send(('ok ' + str(bound)).encode())
            tmp = (conn.recv(max_length)).decode()
            with open(gen_path(current_account, person, '/' + file_path), 'rb') as fp:
                buf = fp.read(max_length)
                conn.send(buf)
                while True:
                    tmp = (conn.recv(max_length)).decode()
                    is_end  = False
                    for k in tmp.split():
                        if int(k) == bound:
                            is_end = True
                            break
                    if is_end:
                        break
                    buf = fp.read(max_length)
                    conn.send(buf)
                fp.close()

            return 'done'

        else:
            conn.send(('error').encode())
            return 'file not found'

    else:
        conn.send(('error').encode())
        if not authorized:
            return 'you have not logged in!'
        else:
            return 'person not found'
