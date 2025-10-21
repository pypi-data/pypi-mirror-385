######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-21T09:01:27.324740                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.mf_extensions.obcheckpoint.plugins.machine_learning_utilities.utils.general


class PathSize(tuple, metaclass=type):
    """
    PathSize(path, calculated_size, early_stopping, not_found)
    """
    @staticmethod
    def __new__(_cls, path, calculated_size, early_stopping, not_found):
        """
        Create new instance of PathSize(path, calculated_size, early_stopping, not_found)
        """
        ...
    def __repr__(self):
        """
        Return a nicely formatted representation string
        """
        ...
    def __getnewargs__(self):
        """
        Return self as a plain tuple.  Used by copy and pickle.
        """
        ...
    ...

def replace_start_and_end_slash(string):
    ...

def get_path_size(start_path, early_stopping_limit = None) -> PathSize:
    ...

def warning_message(message, logger = None, ts = False, prefix = '[no-prefix]'):
    ...

def unit_convert(number, base_unit, convert_unit):
    ...

def is_json_serializable(value):
    """
    Check if value is JSON serializable.
    """
    ...

def safe_serialize(data):
    ...

