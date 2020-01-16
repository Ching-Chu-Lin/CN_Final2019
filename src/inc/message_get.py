import os
import sys
import json
import prettytable as pt

from .account import md5_encode

def gen_path(a, b, c):
    buf = os.getcwd() + '/data/' + a + '/' + b + c
    return buf

def show_all(key):

    ret = ''
    max_length = 4096
    current_account = ''
    authorized = False
    with open(os.getcwd() + '/data/user.json', 'r') as fp:
        data = json.load(fp)
        for tmp in data['user']:
            if tmp['key'] == key:
                current_account = tmp['account']
                authorized = True
        fp.close()
    if authorized:
        ret = pt.PrettyTable()
        ret.field_names = ['User', 'Sender', 'Time', 'Status', 'Message']
        for f in os.listdir(gen_path(current_account, '', '')):
            print(f)
            if f.endswith(".json"):
                with open(gen_path(current_account, f, ''), 'r') as fp:
                    data = json.load(fp)
                    fp.close()
                    tmp = data['message'][len(data['message'])-1]
                    arr = []
                    arr.append(f.split('.')[0])
                    arr.append(tmp['direction'])
                    arr.append(tmp['timestamp'])
                    if tmp['read']:
                        arr.append('( read )')
                    else:
                        arr.append('(unread)')
                    arr.append(tmp['content'])
                    ret.add_row(arr)
        return ret.get_string(sortby="Time", reversesort=True)
    else:
        return 'you have not logged in!'

def get_text(key, person, search):

    max_length = 4096
    current_account = ''

    authorized = False
    person_found = False
    with open(os.getcwd() + '/data/user.json', 'r') as fp:
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

        ret = pt.PrettyTable()
        ret.field_names = ['Sender', 'Time', 'Status', 'Message']
        with open(gen_path(current_account, person, '.json'), 'r') as fp:
            data = json.load(fp)
            fp.close()
            for tmp in data['message']:
                arr = []
                if tmp['content'].find(search) != -1:
                    arr.append(tmp['direction'])
                    arr.append(tmp['timestamp'])
                    if tmp['read'] == True:
                        arr.append('( read )')
                    else:
                        arr.append('(unread)')
                    arr.append(tmp['content'])
                    ret.add_row(arr)
                    if tmp['direction'] == ' in ' or tmp['direction'] == 'self':
                        tmp['read'] = True

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

        return ret.get_string(sortby="Time", reversesort=True)

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
    with open(os.getcwd() + '/data/user.json', 'r') as fp:
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
