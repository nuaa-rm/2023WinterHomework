from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job

from datetime import datetime, timedelta
from typing import Union, Any, Dict


class Storage:
    _storage = {}
    _jobs: Dict[Any, Job] = {}

    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._scheduler.start()

    def isIn(self, k):
        return k in self._storage.keys()

    def get(self, k=None):
        if k is None:
            return self._storage
        else:
            return self._storage[k]

    def set(self, k, v, timeout: Union[timedelta, None] = None):
        self._storage[k] = v
        if timeout:
            job = self._scheduler.add_job(self.erase, 'date', run_date=datetime.now()+timeout, args=(k, True))
            self._jobs[k] = job

    def clear(self):
        self._jobs.clear()
        self._scheduler.remove_all_jobs()
        self._storage.clear()

    def erase(self, v, fromScheduler=False):
        if v in self._storage.keys():
            del self._storage[v]
            if not fromScheduler and v in self._jobs.keys():
                self._jobs[v].remove()
                del self._jobs[v]
        else:
            for _k, _v in self._storage.items():
                if _v == v:
                    del self._storage[_k]
                if not fromScheduler and _k in self._jobs.keys():
                    self._jobs[_k].remove()
                    del self._jobs[_k]
