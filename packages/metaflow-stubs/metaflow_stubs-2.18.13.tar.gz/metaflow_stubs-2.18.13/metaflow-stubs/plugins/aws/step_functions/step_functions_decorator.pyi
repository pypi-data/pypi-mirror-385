######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13                                                                                #
# Generated on 2025-10-20T17:35:52.612098                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators

from ....metadata_provider.metadata import MetaDatum as MetaDatum
from .dynamo_db_client import DynamoDbClient as DynamoDbClient

class StepFunctionsInternalDecorator(metaflow.decorators.StepDecorator, metaclass=type):
    def task_pre_step(self, step_name, task_datastore, metadata, run_id, task_id, flow, graph, retry_count, max_user_code_retries, ubf_context, inputs):
        ...
    def task_finished(self, step_name, flow, graph, is_task_ok, retry_count, max_user_code_retries):
        ...
    ...

