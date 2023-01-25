from typing import Dict, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from task import Task


class Lobby:
    userBeat: List[Dict] = []
    tasks: Dict[int: Task] = {}
    nowTaskId = 0
    scheduler = AsyncIOScheduler()
    tasksCache = None

    def __init__(self, user):
        self.scheduler.start()
        self.scheduler.add_job(self._checkBeat, 'interval', seconds=3)
        self.admin = user['sid']

    def _checkBeat(self):
        removeList = []
        for i in range(len(self.userBeat)):
            it = self.userBeat[i]
            it['live'] -= 1
            if it['live'] <= 0:
                removeList.append(i)
        count = 0
        for it in removeList:
            del self.userBeat[it - count]
            count += 1

    def refreshBeat(self, user):
        found = False
        for info in self.userBeat:
            if info['user']['sid'] == user['sid']:
                info['live'] = 2
                found = True
        if not found:
            self.userBeat.append({'user': user, 'live': 2})

    def getUserList(self, user):
        res = [it['user'] for it in self.userBeat]
        return res

    def createTask(self, config, user):
        if user['sid'] != self.admin:
            raise PermissionError
        self.nowTaskId += 1
        self.tasks[self.nowTaskId] = Task(config)
        self.tasksCache = None

    def deleteTask(self, taskId, user):
        if user['sid'] != self.admin:
            raise PermissionError
        del self.tasks[taskId]
        self.tasksCache = None

    def refreshTasks(self, info: List[int], user):
        self.refreshBeat(user)
        res = {'data': self.tasksCache if self.tasksCache is not None else [], 'new': {}}
        for sysTask in self.tasks.keys():
            isNew = True
            if self.tasksCache is None:
                res['data'].append({
                    'key': sysTask,
                    'id': sysTask,
                    'createAt': self.tasks[sysTask].createAt.strftime('%m-%d %H:%M:%S'),
                    'startAt': self.tasks[sysTask].startTime.strftime('%m-%d %H:%M:%S')
                })
            for userTask in info:
                if userTask == sysTask:
                    isNew = False
            if isNew:
                res['new'][sysTask] = self.tasks[sysTask].getInfo(user)
        if self.tasksCache is None:
            self.tasksCache = res['data']
        return res

    def commitResult(self, task, data, user):
        if task not in self.tasks.keys():
            return Task.Code.taskNotFound
        return self.tasks[task].commit(data, user)

    def refreshResult(self, task, user):
        self.refreshBeat(user)
        if task not in self.tasks.keys():
            return []
        return self.tasks[task].getResult()
