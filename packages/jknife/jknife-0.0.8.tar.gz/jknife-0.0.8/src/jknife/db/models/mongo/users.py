# import packages from default or pip library
from datetime import datetime, timezone
from typing_extensions import Annotated, Doc
from mongoengine import Document, BooleanField, DateTimeField, IntField, StringField

# import packages from this framework
from src.jknife.db.models.rdbms.users import encrypt_password


# define Class for Common SQLModel
class LastSigninDateTimeMixin(Document):
    meta = {'abstract': True}

    last_signin_dt: Annotated[datetime,
    Doc("User's last signin datetime.")] = DateTimeField(null=True, default=None)

    def update_signin_dt(self) -> None:
        self.last_signin_dt = datetime.now(tz=timezone.utc)
        return None


class SigninFailMixin(Document):
    meta = {'abstract': True}

    is_active: Annotated[bool,
    Doc("show whether the user is activated or not.")] = BooleanField(null=False, default=False)
    signin_fail: Annotated[int,
    Doc("If the user fail to login, this value will be incremented.")] = IntField(null=False, default=0, ge=0, le=5)

    def init_signin_fail_count(self) -> None:
        self.signin_fail = 0
        return None

    def activate_user(self) -> None:
        self.is_active = True
        self.init_signin_fail_count()
        return None

    def deactivate_user(self) -> None:
        self.is_active = False
        return None

    def add_signin_fail_count(self, limit: int) -> None:
        if self.signin_fail < limit:
            self.signin_fail += 1

            if self.signin_fail == limit:
                self.deactivate_user()

        return None


class IsAdminMixin(Document):
    meta = {'abstract': True}

    is_admin: Annotated[bool,
    Doc("show whether the user is admin or not.")] = BooleanField(null=False, default=False)

    def grant_admin(self) -> None:
        self.is_admin = True
        return None

    def revoke_admin(self) -> None:
        self.is_admin = False
        return None


class PasswordMixin(Document):
    meta = {'abstract': True}

    password: Annotated[str,
    Doc("password for application user. it is recommended to store password after encrypting.")] = StringField(null=False, unique=False, min_length=32)

    def encrypt_password(self, enc_type:str="sha256"):
        self.password = encrypt_password(password=self.password, enc_type=enc_type)


class UsernameMixin(Document):
    meta = {'abstract': True}

    username: Annotated[str,
    Doc("username for application user. if you want to replace it to email, refer to 'contact' module.")] = StringField(null=False)


# define function to control MongoDB document event
# please follow the procedure below
# create event handler function with name starting with _.
# event handler function must have 3 args: sender, document, **kwargs)
# each db column can get from 'document'
# import pre_init or pre_save from 'mongoengine.signals' in your model file.
# pre_init.connect(EVNET_HANDLER_FUNC_NAME, sender=TABLE_CLASS_NAME)