######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-21T09:01:27.312570                                                            #
######################################################################################################

from __future__ import annotations


from ...exception import MetaflowException as MetaflowException
from .utils import get_default_secrets_backend_type as get_default_secrets_backend_type

class SecretSpec(object, metaclass=type):
    def __init__(self, secrets_backend_type, secret_id, options = {}, role = None):
        ...
    @property
    def secrets_backend_type(self):
        ...
    @property
    def secret_id(self):
        ...
    @property
    def options(self):
        ...
    @property
    def role(self):
        ...
    def to_json(self):
        """
        Mainly used for testing... not the same as the input dict in secret_spec_from_dict()!
        """
        ...
    def __str__(self):
        ...
    @staticmethod
    def secret_spec_from_str(secret_spec_str, role):
        ...
    @staticmethod
    def secret_spec_from_dict(secret_spec_dict, role):
        ...
    ...

