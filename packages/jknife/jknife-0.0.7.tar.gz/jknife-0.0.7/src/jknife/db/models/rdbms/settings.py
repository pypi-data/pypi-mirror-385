# import packages from default or pip library
from pycountry import languages as pylanguage
from typing_extensions import Annotated, Doc
from sqlmodel import SQLModel, Field

# import packages from this framework


# define Class for Common SQLModel
class AllowMaxAccessSettingMixin(SQLModel):
    allow_max_access: Annotated[int,
    Doc("user setting for max access during trying sign in.")] = Field(nullable=False, default=5, ge=3, le=5)


class LanguageSettingMixin(SQLModel):
    language: Annotated[str,
    Doc("language setting for application user.")] = Field(nullable=False)


class DarkModeSettingMixin(SQLModel):
    is_dark_mode: Annotated[bool,
    Doc("light or dark mode for application user.")] = Field(nullable=False, default=False)


# define function to control SQL event
# please follow the procedure below
# use decorator 'event.listens_for()' for event handling function
# event handler function must have 3 args: mapper, connection and target)
# in your model file, import listens_for from 'sqlalchemy.event'
# event.listens_for(target=TARGET_TABLE_CLASS_NAME, identifier=['before_insert', 'before_update',...])
def _convert_language_to_alpha2(mapper, connection, target) -> None:
    if target.language is not None:
        target.language = pylanguage.get(name=target.language).alpha_2
    return None

def _convert_language_to_alpha3(mapper, connection, target) -> None:
    if target.language is not None:
        target.language = pylanguage.get(name=target.language).alpha_3
    return None