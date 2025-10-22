import pydantic
from dodal.devices.aperturescatterguard import (
    ApertureScatterguard,
)
from dodal.devices.attenuator.attenuator import BinaryFilterAttenuator
from dodal.devices.backlight import Backlight
from dodal.devices.common_dcm import DoubleCrystalMonochromator
from dodal.devices.detector.detector_motion import DetectorMotion
from dodal.devices.eiger import EigerDetector
from dodal.devices.fast_grid_scan import (
    ZebraFastGridScanThreeD,
)
from dodal.devices.flux import Flux
from dodal.devices.mx_phase1.beamstop import Beamstop
from dodal.devices.oav.oav_detector import OAV
from dodal.devices.oav.pin_image_recognition import PinTipDetection
from dodal.devices.robot import BartRobot
from dodal.devices.s4_slit_gaps import S4SlitGaps
from dodal.devices.smargon import Smargon
from dodal.devices.synchrotron import Synchrotron
from dodal.devices.undulator import Undulator
from dodal.devices.xbpm_feedback import XBPMFeedback
from dodal.devices.zebra.zebra import Zebra
from dodal.devices.zebra.zebra_controlled_shutter import ZebraShutter
from dodal.devices.zocalo import ZocaloResults


@pydantic.dataclasses.dataclass(config={"arbitrary_types_allowed": True})
class FlyScanEssentialDevices:
    eiger: EigerDetector
    synchrotron: Synchrotron
    zocalo: ZocaloResults
    smargon: Smargon


@pydantic.dataclasses.dataclass(config={"arbitrary_types_allowed": True})
class OavGridDetectionComposite:
    """All devices which are directly or indirectly required by this plan"""

    backlight: Backlight
    oav: OAV
    smargon: Smargon
    pin_tip_detection: PinTipDetection


@pydantic.dataclasses.dataclass(config={"arbitrary_types_allowed": True})
class GridDetectThenXRayCentreComposite(FlyScanEssentialDevices):
    """All devices which are directly or indirectly required by this plan"""

    aperture_scatterguard: ApertureScatterguard
    attenuator: BinaryFilterAttenuator
    backlight: Backlight
    beamstop: Beamstop
    dcm: DoubleCrystalMonochromator
    detector_motion: DetectorMotion
    zebra_fast_grid_scan: ZebraFastGridScanThreeD
    flux: Flux
    oav: OAV
    pin_tip_detection: PinTipDetection
    s4_slit_gaps: S4SlitGaps
    undulator: Undulator
    xbpm_feedback: XBPMFeedback
    zebra: Zebra
    robot: BartRobot
    sample_shutter: ZebraShutter
