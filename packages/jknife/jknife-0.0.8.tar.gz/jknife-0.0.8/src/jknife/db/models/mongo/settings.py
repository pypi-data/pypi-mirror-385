# import packages from default or pip library
from pycountry import languages as pylanguage
from typing_extensions import Annotated, Doc
from mongoengine import Document, BooleanField, IntField, StringField
from fastapi.exceptions import RequestValidationError

# import packages from this framework


# define Class for Common SQLModel
class AllowMaxAccessSettingMixin(Document):
    meta = {'abstract': True}

    allow_max_access: Annotated[int,
    Doc("user setting for max access during trying sign in.")] = IntField(null=False, default=5, min_value=3, max_value=5)


class LanguageSettingMixin(Document):
    meta = {'abstract': True}

    language: Annotated[str,
    Doc("language setting for application user.")] = StringField(null=False)

    _alpha_code_type: Annotated[str,
    Doc("assign 'alpha_2' or 'alpha_3'. default is 'alpha_2'")] = "alpha_2"


class DarkModeSettingMixin(Document):
    meta = {'abstract': True}

    is_dark_mode: Annotated[bool,
    Doc("light or dark mode for application user.")] = BooleanField(null=False, default=False)


# define function to control MongoDB document event
# please follow the procedure below
# create event handler function with name starting with _.
# event handler function must have 3 args: sender, document, **kwargs)
# each db column can get from 'document'
# import pre_init or pre_save from 'mongoengine.signals' in your model file.
# pre_init.connect(EVNET_HANDLER_FUNC_NAME, sender=TABLE_CLASS_NAME)
def _convert_language_to_alpha2(sender, document, **kwargs):
    if document.language and len(document.language) != 2:
        try:
            document.language = pylanguage.get(name=document.language).alpha_2
        except AttributeError:
            raise RequestValidationError(errors={"input": "nation", "msg": "please input official country name."})

    return None

def _convert_language_to_alpha3(sender, document, **kwargs):
    if document.language and len(document.language) != 3:
        try:
            document.language = pylanguage.get(name=document.language).alpha_3
        except AttributeError:
            raise RequestValidationError(errors={"input": "nation", "msg": "please input official country name."})

    return None
