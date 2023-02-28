from typing import Dict, List

from fastapi import FastAPI, Depends, Request, Body
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from depends import getUser, getLobby
from lobby import Lobby
from task import TaskConfig, TaskAnswer
from host import host
import commit as com

app = FastAPI(
    title="长空御风2023寒假作业",
    version='1.0.0'
)
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rateLimitErrorHandler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={"code": 429, "message": "访问过快，请稍后重试"}
    )


@app.exception_handler(RequestValidationError)
async def requestValidationHandler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={"code": 11, "message": "参数错误"}
    )


@app.post('/commit')
@limiter.limit('100/minute')
async def commitInfo(request: Request, data: com.JudgeInfo, user: Dict = Depends(getUser)):
    com.addInfo(user['sid'], data)
    return {'code': 0}


@app.get('/setListen')
@limiter.limit('10/minute')
async def setListen(request: Request, listen: str, user: Dict = Depends(getUser)):
    com.setListen(listen, user['sid'])
    return {'code': 0}


@app.get('/getInfo')
@limiter.limit('60/minute')
async def getInfo(request: Request, user: Dict = Depends(getUser)):
    return {'code': 0, 'data': com.getInfo(user['sid'])}


@app.get('/lobby/create')
@limiter.limit('4/minute')
async def createLobby(request: Request, user: Dict = Depends(getUser)):
    lid = host.createLobby(user)
    return {'code': 0, 'lid': lid}


@app.get('/lobby/{lid}/users', dependencies=[Depends(getUser)])
async def getLobbyUsers(lobby: Lobby = Depends(getLobby)):
    return {'code': 0, 'data': lobby.getUserList()}


@app.get('/lobby/{lid}/admin', dependencies=[Depends(getUser)])
async def getLobbyAdmin(lobby: Lobby = Depends(getLobby)):
    return {'code': 0, 'data': lobby.admin}


@app.post('/lobby/{lid}/createTask')
@limiter.limit('4/minute')
async def createTask(
        request: Request,
        config: TaskConfig,
        user: Dict = Depends(getUser),
        lobby: Lobby = Depends(getLobby)
):
    lobby.createTask(config, user)
    return {'code': 0}


@app.get('/lobby/{lid}/{tid}/delete')
@limiter.limit('4/minute')
async def deleteTask(
        request: Request,
        tid: int,
        user: Dict = Depends(getUser),
        lobby: Lobby = Depends(getLobby)
):
    lobby.deleteTask(tid, user)
    return {'code': 0}


@app.post('/lobby/{lid}/tasks')
async def refreshTask(
        info: List[int] = Body(),
        user: Dict = Depends(getUser),
        lobby: Lobby = Depends(getLobby)
):
    return {'code': 0, 'data': lobby.refreshTasks(info, user)}


@app.post('/lobby/{lid}/{tid}/commit')
async def commitResult(
        tid: int,
        data: TaskAnswer,
        user: Dict = Depends(getUser),
        lobby: Lobby = Depends(getLobby)
):
    res = lobby.commitResult(tid, data, user)
    return {'code': res.value, 'msg': res.name}


@app.get('/lobby/{lid}/{tid}/result')
@limiter.limit('4/minute')
async def refreshTask(
        request: Request,
        tid: int,
        user: Dict = Depends(getUser),
        lobby: Lobby = Depends(getLobby)
):
    return {'code': 0, 'data': lobby.refreshResult(tid, user)}
