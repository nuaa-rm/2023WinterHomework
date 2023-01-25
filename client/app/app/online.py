import requests

import base64
import traceback
import webbrowser
import os
import time
import json

endPoint = 'https://api.auth.bismarck.xyz'
webPoint = 'http://auth.bismarck.xyz'


def initSession(jwt=None):
    session = requests.session()
    session.headers = {'origin': webPoint}
    if jwt is not None:
        session.headers['X-Token'] = jwt
    return session


def getNonce(session):
    res = session.get(f'{endPoint}/auth/device/register', params={
        'mode': 'device',
        'app': '视觉组寒假作业'
    }).json()
    return res['nonce']


def loginTrigger(nonce):
    print('We will use your browser link below to login')
    print('If your browser don\'t automatically, please copy it to your browser and open')
    print(f'{webPoint}/#/?mode=device&app=视觉组寒假作业&nonce={nonce}')
    webbrowser.open(f'{webPoint}/#/?mode=device&app=视觉组寒假作业&nonce={nonce}')


def verifyLogin(session, nonce):
    while True:
        res = session.get(f'{endPoint}/auth/device/verify', params={
            'mode': 'device',
            'app': '视觉组寒假作业',
            'nonce': nonce
        }).json()
        if res['code'] == 0:
            return 0, res['jwt']
        elif res['code'] == 11:
            return 1, None
        elif res['code'] == 13:
            time.sleep(1)


def _getAK(session, refreshKey):
    res = session.get(f'{endPoint}/refreshToken', params={'token': refreshKey})
    if res.status_code != 200:
        return None
    res = res.json()
    refreshKey = res['refresh']
    saveRefreshToken(refreshKey)
    return res['access']


def initAkSession():
    refreshKey = readRefreshToken()
    if refreshKey is None:
        return None, None
    session = initSession()
    _ak = _getAK(session, refreshKey)
    if _ak is None:
        return None, None
    return initSession(_ak), _ak


def getTokenPath():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), '.token')


def saveRefreshToken(jwt):
    with open(getTokenPath(), 'w') as file:
        file.write(jwt)


def readRefreshToken():
    path = getTokenPath()
    if not os.path.exists(path):
        return None
    with open(path, 'r') as file:
        data = file.read()
    return data


def login():
    se = initSession()
    nonce = getNonce(se)
    loginTrigger(nonce)
    code, refreshToken = verifyLogin(se, nonce)
    if code == 0:
        saveRefreshToken(refreshToken)
    return code


def decodeJWT(jwt):
    info = jwt.split('.')[1]
    pad = len(info) % 4
    if pad == 2:
        info += '=='
    elif pad == 3:
        info += '='
    info = base64.b64decode(info)
    info = json.loads(info)
    return info


def getName(jwt):
    return decodeJWT(jwt)['name']

