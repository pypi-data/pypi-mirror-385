######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.12.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-20T19:13:33.280600                                                            #
######################################################################################################

from __future__ import annotations

import abc
import metaflow
import typing
if typing.TYPE_CHECKING:
    import abc
    import metaflow.plugins.secrets
    import metaflow.exception

from ..secrets import SecretsProvider as SecretsProvider
from ...exception import MetaflowException as MetaflowException
from .azure_credential import create_cacheable_azure_credential as create_cacheable_azure_credential

AZURE_KEY_VAULT_PREFIX: None

class MetaflowAzureKeyVaultBadVault(metaflow.exception.MetaflowException, metaclass=type):
    """
    Raised when the secretid is fully qualified but does not have the right key vault domain
    """
    ...

class MetaflowAzureKeyVaultBadSecretType(metaflow.exception.MetaflowException, metaclass=type):
    """
    Raised when the secret type is anything except secrets
    """
    ...

class MetaflowAzureKeyVaultBadSecretPath(metaflow.exception.MetaflowException, metaclass=type):
    """
    Raised when the secret path does not match to expected length
    """
    ...

class MetaflowAzureKeyVaultBadSecretName(metaflow.exception.MetaflowException, metaclass=type):
    """
    Raised when the secret name does not match expected pattern
    """
    ...

class MetaflowAzureKeyVaultBadSecretVersion(metaflow.exception.MetaflowException, metaclass=type):
    """
    Raised when the secret version does not match expected pattern
    """
    ...

class MetaflowAzureKeyVaultBadSecret(metaflow.exception.MetaflowException, metaclass=type):
    """
    Raised when the secret does not match supported patterns in Metaflow
    """
    ...

class AzureKeyVaultSecretsProvider(metaflow.plugins.secrets.SecretsProvider, metaclass=abc.ABCMeta):
    def get_secret_as_dict(self, secret_id, options = {}, role = None):
        ...
    ...

