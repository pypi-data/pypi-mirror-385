######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.13                                                                                #
# Generated on 2025-10-20T17:35:52.632943                                                            #
######################################################################################################

from __future__ import annotations



AWS_SANDBOX_ENABLED: bool

AWS_SANDBOX_REGION: None

SFN_EXECUTION_LOG_GROUP_ARN: None

class StepFunctionsClient(object, metaclass=type):
    def __init__(self):
        ...
    def search(self, name):
        ...
    def push(self, name, definition, role_arn, log_execution_history):
        ...
    def get(self, name):
        ...
    def trigger(self, state_machine_arn, input):
        ...
    def list_executions(self, state_machine_arn, states):
        ...
    def terminate_execution(self, execution_arn):
        ...
    def get_state_machine_arn(self, name):
        ...
    def delete(self, name):
        ...
    ...

