import requests

import webbrowser
import os
import time
import math

endPoint = 'https://api.auth.bismarck.xyz'
webPoint = 'http://auth.bismarck.xyz'
appPoint = 'http://wh_api.bismarck.xyz'


def initSession(jwt=None):
    session = requests.session()
    if jwt is not None:
        session.headers = {'X-Token': jwt}
    else:
        session.headers = {'origin': webPoint}
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
    login_link = f'{webPoint}/#/?mode=device&app=视觉组寒假作业&nonce={nonce}'
    print(login_link)
    webbrowser.open(login_link)


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
    return os.path.join(os.path.dirname(__file__), '.token')


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


class Client:
    session: requests.Session

    def __init__(self):
        self.session, ak = initAkSession()
        if ak is None:
            code = login()
            if code != 0:
                print('登陆出现异常错误')
                exit(0)
            self.session, _ = initAkSession()

    def _get(self, url):
        if self.session is None:
            raise RuntimeError
        res = self.session.get(url)
        if res.status_code == 401:
            self.__init__()
            return self._get(url)
        return res.json()

    def setListen(self, _listen: str):
        self._get(appPoint + '/setListen?listen=%s' % _listen)

    def getInfo(self) -> []:
        return self._get(appPoint + '/getInfo')


def getScore(_data):
    _ok = 1 if _data['ok'] else 0
    _data = math.sqrt(math.sqrt(_data['np'] * _data['nr'] * _data['ep'] * _data['er']))
    if _data < 0.6:
        return 0, _ok
    return _data, _ok


if __name__ == '__main__':
    client = Client()
    print('Please input Student ID which want to listen')
    listen = input('>>> ')
    client.setListen(listen)
    print('Start listen!')
    stupid = []
    easy = []
    normal = []
    while len(stupid) < 5 or len(easy) < 5 or len(normal) < 5:
        info = client.getInfo()['data']
        if len(info) == 0:
            print('Get empty data!')
            time.sleep(2)
            continue
        for data in info:
            s1, s2 = getScore(data)
            if data['mode'] == 'stupid':
                if len(stupid) < 5:
                    stupid.append(6 * s1 + 4 * s2)
                    print('Get Score %.2f in stupid difficulty (%i/5)' % (stupid[-1], len(stupid)))
                else:
                    print('Stupid difficulty has been tried five times!')
            elif data['mode'] == 'easy':
                if len(easy) < 5:
                    easy.append(8 * s1 + 7 * s2)
                    print('Get Score %.2f in easy difficulty (%i/5)' % (easy[-1], len(easy)))
                else:
                    print('Easy difficulty has been tried five times!')
            elif data['mode'] == 'normal':
                if len(normal) < 5:
                    normal.append(8 * s1 + 7 * s2)
                    print('Get Score %.2f in normal difficulty (%i/5)' % (normal[-1], len(normal)))
                else:
                    print('Normal difficulty has been tried five times!')
        time.sleep(2)
    print('-------------------------------------------------')
    print('Total score: %.2f' % sum(stupid + easy + normal))
