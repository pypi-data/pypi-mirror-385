# import packages from default or pip library
from typing_extensions import Annotated, Doc
from pydantic import BaseModel


# import packages from this framework



# define Class for Common SQLModel
class DefaultJWTTokenView(BaseModel):
    """
    This class is a view template for returning JWT tokens information.
    Read Only.
    """

    access_token: Annotated[str,
    Doc("This is an access token string for authenticated user")]
    refresh_token: Annotated[str,
    Doc("This is a token string for reissuing access token")]
    token_type: Annotated[str,
    Doc("Token type that used in this class. Default is 'Bearer'")] = "Bearer"
