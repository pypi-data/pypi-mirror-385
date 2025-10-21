######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13                                                                                #
# Generated on 2025-10-20T17:35:52.620669                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators

from ..exception import AirflowException as AirflowException
from ..airflow_utils import AirflowTask as AirflowTask
from ..airflow_utils import id_creator as id_creator

TASK_ID_HASH_LEN: int

class AirflowSensorDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    """
    Base class for all Airflow sensor decorators.
    """
    def __init__(self, *args, **kwargs):
        ...
    def serialize_operator_args(self):
        """
        Subclasses will parse the decorator arguments to
        Airflow task serializable arguments.
        """
        ...
    def create_task(self):
        ...
    def validate(self, flow):
        """
        Validate if the arguments for the sensor are correct.
        """
        ...
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    ...

