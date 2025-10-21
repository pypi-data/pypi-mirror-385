# import packages from default or pip library
from datetime import datetime
from typing_extensions import Annotated, Doc
from pydantic import BaseModel, field_validator

# import packages from this framework
from src.jknife.views.personnel_info import EmailInputViewMixin
from src.jknife.dependencies.users import validate_password_policy


# define mixin class
class UsernameInputViewMixin(BaseModel):
    username: Annotated[str,
    Doc("username")]


class InputPasswordViewMixin(BaseModel):
    password: Annotated[str,
    Doc("password for user")]


class LastSigninDateTimeViewMixin(BaseModel):
    last_signin_dt: Annotated[datetime | None,
    Doc("User's last signin datetime.")] = None


class SigninFailMixin(BaseModel):
    is_active: Annotated[bool,
    Doc("show whether the user is activated or not.")]
    signin_fail: Annotated[int,
    Doc("If the user fail to login, this value will be incremented.")]


# define common view class
class ChangePasswordView(InputPasswordViewMixin):
    new_password: Annotated[str,
    Doc("New password for changing password")]

    @field_validator('new_password', mode='before')
    @classmethod
    def check_new_password(cls, value) -> str:
        return validate_password_policy(password=value, field="new_password")


class DefaultSignupView(InputPasswordViewMixin, UsernameInputViewMixin):
    password: Annotated[str,
    Doc("password for user")]

    @field_validator('password', mode='before')
    @classmethod
    def check_password(cls, value) -> str:
        return validate_password_policy(password=value)


class DefaultEmailSignupView(InputPasswordViewMixin, EmailInputViewMixin):
    password: Annotated[str,
    Doc("password for user")]

    @field_validator('password', mode='before')
    @classmethod
    def check_password(cls, value) -> str:
        return validate_password_policy(password=value)


class UsernameSigninView(InputPasswordViewMixin, UsernameInputViewMixin):
    pass


class EmailSigninView(InputPasswordViewMixin, EmailInputViewMixin):
    pass
