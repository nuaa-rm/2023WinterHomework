import requests
import ntplib
import numpy as np
import cv2

from typing import Dict, Union, List
from threading import Thread
from datetime import datetime
import random
import string
import base64
import traceback
import webbrowser
import os
import time
import json

from . import procExec
from . import generator

endPoint = 'https://api.auth.bismarck.xyz'
webPoint = 'http://auth.bismarck.xyz'
appPoint = 'http://127.0.0.1:8002'


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


def getTimeDelta():
    ntp_clint = ntplib.NTPClient()
    local_time = time.time()
    internet_time = ntp_clint.request('pool.ntp.org').tx_time
    return local_time - internet_time


class Task(Thread):
    answer: Dict
    img_path: str
    runtime: datetime
    tid: int

    def __init__(self, tid, answer, runtime, committer):
        super().__init__()
        self.tid = tid
        self.answer = answer
        self.runtime = datetime.strptime(runtime, '%Y-%m-%d %H:%M:%S')
        self.committer = committer

    def _getTimeDelta(self):
        return (self.runtime - datetime.now()).total_seconds()

    def generateImage(self):
        _image = np.ones((self.answer['size'], self.answer['size'], 3), np.uint8) * 255
        generator.drawEdges(_image, self.answer['ess'], self.answer['pss'])
        generator.drawPoints(_image, self.answer['pss'])
        fileName = ''.join(random.sample(string.ascii_letters + string.digits, 12))
        self.img_path = os.path.join(os.path.dirname(__file__), f'static/images/{fileName}.png')
        cv2.imwrite(self.img_path, _image)

    def run(self) -> None:
        time.sleep(self._getTimeDelta() - 5)
        self.generateImage()
        time.sleep(self._getTimeDelta())
        res = procExec.run(self.img_path)
        res = {'runtime': res[0], 'nodes': res[1], 'edges': res[2], 'ok': res[3]}
        self.committer(self.tid, res)


class Client:
    name: str = None
    session: Union[requests.Session, None]
    clearLogin = lambda: print('auto login failed')
    lobby: str
    tasks: Dict[int, Task] = {}

    def init(self):
        self.session, ak = initAkSession()
        if ak is not None:
            self.name = decodeJWT(ak)['name']

    def getName(self):
        return self.name

    def setClearLogin(self, func):
        self.clearLogin = func

    def _post(self, url, data: Union[Dict, List, str]):
        if self.session is None:
            self.clearLogin()
            raise RuntimeError
        if not isinstance(data, str):
            data = json.dumps(data)
        res = self.session.post(url, json=data)
        if res.status_code == 401:
            self.init()
            return self._post(url, data)
        return res.json()

    def _get(self, url):
        if self.session is None:
            self.clearLogin()
            raise RuntimeError
        res = self.session.get(url)
        if res.status_code == 401:
            self.init()
            return self._get(url)
        return res.json()

    def _commitCreator(self):
        def commit(tid, data):
            res = self._post(appPoint + f'/lobby/{self.lobby}/{tid}/commit', data)
            if res['code'] != 0 and res['code'] != 2:
                raise RuntimeError
        return commit

    def _createLobbyCreator(self):
        def createLobby():
            res = self._get(appPoint + '/lobby/create')
            self.lobby = res['lid']
            return self.lobby
        return createLobby

    def _changeLobbyCreator(self):
        def changeLobby(lid):
            self.lobby = lid
        return changeLobby

    def _getUsersCreator(self):
        def getUsers():
            res = self._get(appPoint + f'/lobby/{self.lobby}/users')
            return res['data']
        return getUsers

    def _getAdminCreator(self):
        def getAdmin():
            res = self._get(appPoint + f'/lobby/{self.lobby}/admin')
            return res['data']
        return getAdmin

    def _createTaskCreator(self):
        def createTask(config):
            res = self._post(appPoint + f'/lobby/{self.lobby}/createTask', config)
            if res['code'] != 0:
                raise RuntimeError
        return createTask

    def _deleteTaskCreator(self):
        def deleteTask(tid):
            res = self._get(appPoint + f'/lobby/{self.lobby}/{tid}/delete')
            if res['code'] != 0:
                raise RuntimeError
        return deleteTask

    def _refreshTaskCreator(self):
        def refreshTask():
            res = self._post(appPoint + f'/lobby/{self.lobby}/tasks', list(self.tasks.keys()))
            for tid, info in res['data']['new'].items():
                self.tasks[tid] = Task(tid, info['answer'], info['start'], self._commitCreator())
                self.tasks[tid].start()
            return res['data']['data']
        return refreshTask

    def _refreshResultCreator(self):
        def refreshResult(tid):
            res = self._get(appPoint + f'/lobby/{self.lobby}/{tid}/result')
            return res['data']
        return refreshResult

    def getFuncs(self):
        return [
            self._createLobbyCreator(),
            self._changeLobbyCreator(),
            self._getUsersCreator(),
            self._getAdminCreator(),
            self._createTaskCreator(),
            self._deleteTaskCreator(),
            self._refreshTaskCreator(),
            self._refreshResultCreator()
        ]


client = Client()
