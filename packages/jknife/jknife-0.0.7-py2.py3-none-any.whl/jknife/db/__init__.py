# import packages from default or pip library
import importlib, os, redis
from contextlib import asynccontextmanager
from typing_extensions import Annotated, Doc
from fastapi import FastAPI
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import OperationalError
from sqlmodel import SQLModel, Session, create_engine
from mongoengine import connect

# import packages from this framework
from ..logging import LoggerMgmt
from settings import *


# Define supported database
SUPPORT_DATABASE: dict = {
    "none": {"type": "none", "engine": "none"},
    "postgresql": {"type": "dbms", "engine": "rdbms"},
    "mysql": {"type": "dbms", "engine": "rdbms"},
    "mongo": {"type": "dbms", "engine": "mongo"},
    "sqlite": {"type": "sqlite", "engine": "rdbms"},
}

# set logger
logger = LoggerMgmt(logger_names=DB_LOGGER_LIST or ["db"])


# define redis instance
redis_host: str = DATABASE.get("redis").get("host")
redis_port: int = DATABASE.get("redis").get("port")
redis_connector = redis.Redis(host=redis_host, port=redis_port)
if redis_host is not None:
    try:
        redis_connector.ping()
        if not DEBUG_MODE:
            redis_connector.flushdb()

    except redis.exceptions.ConnectionError:
        logger.warning(msg="Can not connect to Redis server. Please check your server's information.")


# define DBConnector
class DBConnector:
    """
    This class will make the application connect to database server which is designed in settings.py
    The list of supported database is written in SUPPORT_DATABASE above.
    """

    def __init__(self):
        self.__type: Annotated[str,
        Doc("Assign the database type. It must be one of value in SUPPORT_DB_TYPES.")] = DATABASE.get("type") or "none"
        self.__db_info: Annotated[dict | None,
        Doc(f"type of database defined in SUPPORTED_DATABASE")] = SUPPORT_DATABASE.get(self.__type)

        # import table classes in models_bak for sqlmodel.
        if self.__db_info.get("engine") == "rdbms":
            for file in os.listdir(os.path.abspath("models")):
                if not file.startswith("__") and file.endswith(".py"):
                    importlib.import_module(f"models_bak.{file.split('.')[0]}")

        # get connection information from settings.py
        if self.__db_info is not None:
            self.__conn_info: Annotated[dict | None,
            Doc("the type of database from DATABASE in settings.py")] = DATABASE.get(self.__db_info.get("type"))

            if self.__type in SUPPORT_DATABASE.keys() and self.__conn_info is not None:

                # for normal DBMS server
                if SUPPORT_DATABASE.get(self.__type).get("type") == "dbms":
                    self.__db: Annotated[str,
                    Doc("The name of database that will be used for this projects")] = self.__conn_info.get("db")
                    self.__host: Annotated[str,
                    Doc("The name of database that will be used for this projects")] = self.__conn_info.get("host")
                    self.__port: Annotated[str,
                    Doc("The name of database that will be used for this projects")] = self.__conn_info.get("port")
                    self.__username: Annotated[str,
                    Doc("The name of database that will be used for this projects")] = self.__conn_info.get("username")
                    self.__password: Annotated[str,
                    Doc("The name of database that will be used for this projects")] = self.__conn_info.get("password")
                    self.__auth_source: Annotated[str,
                    Doc("This class member is for mongo. Input the name of database that the username came from.")] = self.__conn_info.get("auth_source")

                # for sqlite3
                elif SUPPORT_DATABASE.get(self.__type).get("type") == "filedb":
                    self.__sqlite3_filepath: Annotated[str,
                    Doc("This class member is for sqlite3 only. Input must be absolute or relative path.")] = self.__conn_info.get("sqlite_filepath")

                self.__engine: Annotated[Engine,
                Doc("engine will be used to get db session.")] = self.__create_engine()


    def __create_engine(self) -> Engine | None:
        args: Annotated[dict,
        Doc("Arguments for create_engine()")] = {"check_same_thread": False} \
            if SUPPORT_DATABASE.get("type") == "filedb" else {}
        logger.debug(f"DB connection arguments: {args}")

        url = f"{self.__type}://{self.__username}:{self.__password}@{self.__host}:{self.__port}/{self.__db}" \
            if SUPPORT_DATABASE.get(self.__type).get("type") == "dbms" else f"{self.__type}:///{self.__sqlite3_filepath}"
        logger.debug(f"DB connection URL: {url}")

        if SUPPORT_DATABASE.get(self.__type).get("engine") == "rdbms":
            logger.info(f"creating RDBMS engine for '{self.__type}' database...")
            return create_engine(url=url,
                                 echo=DEBUG_MODE,
                                 connect_args=args)

        # create mongo client module.
        connect(**self.__conn_info)
        return None

    @asynccontextmanager
    async def startup_db(self, app: FastAPI):
        if self.__type == "none":
            logger.debug("There is no database config.")
            yield

        else:
            if self.__type in SUPPORT_DATABASE:
                try:
                    if SUPPORT_DATABASE.get(self.__type).get("engine") == "rdbms":
                        SQLModel.metadata.create_all(bind=self.__engine)
                        logger.info(f"successfully connected to '{self.__type}' database!")

                    else:
                        logger.info(f"successfully created `{self.__type}` connecting module!")

                    yield

                except (OperationalError,) as e:
                    logger.error(f"Can not connect to DB server: '{self.__host}:{self.__port}/{self.__db}'")
                    return

            else:
                logger.warning(f"'{self.__type} is not supported database type.")
                return

    # return session for RDBMS
    def get_session(self):
        with Session(self.__engine) as session:
            yield session
