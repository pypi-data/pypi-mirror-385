# import packages from default or pip library
from fastapi.exceptions import RequestValidationError

# import packages from this framework
from settings import PASSWORD_POLICIES


# settings
MIN_LENGTH: int = PASSWORD_POLICIES.get("min_length")
SPECIAL_CHARS: str = "!@#$%^&*()_-+=~`\'\";:\\|<>,.?/"


# define password policy functions
def password_minlen(password: str, field: str = "password"):
    if len(password) >= MIN_LENGTH:
        return password

    raise RequestValidationError(errors={"input": field,
                                         "msg": f"{field} must be at least 8 chars"})


def password_upchar(password: str, field: str = "password") -> str:
    for c in password:
        if c.isupper():
            return password

    raise RequestValidationError(errors={"input": field,
                                         "msg": f"{field} must contain at least one upper character"})

def password_lowchar(password: str, field: str = "password") -> str:
    for c in password:
        if c.islower():
            return password

    raise RequestValidationError(errors={"input": field,
                                         "msg": f"{field} must contain at least one lower character"})


def password_number(password: str, field: str = "password") -> str:
    for c in password:
        if c.isnumeric():
            return password

    raise RequestValidationError(errors={"input": field,
                                         "msg": f"{field} must contain at least one number"})


def password_special(password: str, field: str = "password") -> str:
    for c in password:
        if c in SPECIAL_CHARS:
            return password

    raise RequestValidationError(errors={"input":field,
                                         "msg":f"{field} must contain at least one special character"})


# define dependencies functions
def validate_password_policy(password: str, field: str = "password") -> str:
    policy_mapping: dict = {
        "PASSWORD_MINLEN": password_minlen,
        "PASSWORD_UPCHAR": password_upchar,
        "PASSWORD_LOWCHAR": password_lowchar,
        "PASSWORD_NUMBER": password_number,
        "PASSWORD_SPECIAL": password_special,
    }
    validate_list: list = PASSWORD_POLICIES.get("compliance")

    if len(validate_list) == 0:
        return password

    for func in validate_list:
        tmp = policy_mapping.get(func)
        if tmp is not None and callable(tmp):
            tmp(password=password, field=field)

    return password
