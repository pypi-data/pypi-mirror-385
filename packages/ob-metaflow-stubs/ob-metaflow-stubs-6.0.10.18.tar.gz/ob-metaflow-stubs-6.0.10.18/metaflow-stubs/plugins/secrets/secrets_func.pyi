######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.12.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-20T19:13:33.275395                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import typing

from ...exception import MetaflowException as MetaflowException
from .secrets_spec import SecretSpec as SecretSpec
from .utils import get_secrets_backend_provider as get_secrets_backend_provider

DEFAULT_SECRETS_ROLE: None

def get_secret(source: typing.Union[str, typing.Dict[str, typing.Any]], role: typing.Optional[str] = None) -> typing.Dict[str, str]:
    """
    Get secret from source
    
    Parameters
    ----------
    source : Union[str, Dict[str, Any]]
        Secret spec, defining how the secret is to be retrieved
    role : str, optional
        Role to use for fetching secrets
    """
    ...

