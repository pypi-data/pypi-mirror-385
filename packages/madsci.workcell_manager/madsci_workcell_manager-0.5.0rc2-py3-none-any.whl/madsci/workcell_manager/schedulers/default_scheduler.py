"""Default MADSci Workcell scheduler"""

import traceback
from datetime import datetime, timedelta

from madsci.common.types.action_types import ActionStatus
from madsci.common.types.step_types import Step
from madsci.common.types.workflow_types import (
    SchedulerMetadata,
    Workflow,
)
from madsci.workcell_manager.condition_checks import evaluate_condition_checks
from madsci.workcell_manager.schedulers.scheduler import AbstractScheduler
from madsci.workcell_manager.workflow_utils import insert_parameters


class Scheduler(AbstractScheduler):
    """
    This is the default scheduler for the MADSci Workcell Manager. It is a simple FIFO scheduler that checks if the workflow is ready to run.

    - It checks a variety of conditions to determine if a workflow is ready to run. If the workflow is not ready to run, it will add a reason to the scheduler metadata for the workflow.
    - It sets the priority of the workflow based on the order in which the workflows were submitted.
    """

    def run_iteration(self, workflows: list[Workflow]) -> dict[str, SchedulerMetadata]:
        """Run an iteration of the scheduling algorithm and return a mapping of workflow IDs to SchedulerMetadata"""
        priority = 0
        workflows = sorted(
            workflows,
            key=lambda item: item.submitted_time,
        )
        workflow_definition_metadata_map = {}

        for wf in workflows:
            try:
                metadata = wf.scheduler_metadata
                metadata.ready_to_run = True
                metadata.reasons = []

                if wf.status.current_step_index < len(wf.steps):
                    step = wf.steps[wf.status.current_step_index]
                    updated_step = insert_parameters(step, wf.parameter_values)
                    self.check_workflow_status(wf, metadata)
                    self.location_checks(updated_step, metadata)
                    self.resource_checks(updated_step, metadata)
                    self.node_checks(updated_step, wf, metadata)
                    self.step_checks(updated_step, metadata)
                    metadata = evaluate_condition_checks(updated_step, self, metadata)
                    metadata.priority = priority
                    priority -= 1

            except Exception as e:
                self.logger.error(
                    f"Error in scheduler while evaluating workflow {wf.workflow_id}: {traceback.format_exc()}"
                )
                metadata.ready_to_run = False
                metadata.reasons.append(f"Exception in scheduler: {e}")
            finally:
                workflow_definition_metadata_map[wf.workflow_id] = metadata

        return workflow_definition_metadata_map

    def check_workflow_status(self, wf: Workflow, metadata: SchedulerMetadata) -> None:
        """Check if the workflow is ready to run (i.e. not paused, not completed, etc.)"""
        if wf.status.paused:
            metadata.ready_to_run = False
            metadata.reasons.append("Workflow is paused")
            return
        if wf.status.running:
            metadata.ready_to_run = False
            metadata.reasons.append("Workflow is already running")
            return
        if not wf.status.active:
            metadata.ready_to_run = False
            metadata.reasons.append(
                f"Workflow must be active (i.e., not completed, failed, cancelled, or paused), not {wf.status.description}"
            )

    def location_checks(self, step: Step, metadata: SchedulerMetadata) -> None:
        """Check if the location(s) for the step are ready"""
        for location in step.locations.values():
            if location is None:
                continue
            # Get the current location state from LocationManager
            current_location = location
            try:
                if self.location_client is not None:
                    current_location = self.location_client.get_location(
                        location.location_id
                    )
            except Exception:
                # If LocationManager is not available or location not found, use step's location
                current_location = location

            if (
                current_location.resource_id is not None
                and self.resource_client is not None
            ):
                self.resource_client.get_resource(current_location.resource_id)
                # TODO: what do we do with the location_resource?
            if current_location.reservation is not None:
                metadata.ready_to_run = False
                metadata.reasons.append(
                    f"Location {current_location.location_id} is reserved by {current_location.reservation.owned_by.model_dump(mode='json', exclude_none=True)}"
                )

    def resource_checks(self, step: Step, metadata: SchedulerMetadata) -> None:
        """Check if the resources for the step are ready TODO: actually check"""

    def step_checks(self, step: Step, metadata: SchedulerMetadata) -> None:
        """Check if the step was not ready recently mark the workflow as not active"""
        if (
            step.result is not None
            and step.result.status == ActionStatus.NOT_READY
            and datetime.now().astimezone() - step.result.history_created_at
            < timedelta(seconds=30)
        ):
            metadata.ready_to_run = False
            metadata.reasons.append(f"Waiting for Node {step.node} to be ready")

    def node_checks(
        self, step: Step, wf: Workflow, metadata: SchedulerMetadata
    ) -> None:
        """Check if the node used in the step currently has a "ready" status"""
        if step.node is not None:
            node = self.state_handler.get_node(step.node)
            if node is None:
                metadata.ready_to_run = False
                metadata.reasons.append(f"Node {step.node} not found")
            if not node.status.ready:
                metadata.ready_to_run = False
                metadata.reasons.append(
                    f"Node {step.node} not ready: {node.status.description}"
                )
            # Check if node is locked (another workflow is currently sending it an action request)
            node_lock = self.state_handler.node_lock(step.node)
            if node_lock.locked():
                metadata.ready_to_run = False
                metadata.reasons.append(f"Node {step.node} is locked by another action")

            if node.reservation is not None and node.reservation.check(
                wf.ownership_info
            ):
                metadata.ready_to_run = False
                metadata.reasons.append(
                    f"Node {step.node} is reserved by {node.reservation.owned_by.model_dump(mode='json', exclude_none=True)}"
                )
