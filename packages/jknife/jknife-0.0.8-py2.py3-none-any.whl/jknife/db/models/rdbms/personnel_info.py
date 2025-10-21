# import packages from default or pip library
from datetime import date
from typing_extensions import Annotated, Doc
from sqlmodel import SQLModel, Field
from fastapi.exceptions import RequestValidationError
from pycountry import countries as pycountries

# import packages from this framework


# define Class for Common SQLModel
class AddressMixin(SQLModel):
    address: Annotated[str,
    Doc("Address.")] = Field(nullable=False)


class BirthdateMixin(SQLModel):
    birthdate: Annotated[date,
    Doc("User's Birthdate.")] = Field(nullable=False)


class CPNumMixin(SQLModel):
    cp_num: Annotated[str,
    Doc("cellphone number.")] = Field(nullable=False)


class EmailMixin(SQLModel):
    email: Annotated[str,
    Doc("email address. this can replace username for signup and signin.")] = Field(nullable=False, unique=True)


class FirstnameMixin(SQLModel):
    firstname: Annotated[str,
    Doc("First name of application user.")] = Field(nullable=False, index=True)


class LastnameMixin(SQLModel):
    lastname: Annotated[str,
    Doc("Last name of application user.")] = Field(nullable=False, index=True)


class NationMixin(SQLModel):
    nation: Annotated[str,
    Doc("the nation that user came from.")] = Field(nullable=False)


class NicknameMixin(SQLModel):
    nickname: Annotated[str,
    Doc("User's nickname that used in this application.")] = Field(unique=True, index=True)


class PostalCodeMixin(SQLModel):
    postal_code: Annotated[str,
    Doc("postal number of address.")] = Field(nullable=False)


# define function to control SQL event
# please follow the procedure below
# use decorator 'event.listens_for()' for event handling function
# event handler function must have 3 args: mapper, connection and target)
# in your model file, import listens_for from 'sqlalchemy.event'
# event.listens_for(target=TARGET_TABLE_CLASS_NAME, identifier=['before_insert', 'before_update',...])
def _convert_country_to_alpha2(mapper, connection, target):
    if target.nation is not None and len(target.nation) != 2:
        try:
            target.nation = pycountries.get(name=target.nation).alpha_2
        except AttributeError:
            raise RequestValidationError(errors={"input": "nation", "msg": "please input official country name."})
    return None

def _convert_country_to_alpha3(mapper, connection, target):
    if target.nation is not None and len(target.nation) != 3:
        try:
            target.nation = pycountries.get(name=target.nation).alpha_3
        except AttributeError:
            raise RequestValidationError(errors={"input": "nation", "msg": "please input official country name."})
    return None

def _lower_firstname(mapper, connection, target) -> None:
    if target.firstname is not None:
        target.firstname = target.firstname.lower()
    return None

def _lower_lastname(mapper, connection, target) -> None:
    if target.lastname is not None:
        target.lastname = target.lastname.lower()
    return None

