######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.12.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-20T19:13:33.358930                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

from ...exception import MetaflowException as MetaflowException
from ..kubernetes.kubernetes_client import KubernetesClient as KubernetesClient

ARGO_EVENTS_SENSOR_NAMESPACE: str

class ArgoClientException(metaflow.exception.MetaflowException, metaclass=type):
    ...

class ArgoResourceNotFound(metaflow.exception.MetaflowException, metaclass=type):
    ...

class ArgoNotPermitted(metaflow.exception.MetaflowException, metaclass=type):
    ...

class ArgoClient(object, metaclass=type):
    def __init__(self, namespace = None):
        ...
    def get_workflow(self, name):
        ...
    def get_workflow_template(self, name):
        ...
    def get_workflow_templates(self, page_size = 100):
        ...
    def register_workflow_template(self, name, workflow_template):
        ...
    def delete_cronworkflow(self, name):
        """
        Issues an API call for deleting a cronworkflow
        
        Returns either the successful API response, or None in case the resource was not found.
        """
        ...
    def delete_workflow_template(self, name):
        """
        Issues an API call for deleting a cronworkflow
        
        Returns either the successful API response, or None in case the resource was not found.
        """
        ...
    def terminate_workflow(self, name):
        ...
    def suspend_workflow(self, name):
        ...
    def unsuspend_workflow(self, name):
        ...
    def trigger_workflow_template(self, name, usertype, username, parameters = {}):
        ...
    def schedule_workflow_template(self, name, schedule = None, timezone = None):
        ...
    def register_sensor(self, name, sensor = None, sensor_namespace = 'default'):
        ...
    def delete_sensor(self, name, sensor_namespace):
        """
        Issues an API call for deleting a sensor
        
        Returns either the successful API response, or None in case the resource was not found.
        """
        ...
    ...

def wrap_api_error(error):
    ...

