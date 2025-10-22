from __future__ import annotations

from collections.abc import Callable, Generator
from typing import TYPE_CHECKING

from bluesky.callbacks import CallbackBase
from dodal.devices.zocalo import ZocaloStartInfo, ZocaloTrigger

from mx_bluesky.common.parameters.constants import (
    DocDescriptorNames,
)
from mx_bluesky.common.utils.exceptions import ISPyBDepositionNotMade
from mx_bluesky.common.utils.log import ISPYB_ZOCALO_CALLBACK_LOGGER

if TYPE_CHECKING:
    from event_model.documents import Event, EventDescriptor, RunStart, RunStop


ZocaloInfoGenerator = Generator[list[ZocaloStartInfo], dict, None]


class ZocaloCallback(CallbackBase):
    """Callback class to handle the triggering of Zocalo processing.
    Will start listening for collections when {triggering_plan} has been started.

    For every ispyb deposition that occurs inside this run the callback will send zocalo
    a run_start signal. Once the {triggering_plan} has ended the callback will send a
    run_end signal for all collections.

    Shouldn't be subscribed directly to the RunEngine, instead should be passed to the
    `emit` argument of an ISPyB callback which appends DCIDs to the relevant start doc.

    Args:
        triggering_plan: Name of the bluesky sub-plan inside of which we generate information
            to be submitted to zocalo; this is identified by the 'subplan_name' entry in the
            run start metadata.
        zocalo_environment: Name of the zocalo environment we use to connect to zocalo
        start_info_generator_factory: A factory method which returns a Generator,
            the generator is sent the ZOCALO_HW_READ event document and in return yields
            one or more ZocaloStartInfo which will each be submitted to zocalo as a job.
    """

    def __init__(
        self,
        triggering_plan: str,
        zocalo_environment: str,
        start_info_generator_factory: Callable[[], ZocaloInfoGenerator],
    ):
        super().__init__()
        self._info_generator_factory = start_info_generator_factory
        self.triggering_plan = triggering_plan
        self.zocalo_interactor = ZocaloTrigger(zocalo_environment)
        self._reset_state()

    def _reset_state(self):
        self.run_uid: str | None = None
        self.zocalo_info: list[ZocaloStartInfo] = []
        self._started_zocalo_collections: list[ZocaloStartInfo] = []
        self.descriptors: dict[str, EventDescriptor] = {}
        self._info_generator = self._info_generator_factory()
        # Prime the generator
        next(self._info_generator)

    def start(self, doc: RunStart):
        ISPYB_ZOCALO_CALLBACK_LOGGER.info("Zocalo handler received start document.")
        if self.triggering_plan and doc.get("subplan_name") == self.triggering_plan:
            self.run_uid = doc.get("uid")
        if self.run_uid:
            zocalo_infos = self._info_generator.send(doc)  # type: ignore
            self.zocalo_info.extend(zocalo_infos)

    def descriptor(self, doc: EventDescriptor):
        self.descriptors[doc["uid"]] = doc

    def event(self, doc: Event) -> Event:
        event_descriptor = self.descriptors[doc["descriptor"]]
        if event_descriptor.get("name") == DocDescriptorNames.ZOCALO_HW_READ:
            filename = doc["data"]["eiger_odin_file_writer_id"]
            for start_info in self.zocalo_info:
                start_info.filename = filename
                self.zocalo_interactor.run_start(start_info)
                self._started_zocalo_collections.append(start_info)
            self.zocalo_info = []
        return doc

    def stop(self, doc: RunStop):
        if doc.get("run_start") == self.run_uid:
            ISPYB_ZOCALO_CALLBACK_LOGGER.info(
                f"Zocalo handler received stop document, for run {doc.get('run_start')}."
            )
            if not self._started_zocalo_collections:
                raise ISPyBDepositionNotMade(
                    f"No ISPyB IDs received by the end of {self.triggering_plan=}"
                )
            for info in self._started_zocalo_collections:
                self.zocalo_interactor.run_end(info.ispyb_dcid)
            self._reset_state()
