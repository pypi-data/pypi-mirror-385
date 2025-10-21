######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.12.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-20T19:13:33.250651                                                            #
######################################################################################################

from __future__ import annotations

import typing


class PerimeterExtractor(object, metaclass=type):
    @classmethod
    def for_ob_cli(cls, config_dir: str, profile: str) -> typing.Union[typing.Tuple[str, str], typing.Tuple[None, None]]:
        """
        This function will be called when we are trying to extract the perimeter
        via the ob cli's execution. We will rely on the following logic:
        1. check environment variables like OB_CURRENT_PERIMETER / OBP_PERIMETER
        2. run init config to extract the perimeter related configurations.
        
        Returns
        -------
            Tuple[str, str] : Tuple containing perimeter name , API server url.
        """
        ...
    @classmethod
    def during_metaflow_execution(cls) -> typing.Union[typing.Tuple[str, str], typing.Tuple[None, None]]:
        ...
    ...

