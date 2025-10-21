# import packages from default or pip library
import jwt
from redis.exceptions import ConnectionError
from random import randint
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone

# import packages from this framework
from settings import AUTHENTICATION
from src.jknife.db import logger
from src.jknife.db import redis_connector


# create secret key in this file.
def create_secretkey() -> str:
    return "".join([chr(randint(65, 122)) for _ in range(256)])


# SETTINGS
_DEFAULT_TOKEN_VALID_TIME: int = 20
_DEFAULT_TOKEN_REFRESH_TIME: int = 24 * 60 * 30
_TOKEN_SETTING: dict = AUTHENTICATION.get("token")
_TOKEN_SECRET_KEY: str = _TOKEN_SETTING.get("secret_key") or create_secretkey()
_TOKEN_ISSUER: str = _TOKEN_SETTING.get("token_issuer") or "127.0.0.1"
_TOKEN_AUDIENCE: str = _TOKEN_SETTING.get("token_audience") or "http://127.0.0.1"
_TOKEN_EXP_ACCESS: int = _TOKEN_SETTING.get("token_valid_time") or _DEFAULT_TOKEN_VALID_TIME
_TOKEN_EXP_REFRESH: int = _TOKEN_SETTING.get("token_refresh_time") or _DEFAULT_TOKEN_REFRESH_TIME
_TOKEN_ALGORITHM: str = _TOKEN_SETTING.get("algorithm") or "HS256"


# Bearer Token Window
oauth2_scheme = HTTPBearer(scheme_name="bearer",
                           description="Authentication related with JWT token.\nInput access token got after signing in.",
                           auto_error=False)
basic_scheme = HTTPBasic(scheme_name="basic",
                         description="Authentication with username and password.\nInput username and password.",
                         auto_error=False)


# define function for tokens
def _check_blacklist_access_token(token: str) -> str:
    """
    check whether the access token is registered as blacklist in redis.

    :param token: access_token in string
    :return: access_token, if it is not registered in redis
    """

    user_unique = decode_jwt_token(token=token).get("sub")

    if redis_connector.get(name=f"access_token:{token}"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"msg": "invalid access token"})

    elif not redis_connector.get(name=f"refresh_token:{user_unique}"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"msg": "you have to sign in first."})

    return token

def check_whitelist_refresh_token(user_unique: str, token: str):
    """
    check whether the refresh token is registered as whitelist in redis.

    :param token: refresh_token in string
    :return: refresh_token, if it is registered in redis
    """

    registered_token: bytes = redis_connector.get(name=f"refresh_token:{user_unique}")
    if registered_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"msg": "you have to sign in first."})

    if registered_token.decode("utf-8") != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"msg": "invalid refresh token"})
    return token

def create_jwt_token(user_unique: str, user_data: dict, is_access: bool=True) -> str:
    """
    create jwt token(access and refresh) with user data.

    :param user_unique: primary key to distinguish specific object among the users.
    :param user_data: user data that is customised by developer.
    :param is_access: set token type as bool for access(default) or refresh(False).
    :return: encrypted string token.
    """

    payload: dict = {
        "iss": _TOKEN_ISSUER,
        "sub": str(user_unique),
        "aud": _TOKEN_AUDIENCE,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=_TOKEN_EXP_ACCESS if is_access else _TOKEN_EXP_REFRESH),
        "user_data": user_data,
    }
    return jwt.encode(payload=payload,
                      key=_TOKEN_SECRET_KEY,
                      algorithm=_TOKEN_ALGORITHM)

def decode_jwt_token(token:str, is_access:bool=True) -> dict | None:
    """
    decode jwt token information that encrypted in token string.

    :param token: token value in string
    :param is_access: set token type as bool for access(default) or refresh(False).
    :return:
    """

    try:
        return jwt.decode(jwt=token,
                          key=_TOKEN_SECRET_KEY,
                          audience=_TOKEN_AUDIENCE,
                          algorithms=_TOKEN_ALGORITHM)

    except jwt.exceptions.ExpiredSignatureError:
        token_type: str = "access" if is_access else "refresh"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"msg": f"{token_type} token was expired"})

    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"msg": "invalid access token. can not decode token information."})

def get_bearer_access_token(user_cred: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> str:
    """
    get access token from HTTPBearer credential in RestAPI Docs Page.

    :param user_cred: get access_token information from HTTPBearer credential
    :return: return access_token
    """

    if user_cred is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"msg": "missing access token in headers."})

    if user_cred.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"msg": "invalid access token. token type is not match."})

    return _check_blacklist_access_token(token=user_cred.credentials)

def get_token_info(token: str, is_access: bool = True) -> dict:
    """
    decrypt JWT token and return its data as dict type.

    :param token: JWT token(access or refresh)
    :param is_access: set token type as bool for access(default) or refresh(False).
    :return: token information in dict type.
    """


    payload: dict = decode_jwt_token(token=token, is_access=is_access)
    return payload

def register_blacklist_access_token(token: str, ex: int=_TOKEN_EXP_ACCESS) -> None:
    """
    register JWT access token in redis after signout or changing password
    template: access_token: {ACCESS_TOKEN}

    :param token: access_token that will be registered in redis.
    :param ex: token expiration time in second.
    :return: None
    """

    try:
        redis_connector.set(name=f"access_token:{token}", value="1", ex=ex * 60)
    except ConnectionError:
        logger.warning(msg="fail to register access_token as a blacklist. can not connect to redis db.")

    return None

def register_whitelist_refresh_token(user_unique: str, token: str) -> None:
    """
    register JWT refresh token in redis after signin.
    template: refresh_token:{USER_UNIQUE}

    :param user_unique: primary key for each user.
    :param token: refresh token that was issued after signin.
    :return: None
    """
    try:
        redis_connector.set(name=f"refresh_token:{user_unique}", value=token, ex=_TOKEN_EXP_REFRESH * 60)
    except ConnectionError:
        logger.warning(msg="fail to register refresh_token as a whitelist. can not connect to redis db.")

    return None

def remove_whitelist_refresh_token(user_unique: str) -> None:
    """
    remove registered refresh token in redis after signout or changing password.

    :param user_unique: primary key for each user.
    :return: None
    """

    try:
        redis_connector.delete(f"refresh_token:{user_unique}")
    except ConnectionError:
        logger.warning(msg="fail to remove refresh token from redis. can not connect to redis db.")

    return None