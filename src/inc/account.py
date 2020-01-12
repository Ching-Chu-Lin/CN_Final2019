import os
import sys
import shutil
import random
import string
import json
import hashlib

def md5_encode(password):
    m = hashlib.md5()
    m.update(password.encode('utf-8'))
    return m.hexdigest()

def random_key():
    letters = string.ascii_lowercase
    tmp = ''.join(random.choice(letters) for i in range(256))
    return md5_encode(tmp)

def create_user(account, password):

    duplicate = False
    with open(os.getcwd() + '/data/user.json', 'r') as fp:
        data = json.load(fp)
        for tmp in data['user']:
            if tmp['account'] == account:
                duplicate = True
                break
        fp.close()

    if not duplicate:

        data['user'].append({
            'account': account,
            'password': md5_encode(password),
            'key': '',
            'online': False
        })

        with open(os.getcwd() + '/data/user.json', 'w') as fp:
            json.dump(data, fp)
            fp.close()

        shutil.rmtree(os.getcwd() + '/data/' + account, ignore_errors=True)
        os.mkdir(os.getcwd() + '/data/' + account, 0o755)

        return 'done'

    else:
        return 'account exists'

def delete_user(account, password):

    deleted = False
    with open(os.getcwd() + '/data/user.json', 'r') as fp:
        data = json.load(fp)
        ic = 0
        for tmp in data['user']:
            if tmp['account'] == account \
                and tmp['password'] == md5_encode(password):
                del data['user'][ic]
                deleted = True
                break
            ic += 1
        fp.close()

    if deleted:

        with open(os.getcwd() + '/data/user.json', 'w') as fp:
            json.dump(data, fp)
            fp.close()

    return deleted

def change_password(account, password, new_password):
    ret = delete_user(account, password)
    if ret:
        return create_user(account, new_password)
    else:
        return 'account does not exist'\

def log_in(account, password):

    authorized = False
    key = ''
    with open(os.getcwd() + '/data/user.json', 'r') as fp:
        data = json.load(fp)
        for tmp in data['user']:
            if tmp['account'] == account \
                and tmp['password'] == md5_encode(password):
                key = random_key();
                tmp['key'] = key
                tmp['online'] = True
                authorized = True
                break
        fp.close()

    if authorized:

        with open(os.getcwd() + '/data/user.json', 'w') as fp:
            json.dump(data, fp)
            fp.close()

        return key

    else:
        return 'wrong account or password'

def log_out(key):

    with open(os.getcwd() + '/data/user.json', 'r') as fp:
        data = json.load(fp)
        for tmp in data['user']:
            if tmp['key'] == key:
                tmp['online'] = False
        fp.close()

    with open(os.getcwd() + '/data/user.json', 'w') as fp:
            json.dump(data, fp)
            fp.close()

    return 'you have logged out'
