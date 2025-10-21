import sys
import os


FOLDER_LIST: tuple = ("models", "routers", "views", )

# Help MSG for commands 'jknife'
HELP_MSG = """
[ Command 'jknife' ]
Usage: jknife [sub_command] [3rd argument]

* sub_command:
- startproject [PROJECT_NAME]   : create project filesystem
- createapp [APP_NAME]          : create API application in project
- run [OPTIONS]                 : run server with uvicorn

[run OPTIONS]
--host [HOSTNAME]               : run server with hostname [HOSTNAME] 
--port [PORT_INT]               : run server with portnumber [PORT]
--reload                        : reload uvicorn server automatically after editing source.
"""

# Template for models/APP_NAME.py
MODULE_IMPORT_STRING_MODELS: str = """
# import packages from default or pip library
from typing_extensions import Annotated, Doc

# import packages from this framework below


# set CONSTANT variables below.


# define your own customising class below
"""

# Template for routers/APP_NAME.py
MODULE_IMPORT_STRING_ROUTERS: str = """# import packages from default or pip library
from fastapi import APIRouter, Depends, status, HTTPException
from typing_extensions import Annotated, Doc

# import packages from this framework below


# set CONSTANT variables below.
router = APIRouter(prefix="/{}",
                   tags=['{}'])

# define your own customising class below
"""

# Template for views/APP_NAME.py
MODULE_IMPORT_STRING_VIEWS: str = """# import packages from default or pip library
from pydantic import BaseModel

# import packages from this framework below


# set CONSTANT variables below.


# define your own customising class below
"""

# WARN MSGs
WARN_MSG_ALREADY_EXIST_PROJECT: str = """
[WARNING] You already have project '{}'.
"""

# ERROR MSGs
ERROR_MSG_START_PROJECT: str = """
[ERROR] 
- You have to execute 'createapp' command in your project folder.

* Command for Starting Project: jknife startproject [PROJECT_NAME]
"""

# File Contents
CONTENTS_IN_SETTINGS: str = """# this file is charge of config for custom fastapi.
from os import environ


# [ DEBUG ]
# this variable is a mode switcher.
# if you are about to publish your application to public, please turn this switch to False.
# on the other hands, during development, please switch this value to True.
# DEBUG_MODE provides
# - query logs on database.
DEBUG_MODE: bool = True

# [ API_VERSION ]
# API_VERSION is a management variables for your api.
# This value will be used to call api as an URL prefix. e.g) /api/{YOUR_API_VERSION}/
# you can modify the value of API_VERSION to whatever you want.
API_VERSION: str = "v1"

# [ DATABASE ]
# DATABASE is charge of connection to database server.
# recommend to store DB information in env var and get them by using environ.get()
# this framework supports some databases.
# - supported type: ["none", "postgresql", "mysql", "sqlite", "mongo"]
#
# type 'none': if you do not want to use database. it is a default if the type is None
# structure of database
# - type in ['postgresql', 'mysql', 'mongo']
#   - key: "dbms"
#   - values: {"username": DB_USERNAME, "password": DB_PASSWORD, "host": DB_HOST, "port": DB_PORT, "db": DB_NAME}
#   -         if you use mongo, it is possible to add key 'authSource' for name of database that is responsible for auth.
# - type 'sqlite'
#   - sqlite_filepath: input path of sqlite3 database file in an absolute way or a relative one.
# "redis" exist for the Redis - cached db.
DATABASE: dict = {
    "type": environ.get("db_type"),
    "dbms": {
        "username": environ.get("db_username"),
        "password": environ.get("db_password"),
        "host": environ.get("db_host"),
        "port": int(environ.get("db_port")),
        "db": environ.get("db_name"),
        "authSource": environ.get("mongo_auth_source")
    },
    "sqlite": {
        "sqlite_filepath": "./fastapi.db"
    },
    "redis": {
        "host": environ.get("redis_host"),
        "port": environ.get("redis_port"),
    }
}

# [ AUTHENTICATION ]
# AUTHENTICATION is charge of JWT token for authenticated user.
# token: information for JWT token
# - token_issuer: token issuer
# - token_audience: IP or URL address that allows this token
# - token_valid_time: interval time between when the access token issued and expired in minutes.
# - token_refresh_time: interval time in minute for reissuing access token.
# - secret_key: secret key to encrypt token
# - algorithm: select encryption algorithm
#   * HS: for HMAC symmetric algorithm
#   * RS: for RSA symmetric algorithm
#   * ES: for ECDSA asymmetric algorithm
AUTHENTICATION: dict = {
    "token": {
        "token_issuer": "http://127.0.0.1",
        "token_audience": "http://127.0.0.1",
        "token_valid_time": 20,
        "token_refresh_time": 60 * 24 * 30,
        "secret_key": "THIS IS A TEST",
        "algorithm": "HS256"
    }
}

# [ PASSWORD_POLICIES ]
# PASSWORD_POLICIES is charge of password compliance, when users are created or change their password
# compliance: the list of password policies
# - PASSWORD_MINLEN: limit the minimum length of password. default is 8 but it can be customized with 'min_length'.
# - PASSWORD_UPCHAR: password must contain at least one upper alphabet character.
# - PASSWORD_LOWCHAR: password must contain at least one lower alphabet character.
# - PASSWORD_NUMBER: password must contain at least one numeric character.
# - PASSWORD_SPECIAL: password must contain at least one special character.
# encrypt_type: algorithm for encrypting password. please refer to 'hashlib.algorithms_available'
# min_length: minimum length of password. it will be used for PASSWORD_MINLEN
PASSWORD_POLICIES: dict = {
    "compliance": [
        "PASSWORD_MINLEN",
        "PASSWORD_UPCHAR",
        "PASSWORD_LOWCHAR",
        "PASSWORD_NUMBER",
        "PASSWORD_SPECIAL"
    ],
    "encrypt_type": "sha256",
    "min_length": 8
}


# [ LOG_SETTINGS ]
# LOG_SETTINGS is based on python dictConfig
# (https://docs.python.org/3/library/logging.config.html#dictionary-schema-details).
# Refer to the official documentation, write down your own config for logging.
# {"version": 1, "disable_existing_logger": False} will be applied automatically.
# If DEBUG_MODE is True, uvicorn log will be printed out on your console.
# Default Logger:
# * DB: The logger 'db' is charge of database logging.
#       if you want to change the name of logger, you should also change the DB_LOGGER_LIST below.
#       or you can not see any proper log.
LOG_SETTINGS: dict = {
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(name)s:%(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S:%s"
        }
    },
    "handlers": {
        "main": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "default",
            "filename": "logs/all_logs.log",
            "maxBytes": 1024 * 1024 * 100,          # 10 MB
            "backupCount": 3
        },
        "db": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "default",
            "filename": "logs/db.log",
            "maxBytes": 1024 * 1024 * 100,          # 10 MB
            "backupCount": 3
        },
        "db_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "default",
            "filename": "logs/db_error.log",
            "maxBytes": 1024 * 1024 * 100,           # 10 MB
            "backupCount": 3
        }
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["main"],
        },
        "db": {
            "level": "INFO",
            "handlers": ["db", "db_error"],
            "propagate": True,
        },
    }
}

# [ LOGGER_LIST ]
# create your own logger instance with core.logging.LoggerMgmt and use it in specific realm.
DB_LOGGER_LIST = ("db",)


### END CONTENTS ###
"""
CONTENTS_IN_MAIN: str = """# import modules from python library
import importlib, os
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


# import required objects from projects
from jknife.db import DBConnector
from settings import API_VERSION


# set main url for all router
MAIN_URL: str = f"/api/{API_VERSION}"


# DB Connector
db_connector = DBConnector()

# start application
app = FastAPI(lifespan=db_connector.startup_db)


# add exception handler for ValidationException
@app.exception_handler(exc_class_or_status_code=RequestValidationError)
async def validation_error(req: Request, exc: RequestValidationError):
    errors: dict = exc.errors()[0] if isinstance(exc.errors(), list) else dict(exc.errors())
    result: dict = {"field": errors.get("input"), "msg": errors.get("msg")}
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": result}
    )


# add routers_bak
for router in os.listdir(os.path.abspath(path="routers_bak")):
    if not router.startswith("__"):
        tmp_module = importlib.import_module(name=f"routers_bak.{router.split('.')[0]}")
        app.include_router(router=tmp_module.router,
                           prefix=MAIN_URL)


"""


def startproject(pjt_name: str) -> None:
    # check whether the folder 'pjt_name' exist or not.
    if pjt_name in os.listdir():
        # print WARNING
        print(WARN_MSG_ALREADY_EXIST_PROJECT.format(pjt_name))
        return None

    # create project folder
    os.mkdir(pjt_name)

    # create working folders for jknife
    for folder_name in FOLDER_LIST:
        if f"{folder_name}" not in os.listdir(pjt_name):
            os.mkdir(f"{pjt_name}/{folder_name}")

            if "__init__.py" not in os.listdir(f"{pjt_name}/{folder_name}"):
                with open(f"{pjt_name}/{folder_name}/__init__.py", mode="w") as f:
                    f.write("")

    # create settings.py file
    if f"settings.py" not in os.listdir(pjt_name):
        with open(f"{pjt_name}/settings.py", "w") as f:
            f.write(CONTENTS_IN_SETTINGS)

    # create main.py file
    if f"main.py" not in os.listdir(pjt_name):
        with open(f"{pjt_name}/main.py", "w") as f:
            f.write(CONTENTS_IN_MAIN)

    return None

def createapp(app_name: str) -> None:
    # check main folders for jknife
    for folder_name in FOLDER_LIST:
       try:
           if os.listdir(folder_name):
                with open(f"{folder_name}/__init__.py", "w") as f:
                    f.write("")

       except FileNotFoundError:
           print(ERROR_MSG_START_PROJECT)
           return None

    # create app.py in 'models' folder
    with open(f"models/{app_name}.py", "w") as f:
        f.write(MODULE_IMPORT_STRING_MODELS)

    with open(f"routers/{app_name}.py", "w") as f:
        f.write(MODULE_IMPORT_STRING_ROUTERS.format(app_name, app_name))

    with open(f"views/{app_name}.py", "w") as f:
        f.write(MODULE_IMPORT_STRING_VIEWS)

    return None

def help_msg():
    print(HELP_MSG)
    return None

def run_server(options: list):
    args = "".join([ option.replace("=", "") for option in options ])
    print(f"uvicorn main:app {args}")
    return None

def main() -> None:
    read_command: list = sys.argv

    try:
        sub_command = read_command[1]

        if sub_command == "startproject":
            startproject(pjt_name=read_command[2])
            return None

        elif sub_command == "createapp":
            createapp(app_name=read_command[2])
            return None

        elif sub_command == "run":
            run_server(read_command[2:])
            return None

    except IndexError:
        pass

    help_msg()
    return None


if __name__ == "__main__":
    main()