######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13                                                                                #
# Generated on 2025-10-20T17:35:52.609103                                                            #
######################################################################################################

from __future__ import annotations


from ...exception import MetaflowException as MetaflowException
from ...exception import MetaflowInternalError as MetaflowInternalError

class Azure(object, metaclass=type):
    @classmethod
    def get_root_from_config(cls, echo, create_on_absent = True):
        ...
    def __init__(self):
        ...
    def __enter__(self):
        ...
    def __exit__(self, *args):
        ...
    def get(self, key = None, return_missing = False):
        """
        Key MUST be a fully qualified path with uri scheme.  azure://<container_name>/b/l/o/b/n/a/m/e
        """
        ...
    def put(self, key, obj, overwrite = True):
        """
        Key MUST be a fully qualified path.  <container_name>/b/l/o/b/n/a/m/e
        """
        ...
    def info(self, key = None, return_missing = False):
        ...
    ...

class AzureObject(object, metaclass=type):
    def __init__(self, url, path, exists, size):
        ...
    @property
    def path(self):
        ...
    @property
    def url(self):
        ...
    @property
    def exists(self):
        ...
    @property
    def size(self):
        ...
    ...

