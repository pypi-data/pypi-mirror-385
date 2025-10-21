# import modules from python library
import importlib, os
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


# import required objects from projects
from src.jknife.db import DBConnector
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
for router in os.listdir(os.path.abspath(path="routers")):
    if not router.startswith("__"):
        tmp_module = importlib.import_module(name=f"routers.{router.split('.')[0]}")
        app.include_router(router=tmp_module.router,
                           prefix=MAIN_URL)
