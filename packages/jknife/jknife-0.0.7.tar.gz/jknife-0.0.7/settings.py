# this file is charge of config for custom fastapi.

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
