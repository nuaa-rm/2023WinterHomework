from typing import Dict
import random
import string

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from lobby import Lobby


class LobbyHost:
    lobbies: Dict[str, Lobby] = {}
    lobbiesLive: Dict[str, int] = {}
    scheduler = AsyncIOScheduler()

    def __init__(self):
        self.scheduler.start()
        self.scheduler.add_job(self._checkBeat, 'interval', minutes=3)

    def _checkBeat(self):
        removeList = []
        for k in self.lobbies.keys():
            self.lobbiesLive[k] -= 1
            if self.lobbiesLive[k] <= 0:
                removeList.append(k)
        for k in removeList:
            del self.lobbies[k]
            del self.lobbiesLive[k]

    def createLobby(self, user):
        lid = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        while lid in self.lobbies.keys():
            lid = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        self.lobbies[lid] = Lobby(user)
        self.lobbiesLive[lid] = 3

    def __getitem__(self, item) -> Lobby:
        if item not in self.lobbies.keys():
            raise NameError
        self.lobbiesLive[item] = 3
        return self.lobbies[item]


host = LobbyHost()
