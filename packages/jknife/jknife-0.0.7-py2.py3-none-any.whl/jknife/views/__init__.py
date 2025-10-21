# import packages from default or pip library
from datetime import datetime
from pydantic import BaseModel
from typing_extensions import Annotated, Doc, Optional
from uuid import UUID

# import packages from this framework


# define mixin class
class IdViewMixin(BaseModel):
    id: Annotated[int,
    Doc("Default integer id for each table row.")]


class UUIDViewMixin(BaseModel):
    id: Annotated[UUID,
    Doc("UUID format id for each table row.")]


class RegisterDateTimeViewMixin(BaseModel):
    register_dt: Annotated[Optional[datetime],
    Doc("Datetime that the row was added at.")]
