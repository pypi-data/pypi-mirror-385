######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-21T09:01:27.313451                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

from ...exception import MetaflowException as MetaflowException

class AirflowException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, msg):
        ...
    ...

class NotSupportedException(metaflow.exception.MetaflowException, metaclass=type):
    ...

