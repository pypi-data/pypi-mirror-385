# import packages from default or pip library
from typing_extensions import Annotated, Doc
from mongoengine import Document, ListField, pre_save

# import packages from this framework


# define Class for Common SQLModel
class AllowIPsMixin(Document):
    meta = {'abstract': True}

    allow_ips: Annotated[list[str],
    Doc("Set IPv4 or IPv6 addresses or networks to allow user to access")] = ListField(null=False,
                                                                                       default=["127.0.0.1"])


# define function to control MongoDB document event
# please follow the procedure below
# create event handler function with name starting with _.
# event handler function must have 3 args: sender, document, **kwargs)
# each db column can get from 'document'
# import pre_init or pre_save from 'mongoengine.signals' in your model file.
# pre_init.connect(EVNET_HANDLER_FUNC_NAME, sender=TABLE_CLASS_NAME)
def _convert_ips_to_str(sender, document, **kwargs) -> None:
    if document.allow_ip:
        document.allow_ip = [ str(ip) for ip in document.allow_ip ]
    return None
