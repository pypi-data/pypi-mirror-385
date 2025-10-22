from __future__ import annotations

from typing import TYPE_CHECKING

from mx_bluesky.common.external_interaction.callbacks.common.ispyb_mapping import (
    get_proposal_and_session_from_visit_string,
)
from mx_bluesky.common.external_interaction.callbacks.common.plan_reactive_callback import (
    PlanReactiveCallback,
)
from mx_bluesky.common.external_interaction.ispyb.exp_eye_store import (
    BLSampleStatus,
    ExpeyeInteraction,
    RobotActionID,
    create_update_data_from_event_doc,
)
from mx_bluesky.common.utils.log import ISPYB_ZOCALO_CALLBACK_LOGGER
from mx_bluesky.hyperion.parameters.constants import CONST

if TYPE_CHECKING:
    from event_model.documents import Event, EventDescriptor, RunStart, RunStop


robot_update_mapping = {
    "robot-barcode": "sampleBarcode",
    "robot-current_pin": "containerLocation",
    "robot-current_puck": "dewarLocation",
    # I03 uses webcam/oav snapshots in place of before/after snapshots
    "webcam-last_saved_path": "xtalSnapshotBefore",
    "oav-snapshot-last_saved_path": "xtalSnapshotAfter",
}


class RobotLoadISPyBCallback(PlanReactiveCallback):
    def __init__(self) -> None:
        ISPYB_ZOCALO_CALLBACK_LOGGER.debug("Initialising ISPyB Robot Load Callback")
        super().__init__(log=ISPYB_ZOCALO_CALLBACK_LOGGER)
        self._sample_id: int | None = None

        self.run_uid: str | None = None
        self.descriptors: dict[str, EventDescriptor] = {}
        self.action_id: RobotActionID | None = None
        self.expeye = ExpeyeInteraction()

    def activity_gated_start(self, doc: RunStart):
        ISPYB_ZOCALO_CALLBACK_LOGGER.debug(
            "ISPyB robot load callback received start document."
        )
        subplan = doc.get("subplan_name")
        if subplan == CONST.PLAN.ROBOT_LOAD or subplan == CONST.PLAN.ROBOT_UNLOAD:
            ISPYB_ZOCALO_CALLBACK_LOGGER.debug(
                f"ISPyB robot load callback received: {doc}"
            )
            self.run_uid = doc.get("uid")
            metadata = doc.get("metadata")
            assert isinstance(metadata, dict)
            self._sample_id = metadata["sample_id"]
            assert isinstance(self._sample_id, int)
            proposal, session = get_proposal_and_session_from_visit_string(
                metadata["visit"]
            )
            self.action_id = self.expeye.start_robot_action(
                "LOAD" if subplan == CONST.PLAN.ROBOT_LOAD else "UNLOAD",
                proposal,
                session,
                self._sample_id,
            )
        return super().activity_gated_start(doc)

    def activity_gated_descriptor(self, doc: EventDescriptor) -> EventDescriptor | None:
        self.descriptors[doc["uid"]] = doc
        return super().activity_gated_descriptor(doc)

    def activity_gated_event(self, doc: Event) -> Event | None:
        event_descriptor = self.descriptors.get(doc["descriptor"])
        if (
            event_descriptor
            and event_descriptor.get("name") == CONST.DESCRIPTORS.ROBOT_UPDATE
        ):
            assert self.action_id is not None, (
                "ISPyB Robot load callback event called unexpectedly"
            )
            # I03 uses webcam/oav snapshots in place of before/after snapshots
            update_data = create_update_data_from_event_doc(robot_update_mapping, doc)
            self.expeye.update_robot_action(self.action_id, update_data)

        return super().activity_gated_event(doc)

    def activity_gated_stop(self, doc: RunStop) -> RunStop | None:
        ISPYB_ZOCALO_CALLBACK_LOGGER.debug(
            "ISPyB robot load callback received stop document."
        )
        if doc.get("run_start") == self.run_uid:
            assert self.action_id is not None, (
                "ISPyB Robot load callback stop called unexpectedly"
            )
            exit_status = doc.get("exit_status")
            assert exit_status, "Exit status not available in stop document!"
            assert self._sample_id is not None, "Stop called before start"
            reason = doc.get("reason") or "OK"

            self.expeye.end_robot_action(self.action_id, exit_status, reason)
            self.expeye.update_sample_status(
                self._sample_id,
                BLSampleStatus.LOADED
                if exit_status == "success"
                else BLSampleStatus.ERROR_BEAMLINE,
            )
            self.action_id = None
        return super().activity_gated_stop(doc)
