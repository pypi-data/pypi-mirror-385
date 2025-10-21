######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-21T09:01:27.259735                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
import abc
if typing.TYPE_CHECKING:
    import metaflow.packaging_sys.backend
    import io
    import typing
    import abc
    import tarfile

from .backend import PackagingBackend as PackagingBackend

class TarPackagingBackend(metaflow.packaging_sys.backend.PackagingBackend, metaclass=abc.ABCMeta):
    @classmethod
    def get_extract_commands(cls, archive_name: str, dest_dir: str) -> typing.List[str]:
        ...
    def __init__(self):
        ...
    def create(self):
        ...
    def add_file(self, filename: str, arcname: typing.Optional[str] = None):
        ...
    def add_data(self, data: io.BytesIO, arcname: str):
        ...
    def close(self):
        ...
    def get_blob(self) -> typing.Union[bytes, bytearray, None]:
        ...
    @classmethod
    def cls_open(cls, content: typing.IO[bytes]) -> tarfile.TarFile:
        ...
    @classmethod
    def cls_member_name(cls, member: typing.Union[tarfile.TarInfo, str]) -> str:
        """
        Returns the name of the member as a string.
        """
        ...
    @classmethod
    def cls_has_member(cls, archive: tarfile.TarFile, name: str) -> bool:
        ...
    @classmethod
    def cls_get_member(cls, archive: tarfile.TarFile, name: str) -> typing.Optional[bytes]:
        ...
    @classmethod
    def cls_extract_members(cls, archive: tarfile.TarFile, members: typing.Optional[typing.List[typing.Any]] = None, dest_dir: str = '.'):
        ...
    @classmethod
    def cls_list_members(cls, archive: tarfile.TarFile) -> typing.Optional[typing.List[tarfile.TarInfo]]:
        ...
    @classmethod
    def cls_list_names(cls, archive: tarfile.TarFile) -> typing.Optional[typing.List[str]]:
        ...
    ...

