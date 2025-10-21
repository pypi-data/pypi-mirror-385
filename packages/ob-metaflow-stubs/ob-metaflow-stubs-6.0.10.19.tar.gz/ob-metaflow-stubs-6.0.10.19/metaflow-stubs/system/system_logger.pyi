######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-21T09:01:27.291199                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import typing
    import metaflow.event_logger


class SystemLogger(object, metaclass=type):
    def __init__(self):
        ...
    def __del__(self):
        ...
    def init_system_logger(self, flow_name: str, logger: "metaflow.event_logger.NullEventLogger"):
        ...
    @property
    def logger(self) -> typing.Optional["metaflow.event_logger.NullEventLogger"]:
        ...
    def log_event(self, level: str, module: str, name: str, payload: typing.Optional[typing.Any] = None):
        """
        Log an event to the event logger.
        
        Parameters
        ----------
        level : str
            Log level of the event. Can be one of "info", "warning", "error", "critical", "debug".
        module : str
            Module of the event. Usually the name of the class, function, or module that the event is being logged from.
        name : str
            Name of the event. Used to qualify the event type.
        payload : Optional[Any], default None
            Payload of the event. Contains the event data.
        """
        ...
    ...

