# import packages from default or pip library
from typing_extensions import Annotated, Doc
from pydantic import BaseModel

# import packages from this framework


# Error Mixin Class
class ErrMsgMixin(BaseModel):
    msg: Annotated[str,
    Doc("message for error")]


class ErrMsgTypeMixin(BaseModel):
    type: Annotated[str,
    Doc("customised message type. for example, 'password_mismatch' or 'unauthorised access'.")]


class ErrMsgBoolResultMixin(BaseModel):
    result: Annotated[bool, Doc("result of calling API in bool type.")] = False


class FieldValidationErrMixin(BaseModel):
    field: Annotated[str,
    Doc("field name which has an error.")]


# Error Model
class DefaultErrorMsgView(ErrMsgMixin):
    pass


class ErrMsgWithTypeView(ErrMsgTypeMixin, DefaultErrorMsgView):
    pass


class ErrMsgWithTypeAndResultView(ErrMsgBoolResultMixin, ErrMsgWithTypeView):
    pass