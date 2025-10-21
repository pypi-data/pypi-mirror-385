######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-21T09:01:27.258276                                                            #
######################################################################################################

from __future__ import annotations

import importlib
import typing
import abc
if typing.TYPE_CHECKING:
    import importlib.metadata
    import abc
    import os


TYPE_CHECKING: bool

def modules_to_distributions() -> typing.Dict[str, typing.List[importlib.metadata.Distribution]]:
    """
    Return a mapping of top-level modules to their distributions.
    
    Returns
    -------
    Dict[str, List[metadata.Distribution]]
        A mapping of top-level modules to their distributions.
    """
    ...

class PackagedDistribution(importlib.metadata.Distribution, metaclass=type):
    """
    A Python Package packaged within a MetaflowCodeContent. This allows users to use use importlib
    as they would regularly and the packaged Python Package would be considered as a
    distribution even if it really isn't (since it is just included in the PythonPath).
    """
    def __init__(self, root: str, content: typing.Dict[str, str]):
        ...
    def read_text(self, filename: typing.Union[str, os.PathLike]) -> typing.Optional[str]:
        """
        Attempt to load metadata file given by the name.
        
        :param filename: The name of the file in the distribution info.
        :return: The text if found, otherwise None.
        """
        ...
    def locate_file(self, path: typing.Union[str, os.PathLike]):
        ...
    ...

class PackagedDistributionFinder(importlib.metadata.DistributionFinder, metaclass=abc.ABCMeta):
    def __init__(self, dist_info: typing.Dict[str, typing.Dict[str, str]]):
        ...
    def find_distributions(self, context = ...):
        ...
    ...

