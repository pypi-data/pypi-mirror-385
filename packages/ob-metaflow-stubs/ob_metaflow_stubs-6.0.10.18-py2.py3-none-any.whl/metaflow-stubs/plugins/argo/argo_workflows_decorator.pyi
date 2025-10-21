######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.12.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-20T19:13:33.276525                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.graph
    import metaflow.decorators
    import metaflow.flowspec

from ...metaflow_current import current as current
from ...events import Trigger as Trigger
from ...metadata_provider.metadata import MetaDatum as MetaDatum
from ...flowspec import FlowSpec as FlowSpec
from .argo_events import ArgoEvent as ArgoEvent

class ArgoWorkflowsInternalDecorator(metaflow.decorators.StepDecorator, metaclass=type):
    def task_pre_step(self, step_name, task_datastore, metadata, run_id, task_id, flow, graph, retry_count, max_user_code_retries, ubf_context, inputs):
        ...
    def task_finished(self, step_name, flow: metaflow.flowspec.FlowSpec, graph: metaflow.graph.FlowGraph, is_task_ok, retry_count, max_user_code_retries):
        ...
    ...

