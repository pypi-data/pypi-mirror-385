# import packages from default or pip library
from datetime import date
from typing_extensions import Annotated, Doc
from pydantic import BaseModel, EmailStr

# import packages from this framework


# define mixin class
class BirthdateViewMixin(BaseModel):
    birthdate: Annotated[date,
    Doc("user's birthdate")]


class CPNumViewMixin(BaseModel):
    cp_num: Annotated[str,
    Doc("cellphone number.")]


class EmailInputViewMixin(BaseModel):
    email: Annotated[EmailStr,
    Doc("email address for user. it can be replaced username.")]


class FirstNameViewMixin(BaseModel):
    firstname: Annotated[str,
    Doc("firstname of user")]


class LastNameViewMixin(BaseModel):
    lastname: Annotated[str,
    Doc("lastname of user")]


class NationViewMixin(BaseModel):
    nation: Annotated[str,
    Doc("the nation that user came from.")]


class PostalCodeViewMixin(BaseModel):
    postal_code: Annotated[str,
    Doc("postal number of address.")]
