from __future__ import annotations

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.devices.aperturescatterguard import ApertureScatterguard, ApertureValue
from dodal.devices.motors import XYZStage
from dodal.devices.robot import BartRobot
from dodal.devices.smargon import CombinedMove, Smargon, StubPosition
from dodal.plan_stubs.motor_utils import MoveTooLargeError, home_and_reset_wrapper

from mx_bluesky.common.parameters.constants import (
    DocDescriptorNames,
    HardwareConstants,
    PlanNameConstants,
)
from mx_bluesky.common.utils.log import LOGGER

SLEEP_PER_CHECK = 0.1


def wait_for_smargon_not_disabled(smargon: Smargon, timeout=60):
    """Waits for the smargon disabled flag to go low. The robot hardware is responsible
    for setting this to low when it is safe to move. It does this through a physical
    connection between the robot and the smargon.
    """
    LOGGER.info("Waiting for smargon enabled")
    times_to_check = int(timeout / SLEEP_PER_CHECK)
    for _ in range(times_to_check):
        smargon_disabled = yield from bps.rd(smargon.disabled)
        if not smargon_disabled:
            LOGGER.info("Smargon now enabled")
            return
        yield from bps.sleep(SLEEP_PER_CHECK)
    raise TimeoutError(
        "Timed out waiting for smargon to become enabled after robot load"
    )


def _raise_exception_if_moved_out_of_cryojet(exception):
    yield from bps.null()
    if isinstance(exception, MoveTooLargeError):
        raise Exception(
            f"Moving {exception.axis} back to {exception.position} after \
                        robot load would move it out of the cryojet. The max safe \
                        distance is {exception.maximum_move}"
        )


def do_plan_while_lower_gonio_at_home(plan: MsgGenerator, lower_gonio: XYZStage):
    """Moves the lower gonio to home then performs the provided plan and moves it back.

    The lower gonio must be in the correct position for the robot load and we
    want to put it back afterwards. Note we don't need to wait for the move as the robot
    is interlocked to the lower gonio and the move is quicker than the robot takes to
    get to the load position.

    Args:
        plan (MsgGenerator): The plan to run while the lower gonio is at home.
        lower_gonio (XYZStage): The lower gonio to home.
    """
    yield from bpp.contingency_wrapper(
        home_and_reset_wrapper(
            plan,
            lower_gonio,
            BartRobot.LOAD_TOLERANCE_MM,
            HardwareConstants.CRYOJET_MARGIN_MM,
            "lower_gonio",
            wait_for_all=False,
        ),
        except_plan=_raise_exception_if_moved_out_of_cryojet,
    )
    return "reset-lower_gonio"


def prepare_for_robot_load(
    aperture_scatterguard: ApertureScatterguard, smargon: Smargon
):
    yield from bps.abs_set(
        aperture_scatterguard.selected_aperture,
        ApertureValue.OUT_OF_BEAM,
        group="prepare_robot_load",
    )

    yield from bps.mv(smargon.stub_offsets, StubPosition.RESET_TO_ROBOT_LOAD)

    yield from bps.mv(smargon, CombinedMove(x=0, y=0, z=0, chi=0, phi=0, omega=0))

    yield from bps.wait("prepare_robot_load")


def robot_unload(
    robot: BartRobot,
    smargon: Smargon,
    aperture_scatterguard: ApertureScatterguard,
    lower_gonio: XYZStage,
    visit: str,
):
    """Unloads the currently mounted pin into the location that it was loaded from. The
    loaded location is stored on the robot and so need not be provided.
    """
    yield from prepare_for_robot_load(aperture_scatterguard, smargon)
    sample_id = yield from bps.rd(robot.sample_id)

    @bpp.run_decorator(
        md={
            "subplan_name": PlanNameConstants.ROBOT_UNLOAD,
            "metadata": {"visit": visit, "sample_id": sample_id},
            "activate_callbacks": [
                "RobotLoadISPyBCallback",
            ],
        },
    )
    def do_robot_unload_and_send_to_ispyb():
        yield from bps.create(name=DocDescriptorNames.ROBOT_UPDATE)
        yield from bps.read(robot)
        yield from bps.save()

        def _unload():
            yield from bps.trigger(robot.unload, wait=True)
            yield from wait_for_smargon_not_disabled(smargon)

        gonio_finished = yield from do_plan_while_lower_gonio_at_home(
            _unload(), lower_gonio
        )
        yield from bps.wait(gonio_finished)

    yield from do_robot_unload_and_send_to_ispyb()
