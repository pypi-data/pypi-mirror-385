# import packages from default or pip library
from datetime import datetime, timezone
from typing_extensions import (Annotated,
                               Doc,
                               Optional,
                               deprecated)
from uuid import UUID, uuid4
from mongoengine import Document, UUIDField, DateTimeField


# import packages from this framework


# define Class for Common MongoDB
@deprecated("MongoDB does not requires to set uuid manually.")
class UUIDMixin(Document):
    meta = {'abstract': True}

    id: Annotated[UUID,
    Doc("UUID format id for each table row.")] = UUIDField(primary_key=True, default=None, unique=True)


class RegisterDateTimeMixin(Document):
    meta = {'abstract': True}

    register_dt: Annotated[datetime,
    Doc("Datetime that the row was added at.")] = DateTimeField(null=False, default=None)


class UpdateDateTimeMixin(Document):
    meta = {'abstract': True}

    update_dt: Annotated[Optional[datetime],
    Doc("Datetime that the row was updated at.")] = DateTimeField(null=False, default=None)


# define function to control MongoDB document event
# please follow the procedure below
# create event handler function with name starting with _.
# event handler function must have 3 args: sender, document, **kwargs)
# each db column can get from 'document'
# import pre_init or pre_save from 'mongoengine.signals' in your model file.
# pre_init.connect(EVNET_HANDLER_FUNC_NAME, sender=TABLE_CLASS_NAME)
@deprecated("MongoDB does not requires to set uuid manually.")
def _assign_uuid(sender, document, **kwargs) -> None:
    if document.id is None:
        document.id = uuid4()
    return None

def _assign_register_datetime(sender, document, **kwargs) -> None:
    if document.register_dt is None:
        document.register_dt = datetime.now(tz=timezone.utc)
    return None

def _assign_update_datetime(sender, document, **kwargs) -> None:
    document.update_dt = datetime.now(tz=timezone.utc)
    return None
