from __future__ import annotations

import pydantic
from dodal.devices.aperturescatterguard import (
    ApertureScatterguard,
)
from dodal.devices.attenuator.attenuator import BinaryFilterAttenuator
from dodal.devices.backlight import Backlight
from dodal.devices.common_dcm import DoubleCrystalMonochromatorWithDSpacing
from dodal.devices.eiger import EigerDetector
from dodal.devices.fast_grid_scan import (
    PandAFastGridScan,
    ZebraFastGridScanThreeD,
)
from dodal.devices.flux import Flux
from dodal.devices.robot import BartRobot
from dodal.devices.s4_slit_gaps import S4SlitGaps
from dodal.devices.synchrotron import Synchrotron
from dodal.devices.undulator import Undulator
from dodal.devices.xbpm_feedback import XBPMFeedback
from dodal.devices.zebra.zebra import Zebra
from dodal.devices.zebra.zebra_controlled_shutter import ZebraShutter
from dodal.devices.zocalo import ZocaloResults
from ophyd_async.fastcs.panda import HDFPanda

from mx_bluesky.common.experiment_plans.common_flyscan_xray_centre_plan import (
    FlyScanEssentialDevices,
)
from mx_bluesky.common.parameters.device_composites import (
    GridDetectThenXRayCentreComposite,
)


@pydantic.dataclasses.dataclass(config={"arbitrary_types_allowed": True})
class HyperionFlyScanXRayCentreComposite(FlyScanEssentialDevices):
    """All devices which are directly or indirectly required by this plan"""

    aperture_scatterguard: ApertureScatterguard
    attenuator: BinaryFilterAttenuator
    dcm: DoubleCrystalMonochromatorWithDSpacing
    eiger: EigerDetector
    flux: Flux
    s4_slit_gaps: S4SlitGaps
    undulator: Undulator
    synchrotron: Synchrotron
    zebra: Zebra
    zocalo: ZocaloResults
    panda: HDFPanda
    panda_fast_grid_scan: PandAFastGridScan
    robot: BartRobot
    sample_shutter: ZebraShutter
    backlight: Backlight
    xbpm_feedback: XBPMFeedback
    zebra_fast_grid_scan: ZebraFastGridScanThreeD


@pydantic.dataclasses.dataclass(config={"arbitrary_types_allowed": True})
class HyperionGridDetectThenXRayCentreComposite(GridDetectThenXRayCentreComposite):
    """All devices which are directly or indirectly required by this plan"""

    panda: HDFPanda
    panda_fast_grid_scan: PandAFastGridScan
