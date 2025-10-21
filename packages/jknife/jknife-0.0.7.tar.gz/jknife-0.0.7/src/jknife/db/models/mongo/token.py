# import packages from default or pip library
from datetime import datetime, timedelta, timezone
from typing_extensions import Annotated, Doc
from mongoengine import Document, DateTimeField, StringField, pre_init

# import packages from this framework
from settings import AUTHENTICATION

# settings
TOKEN_VALID_TIME: int = AUTHENTICATION.get("token").get("token_valid_time")


# define classes
class AccessTokenMixin(Document):
    meta = {'abstract': True}

    access_token: Annotated[str,
    Doc("This is a access token that will be stored in DB or somewhere")] = StringField(primary_key=True,
                                                                                        null=False,
                                                                                        unique=True)


class TokenValidDateTime(Document):
    meta = {'abstract': True}

    issued_dt: Annotated[datetime,
    Doc("datetime when the token issued.")] = DateTimeField(null=False)
    expiration_dt: Annotated[datetime,
    Doc("datetime when the token will be expired.")] = DateTimeField(null=False)


class RefreshTokenMixin(Document):
    meta = {'abstract': True}

    refresh_token: Annotated[str,
    Doc("This is a refresh token that will be used for issuing access token again.")] = StringField(null=False,
                                                                                                    unique=True)


class JWTTokens(RefreshTokenMixin, AccessTokenMixin):
    meta = {'abstract': True}

    token_type: Annotated[str,
    Doc("Token type that used in this class.")] = StringField(null=False,
                                                              default="Bearer")


# define function to control MongoDB document event
# please follow the procedure below
# create event handler function with name starting with _.
# event handler function must have 3 args: sender, document, **kwargs)
# each db column can get from 'document'
# import pre_init or pre_save from 'mongoengine.signals' in your model file.
# pre_init.connect(EVNET_HANDLER_FUNC_NAME, sender=TABLE_CLASS_NAME)
def _fill_token_datetime_field(sender, document, **kwargs) -> None:
    if document.issued_dt is None:
        document.issued_dt = datetime.now(tz=timezone.utc)

    if document.expiration_dt is None:
        document.expiration_dt = document.issued_dt + timedelta(minutes=TOKEN_VALID_TIME)

    return None