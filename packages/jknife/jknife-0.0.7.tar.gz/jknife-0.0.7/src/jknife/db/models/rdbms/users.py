# import packages from default or pip library
import hashlib
from datetime import datetime, timezone
from typing_extensions import Annotated, Doc
from sqlmodel import SQLModel, Field

# import packages from this framework
from settings import PASSWORD_POLICIES


# password encryption algorithm
ENCRYPT_TYPE: str = PASSWORD_POLICIES.get("encrypt_type")


# define Class for Common SQLModel
class LastSigninDateTimeMixin(SQLModel):
    last_signin_dt: Annotated[datetime,
    Doc("User's last signin datetime.")] = Field(nullable=True, default=None)

    def update_signin_dt(self) -> None:
        self.last_signin_dt = datetime.now(tz=timezone.utc)
        return None


class SigninFailMixin(SQLModel):
    is_active: Annotated[bool,
    Doc("show whether the user is activated or not.")] = Field(nullable=False, default=False)
    signin_fail: Annotated[int,
    Doc("If the user fail to login, this value will be incremented.")] = Field(nullable=False, default=0, ge=0, le=5)

    def activate_user(self) -> None:
        self.is_active = True
        self.__init_signin_fail_count()
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

    def __init_signin_fail_count(self) -> None:
        self.signin_fail = 0
        return None


class IsAdminMixin(SQLModel):
    is_admin: Annotated[bool,
    Doc("show whether the user is admin or not.")] = Field(nullable=False, default=False)

    def grant_admin(self) -> None:
        self.is_admin = True
        return None

    def revoke_admin(self) -> None:
        self.is_admin = False
        return None


class PasswordMixin(SQLModel):
    password: Annotated[str,
    Doc("password for application user. it is recommended to store password after encrypting.")] = Field(nullable=False, unique=False, min_length=32)

    def encrypt_password(self, enc_type:str=ENCRYPT_TYPE):
        self.password = encrypt_password(password=self.password, enc_type=enc_type)


class UsernameMixin(SQLModel):
    username: Annotated[str,
    Doc("username for application user. if you want to replace it to email, refer to 'contact' module.")] = Field(nullable=False, unique=True, min_length=8)


# define function for users
def encrypt_password(password:str, enc_type:str=ENCRYPT_TYPE) -> str:
    if enc_type not in hashlib.algorithms_available:
        raise ValueError(f"'{enc_type}' is not supported hash method in this application. Password will be encrypted with default hash.")

    return getattr(hashlib, enc_type)(string=password.encode("utf-8")).hexdigest()


# define function to control SQL event
# please follow the procedure below
# use decorator 'event.listens_for()' for event handling function
# event handler function must have 3 args: mapper, connection and target)
# in your model file, import listens_for from 'sqlalchemy.event'
# event.listens_for(target=TARGET_TABLE_CLASS_NAME, identifier=['before_insert', 'before_update',...])

