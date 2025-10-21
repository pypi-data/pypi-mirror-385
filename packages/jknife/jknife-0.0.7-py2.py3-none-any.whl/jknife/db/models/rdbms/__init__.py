# import packages from default or pip library
from datetime import datetime, timezone
from typing_extensions import (Annotated,
                               Doc,
                               Optional)
from uuid import UUID, uuid4
from sqlmodel import (SQLModel,
                      Field)

# import packages from this framework


# define Class for Common SQLModel
class IdMixin(SQLModel):
    id: Annotated[int,
    Doc("Default integer id for each table row.")] = Field(primary_key=True, default=None)


class UUIDMixin(SQLModel):
    id: Annotated[UUID,
    Doc("UUID format id for each table row.")] = Field(primary_key=True, default=None)


class RegisterDateTimeMixin(SQLModel):
    register_dt: Annotated[datetime,
    Doc("Datetime that the row was added at.")] = Field(nullable=False, default=None)


class UpdateDateTimeMixin(SQLModel):
    update_dt: Annotated[Optional[datetime],
    Doc("Datetime that the row was updated at.")] = Field(nullable=True, default=None)


# define function to control SQL event
# please follow the procedure below
# use decorator 'event.listens_for()' for event handling function
# event handler function must have 3 args: mapper, connection and target)
# in your model file, import listens_for from 'sqlalchemy.event'
# event.listens_for(target=TARGET_TABLE_CLASS_NAME, identifier=['before_insert', 'before_update',...])
def _assign_register_datetime(mapper, connection, target) -> None:
    if target.register_dt is None:
        target.register_dt = datetime.now(tz=timezone.utc)
    return None

def _assign_update_datetime(mapper, connection, target) -> None:
    if target.update_dt is not None:
        target.update_dt = datetime.now(tz=timezone.utc)
    return None

def _assign_uuid(mapper, connection, target) -> None:
    if target.id is None:
        target.id = uuid4()
    return None