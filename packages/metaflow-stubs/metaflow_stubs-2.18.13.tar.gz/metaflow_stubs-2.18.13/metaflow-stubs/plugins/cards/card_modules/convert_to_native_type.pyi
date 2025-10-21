######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13                                                                                #
# Generated on 2025-10-20T17:35:52.611372                                                            #
######################################################################################################

from __future__ import annotations



class TypeResolvedObject(tuple, metaclass=type):
    """
    TypeResolvedObject(data, is_image, is_table)
    """
    @staticmethod
    def __new__(_cls, data, is_image, is_table):
        """
        Create new instance of TypeResolvedObject(data, is_image, is_table)
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

TIME_FORMAT: str

MAX_ARTIFACT_SIZE: int

class TaskToDict(object, metaclass=type):
    def __init__(self, only_repr = False, runtime = False, max_artifact_size = None):
        ...
    def __call__(self, task, graph = None):
        ...
    def object_type(self, object):
        ...
    def parse_image(self, data_object):
        ...
    def infer_object(self, artifact_object):
        ...
    ...

