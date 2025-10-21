# import packages from default or pip library
from datetime import date
from typing_extensions import Annotated, Doc
from mongoengine import Document, DateField, StringField, EmailField
from fastapi.exceptions import RequestValidationError
from pycountry import countries as pycountries

# import packages from this framework


# define Class for Common SQLModel
class AddressMixin(Document):
    meta = {'abstract': True}

    address: Annotated[str,
    Doc("Address.")] = StringField(null=False)


class BirthdateMixin(Document):
    meta = {'abstract': True}

    birthdate: Annotated[date,
    Doc("User's Birthdate.")] = DateField(null=False)


class CPNumMixin(Document):
    meta = {'abstract': True}

    cp_num: Annotated[str,
    Doc("cellphone number.")] = StringField(null=False)


class EmailMixin(Document):
    meta = {'abstract': True}

    email: Annotated[str,
    Doc("email address. this can replace username for signup and signin.")] = EmailField(null=False, unique=True)


class FirstnameMixin(Document):
    meta = {'abstract': True}

    firstname: Annotated[str,
    Doc("First name of application user.")] = StringField(null=False)


class LastnameMixin(Document):
    meta = {'abstract': True}

    lastname: Annotated[str,
    Doc("Last name of application user.")] = StringField(null=False)


class NationMixin(Document):
    meta = {'abstract': True}

    nation: Annotated[str,
    Doc("the nation that user came from.")] = StringField(null=False)


class NicknameMixin(Document):
    meta = {'abstract': True}

    nickname: Annotated[str,
    Doc("User's nickname that used in this application.")] = StringField(unique=True)


class PostalCodeMixin(Document):
    meta = {'abstract': True}

    postal_code: Annotated[str,
    Doc("postal number of address.")] = StringField(null=False)


# define function to control MongoDB document event
# please follow the procedure below
# create event handler function with name starting with _.
# event handler function must have 3 args: sender, document, **kwargs)
# each db column can get from 'document'
# import pre_init or pre_save from 'mongoengine.signals' in your model file.
# pre_init.connect(EVNET_HANDLER_FUNC_NAME, sender=TABLE_CLASS_NAME)
def _convert_country_to_alpha2(sender, document, **kwargs):
    if document.nation and len(document.nation) != 2:
        try:
            document.nation = pycountries.get(name=document.nation).alpha_2
        except AttributeError:
            raise RequestValidationError(errors={"input": "nation", "msg": "please input official country name."})

    return None

def _convert_country_to_alpha3(sender, document, **kwargs):
    if document.nation and len(document.nation) != 3:
        try:
            document.nation = pycountries.get(name=document.nation).alpha_3
        except AttributeError:
            raise RequestValidationError(errors={"input": "nation", "msg": "please input official country name."})

    return None

def _lower_firstname(sender, document, **kwargs) -> None:
    if document.firstname:
        document.firstname = document.firstname.lower()
    return None

def _lower_lastname(sender, document, **kwargs) -> None:
    if document.lastname:
        document.lastname = document.lastname.lower()
    return None
