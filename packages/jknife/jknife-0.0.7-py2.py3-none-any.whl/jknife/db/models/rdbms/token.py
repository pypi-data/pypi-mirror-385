# import packages from default or pip library
from datetime import datetime, timedelta, timezone
from typing_extensions import Annotated, Doc
from sqlmodel import SQLModel, Field

# import packages from this framework
from settings import AUTHENTICATION

# settings
TOKEN_VALID_TIME: int = AUTHENTICATION.get("token").get("token_valid_time")


# define classes
class AccessTokenMixin(SQLModel):
    access_token: Annotated[str,
    Doc("This is a access token that will be stored in DB or somewhere")] = Field(primary_key=True,
                                                                                  nullable=False,
                                                                                  unique=True)


class RefreshTokenMixin(SQLModel):
    refresh_token: Annotated[str,
    Doc("This is a refresh token that will be used for issuing access token again.")] = Field(nullable=False,
                                                                                              unique=True)


class TokenValidDateTimeMixin(SQLModel):
    issued_dt: Annotated[datetime,
    Doc("datetime when the token issued.")] = Field(nullable=False)
    expiration_dt: Annotated[datetime,
    Doc("datetime when the token will be expired.")] = Field(nullable=False)


class JWTTokens(RefreshTokenMixin, AccessTokenMixin):
    token_type: Annotated[str,
    Doc("Token type that used in this class.")] = Field(nullable=False,
                                                        default="Bearer")


# define function to control SQL event
# please follow the procedure below
# use decorator 'event.listens_for()' for event handling function
# event handler function must have 3 args: mapper, connection and target)
# in your model file, import listens_for from 'sqlalchemy.event'
# event.listens_for(target=TARGET_TABLE_CLASS_NAME, identifier=['before_insert', 'before_update',...])
def _fill_token_datetime_field(mapper, connection, target) -> None:
    if target.issued_dt is None:
        target.issued_dt = datetime.now(tz=timezone.utc)

    if target.expired is None:
        target.expired_dt = target.issued_dt + timedelta(minutes=TOKEN_VALID_TIME)

    return None
