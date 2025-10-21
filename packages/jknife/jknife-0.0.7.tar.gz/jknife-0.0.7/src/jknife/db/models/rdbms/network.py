# import packages from default or pip library
from typing_extensions import Annotated, Doc
from sqlmodel import SQLModel, Field

# import packages from this framework


# define Class for Common SQLModel
class AllowIPsMixin(SQLModel):
    allow_ips: Annotated[list[str],
    Doc("Set IPv4 or IPv6 addresses or networks to allow user to access")] = Field(nullable=False,
                                                                                   default=["127.0.0.1"])


# define function to control SQL event
# please follow the procedure below
# use decorator 'event.listens_for()' for event handling function
# event handler function must have 3 args: mapper, connection and target)
# in your model file, import listens_for from 'sqlalchemy.event'
# event.listens_for(target=TARGET_TABLE_CLASS_NAME, identifier=['before_insert', 'before_update',...])
def _convert_ips_to_str(mapper, connection, target) -> None:
    if target.allow_ips is not None:
        target.allow_ips = [ str(ip) for ip in target.allow_ips ]
    return None