######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13                                                                                #
# Generated on 2025-10-20T17:35:52.592757                                                            #
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

