######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.12.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-20T19:13:33.245060                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.mf_extensions.obcheckpoint.plugins.machine_learning_utilities.datastructures

from .core import Checkpointer as Checkpointer
from .core import WriteResolver as WriteResolver
from .core import ReadResolver as ReadResolver
from ..datastructures import CheckpointArtifact as CheckpointArtifact

TYPE_CHECKING: bool

CHECKPOINT_UID_ENV_VAR_NAME: str

DEFAULT_NAME: str

def load_checkpoint(checkpoint: typing.Union[metaflow.mf_extensions.obcheckpoint.plugins.machine_learning_utilities.datastructures.CheckpointArtifact, dict, str], local_path: str):
    ...

