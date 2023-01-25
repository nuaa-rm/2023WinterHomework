from typing import Union

from jose import jwt, JWTError
from fastapi import Depends, Header, Cookie, HTTPException, status

import config as cfg
from host import host
from lobby import Lobby

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)

not_exist_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Lobby not exist",
)


def _getToken(
        token: Union[str, None] = None,
        x_token: Union[str, None] = Header(default=None),
        c_token: Union[str, None] = Cookie(default=None)
):
    if x_token:
        return x_token
    elif c_token:
        return c_token
    elif token:
        return token
    else:
        raise credentials_exception


def _verifyAppJWT(token: str):
    options = {"verify_signature": True, "verify_aud": False, "exp": True}
    return jwt.decode(token, cfg.publicKey, 'RS256', options)


def getUser(token: str = Depends(_getToken)):
    try:
        payload = _verifyAppJWT(token)
    except JWTError:
        raise credentials_exception
    return {'sid': payload['aud'], 'name': payload['name']}


def getLobby(lobby: str) -> Lobby:
    try:
        return host[lobby]
    except NameError:
        raise not_exist_exception
