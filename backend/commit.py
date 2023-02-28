import copy

from pydantic import BaseModel
from datetime import timedelta

from timedStorage import Storage
import config


class JudgeInfo(BaseModel):
    mode: str
    time: str
    co: bool
    nr: str
    np: str
    er: str
    ep: str
    ok: bool


listen = None
storage = Storage()
nowId = 0


def setListen(_listen, uid):
    global listen
    if str(uid) in config.admins:
        listen = _listen
        storage.clear()


def addInfo(uid, info: JudgeInfo):
    global nowId
    if uid == listen:
        print('add')
        if info.np == 'NaN%':
            info.np = '0%'
        if info.ep == 'NaN%':
            info.ep = '0%'
        storage.set(nowId, {
            'mode': info.mode,
            'time': float(info.time[:-1]),
            'co': info.co,
            'ok': info.ok,
            'nr': float(info.nr[:-1]) / 100,
            'np': float(info.np[:-1]) / 100,
            'er': float(info.er[:-1]) / 100,
            'ep': float(info.ep[:-1]) / 100,
        }, timedelta(minutes=2))
        nowId += 1
        if nowId >= 1e5:
            nowId = 0


def getInfo(uid):
    if str(uid) in config.admins:
        info = list(storage.get().values())
        storage.clear()
        return info
    else:
        return []

