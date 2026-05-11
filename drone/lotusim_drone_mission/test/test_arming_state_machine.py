"""
Unit tests for ArmingStateMachine.

These tests are deliberately ROS-free: the state machine class is the
decision boundary and can be exercised without spinning rclpy. The full
ROS-level E2E (publishing /fmu/in/vehicle_command and seeing
/fmu/out/vehicle_status advance) is covered by the Sprint 3 ros2 bag.
"""

from px4_msgs.msg import VehicleStatus

from lotusim_drone_mission.arming_state_machine import (
    ArmingState,
    ArmingStateMachine,
)


def test_initial_state_is_disarmed():
    sm = ArmingStateMachine()
    assert sm.observed == ArmingState.DISARMED


def test_request_arm_from_disarmed_emits_param1_1():
    sm = ArmingStateMachine()
    cmd = sm.request(arm=True)
    assert cmd is not None
    assert cmd.param1 == 1.0
    assert cmd.param2 == 0.0
    assert cmd.force is False


def test_request_disarm_from_disarmed_is_noop():
    sm = ArmingStateMachine()
    assert sm.request(arm=False) is None


def test_request_arm_when_armed_is_noop():
    sm = ArmingStateMachine()
    sm.observe_status(VehicleStatus.ARMING_STATE_ARMED)
    assert sm.observed == ArmingState.ARMED
    assert sm.request(arm=True) is None


def test_request_disarm_when_armed_emits_param1_0():
    sm = ArmingStateMachine()
    sm.observe_status(VehicleStatus.ARMING_STATE_ARMED)
    cmd = sm.request(arm=False)
    assert cmd is not None
    assert cmd.param1 == 0.0


def test_force_arm_resends_even_when_armed():
    sm = ArmingStateMachine()
    sm.observe_status(VehicleStatus.ARMING_STATE_ARMED)
    cmd = sm.request(arm=True, force=True)
    assert cmd is not None
    assert cmd.param1 == 1.0
    assert cmd.param2 == 21196.0
    assert cmd.force is True


def test_observe_unknown_status_value_is_ignored():
    sm = ArmingStateMachine()
    sm.observe_status(VehicleStatus.ARMING_STATE_ARMED)
    assert sm.observed == ArmingState.ARMED
    # PX4 has additional ARMING_STATE_* values (INIT, STANDBY_ERROR, etc.)
    # — we only care about ARMED / DISARMED for this sprint and must not
    # silently drop the last known state.
    sm.observe_status(99)
    assert sm.observed == ArmingState.ARMED


def test_arm_disarm_round_trip():
    sm = ArmingStateMachine()
    # Arm
    assert sm.request(arm=True) is not None
    sm.observe_status(VehicleStatus.ARMING_STATE_ARMED)
    # Subsequent arm is noop
    assert sm.request(arm=True) is None
    # Disarm
    assert sm.request(arm=False) is not None
    sm.observe_status(VehicleStatus.ARMING_STATE_DISARMED)
    # Subsequent disarm is noop
    assert sm.request(arm=False) is None
