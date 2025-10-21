######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.12.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-20T19:13:33.260760                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

from ...exception import MetaflowException as MetaflowException

TYPE_CHECK_REGEX: str

class CardClassFoundException(metaflow.exception.MetaflowException, metaclass=type):
    """
    This exception is raised with MetaflowCard class is not present for a particular card type.
    """
    def __init__(self, card_name):
        ...
    ...

class TypeRequiredException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self):
        ...
    ...

class CardNotPresentException(metaflow.exception.MetaflowException, metaclass=type):
    """
    This exception is raised with a card is not present in the datastore.
    """
    def __init__(self, pathspec, card_type = None, card_hash = None, card_id = None):
        ...
    ...

class TaskNotFoundException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, pathspec_query, resolved_from, run_id = None):
        ...
    ...

class IncorrectCardArgsException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, card_type, args):
        ...
    ...

class UnrenderableCardException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, card_type, args):
        ...
    ...

class UnresolvableDatastoreException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, task):
        ...
    ...

class IncorrectArgumentException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, obj_type):
        ...
    ...

class IncorrectPathspecException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, pthspec):
        ...
    ...

class ComponentOverwriteNotSupportedException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, component_id, card_id, card_type):
        ...
    ...

