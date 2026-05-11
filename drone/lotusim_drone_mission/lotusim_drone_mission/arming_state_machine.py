"""
Arming state machine for manual_control_node.

Kept ROS-free so unit tests can drive it without spinning rclpy. The ROS
node observes VehicleStatus.arming_state and asks this machine whether
to emit a VehicleCommand on /fmu/in/vehicle_command.

PX4 reference (VEHICLE_CMD_COMPONENT_ARM_DISARM = 400):
    param1 = 1.0 -> arm
    param1 = 0.0 -> disarm
    param2 = 21196.0 -> force arm/disarm (skip preflight checks)
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class ArmingState(IntEnum):
    """Mirrors px4_msgs/VehicleStatus.ARMING_STATE_* constants."""

    DISARMED = 1
    ARMED = 2


@dataclass(frozen=True)
class ArmCommand:
    param1: float
    param2: float = 0.0  # 21196.0 = magic force value
    force: bool = False


class ArmingStateMachine:
    """
    Track local belief of arming state, decide which command to emit.

    The status feed from /fmu/out/vehicle_status is the source of truth;
    user requests are translated into a VehicleCommand only when the
    desired state differs from the observed one.
    """

    def __init__(self) -> None:
        self._observed = ArmingState.DISARMED

    @property
    def observed(self) -> ArmingState:
        return self._observed

    def observe_status(self, arming_state: int) -> None:
        if arming_state == int(ArmingState.ARMED):
            self._observed = ArmingState.ARMED
        elif arming_state == int(ArmingState.DISARMED):
            self._observed = ArmingState.DISARMED

    def request(self, arm: bool, *, force: bool = False) -> Optional[ArmCommand]:
        """
        Return the VehicleCommand payload to send, or None if no-op.

        No command is emitted when already in the requested state, unless
        force=True (e.g. resyncing after a missed status update).
        """
        target = ArmingState.ARMED if arm else ArmingState.DISARMED
        if self._observed == target and not force:
            return None
        return ArmCommand(
            param1=1.0 if arm else 0.0,
            param2=21196.0 if force else 0.0,
            force=force,
        )
