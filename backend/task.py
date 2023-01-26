from typing import Dict, Union, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from generator import generate
from judge import judge


class TaskConfig(BaseModel):
    size: int
    number: int
    ek: int
    start: datetime


class TaskAnswer(BaseModel):
    runtime: float
    nodes: List
    edges: List


class Task:
    result: Dict[str, Union[dict, None]] = {}
    createAt: datetime.now()

    class Code(Enum):
        ok = 0
        alreadyCommit = 1
        taskNotFound = 2
        notStart = 3
        lobbyNotFound = 4

    def __init__(self, config: TaskConfig):
        self.answer = generate(_pSize=[config.size] * 2, _pNumber=config.number, _ek=config.ek)
        self.answer['size'] = config.size * 100
        self.startTime = config.start

    def getInfo(self, user):
        self.result[user['sid']] = {
            'key': user['sid'],
            'sid': user['sid'],
            'name': user['name'],
            'progress': 'Processing'
        }
        return self.answer

    def commit(self, data: Dict, user: Dict):
        if datetime.now() < self.startTime:
            return self.Code.notStart
        if user['sid'] in self.result.keys():
            return self.Code.alreadyCommit
        if data['ok']:
            judgeInfo = judge(data, self.answer)
            if judgeInfo['ok']:
                judgeInfo['progress'] = 'Success'
            else:
                judgeInfo['progress'] = 'Warning'
            del judgeInfo['ok']
            self.result['sid'] = {
                'key': user['sid'],
                'sid': user['sid'],
                'name': user['name'],
                **judgeInfo
            }
        else:
            self.result['sid'] = {
                'sid': user['sid'],
                'name': user['name'],
                'progress': 'Error'
            }
        return self.Code.ok

    def getResult(self):
        return self.result.values()
