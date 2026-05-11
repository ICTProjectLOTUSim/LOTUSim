"""
Manual control node.

Bridges UI stick commands into the PX4 downstream topics:
- Subscribes /lotusim/ui/drone_manual_cmd (lotusim_drone_msgs/DroneManualCmd, 20 Hz).
- Re-publishes each command as /fmu/in/manual_control_setpoint.
- Publishes /fmu/in/offboard_control_mode heartbeat at 10 Hz.
- Exposes a ~/arm_disarm std_srvs/SetBool service that sends
  VEHICLE_CMD_COMPONENT_ARM_DISARM on /fmu/in/vehicle_command, gated by
  the arming state machine (no-op if already in the requested state).

QoS choice: mock_px4_node subscribes /fmu/in/* with BEST_EFFORT +
TRANSIENT_LOCAL, so publishers must offer at least the same durability.
Real PX4 over uXRCE-DDS uses BEST_EFFORT too; the topic contract entry
"RELIABLE" in ros2_plan.md §2.2 was aspirational and is overridden here
to keep mock <-> node compatibility (documented in sprint3_review.md).
"""

from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
    QoSProfile,
    QoSReliabilityPolicy,
)

from std_srvs.srv import SetBool

from px4_msgs.msg import (
    ManualControlSetpoint,
    OffboardControlMode,
    VehicleCommand,
    VehicleStatus,
)

from lotusim_drone_msgs.msg import DroneManualCmd

from lotusim_drone_mission.arming_state_machine import (
    ArmCommand,
    ArmingStateMachine,
)


VEHICLE_CMD_COMPONENT_ARM_DISARM = 400


def px4_io_qos(depth: int = 1) -> QoSProfile:
    return QoSProfile(
        reliability=QoSReliabilityPolicy.BEST_EFFORT,
        durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=depth,
    )


def ui_sub_qos() -> QoSProfile:
    return QoSProfile(
        reliability=QoSReliabilityPolicy.RELIABLE,
        durability=QoSDurabilityPolicy.VOLATILE,
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=10,
    )


def _clamp_unit(v: float) -> float:
    return max(-1.0, min(1.0, float(v)))


class ManualControlNode(Node):
    def __init__(self) -> None:
        super().__init__('manual_control_node')

        self.declare_parameter('target_system', 1)
        self.declare_parameter('target_component', 1)
        self.declare_parameter('source_system', 255)
        self.declare_parameter('source_component', 1)
        self.declare_parameter('offboard_heartbeat_hz', 10.0)

        self._target_system = int(self.get_parameter('target_system').value)
        self._target_component = int(self.get_parameter('target_component').value)
        self._source_system = int(self.get_parameter('source_system').value)
        self._source_component = int(self.get_parameter('source_component').value)

        self._arming = ArmingStateMachine()

        setpoint_qos = px4_io_qos(depth=1)
        cmd_qos = px4_io_qos(depth=10)
        self.pub_setpoint = self.create_publisher(
            ManualControlSetpoint, '/fmu/in/manual_control_setpoint', setpoint_qos)
        self.pub_offboard = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', setpoint_qos)
        self.pub_command = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', cmd_qos)

        self.create_subscription(
            DroneManualCmd, '/lotusim/ui/drone_manual_cmd',
            self._on_ui_cmd, ui_sub_qos())

        status_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5,
        )
        self.create_subscription(
            VehicleStatus, '/fmu/out/vehicle_status',
            self._on_status, status_qos)

        self._arm_srv = self.create_service(
            SetBool, '~/arm_disarm', self._on_arm_disarm)

        hz = float(self.get_parameter('offboard_heartbeat_hz').value)
        self.create_timer(1.0 / hz, self._tick_offboard)

        self.get_logger().info(
            f'manual_control_node up: heartbeat={hz:.1f}Hz, '
            f'target_system={self._target_system}')

    def _now_us(self) -> int:
        return self.get_clock().now().nanoseconds // 1000

    def _on_ui_cmd(self, msg: DroneManualCmd) -> None:
        setpoint = ManualControlSetpoint()
        ts = self._now_us()
        setpoint.timestamp = ts
        setpoint.timestamp_sample = ts
        setpoint.throttle = _clamp_unit(msg.throttle)
        setpoint.roll = _clamp_unit(msg.roll)
        setpoint.pitch = _clamp_unit(msg.pitch)
        setpoint.yaw = _clamp_unit(msg.yaw)
        setpoint.valid = True
        setpoint.data_source = ManualControlSetpoint.SOURCE_RC
        self.pub_setpoint.publish(setpoint)

    def _tick_offboard(self) -> None:
        msg = OffboardControlMode()
        msg.timestamp = self._now_us()
        msg.position = False
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        # manual_control_setpoint is its own mode; the heartbeat just
        # tells PX4 "an offboard producer is alive."
        self.pub_offboard.publish(msg)

    def _on_status(self, msg: VehicleStatus) -> None:
        self._arming.observe_status(int(msg.arming_state))

    def _on_arm_disarm(
        self, request: SetBool.Request, response: SetBool.Response
    ) -> SetBool.Response:
        cmd = self._arming.request(arm=bool(request.data))
        if cmd is None:
            state = 'ARMED' if self._arming.observed.value == 2 else 'DISARMED'
            response.success = True
            response.message = f'noop: already {state}'
            return response

        self._send_arm_command(cmd)
        response.success = True
        response.message = (
            f'sent VEHICLE_CMD_COMPONENT_ARM_DISARM param1={cmd.param1}')
        return response

    def _send_arm_command(self, cmd: ArmCommand) -> None:
        msg = VehicleCommand()
        msg.timestamp = self._now_us()
        msg.command = VEHICLE_CMD_COMPONENT_ARM_DISARM
        msg.param1 = cmd.param1
        msg.param2 = cmd.param2
        msg.target_system = self._target_system
        msg.target_component = self._target_component
        msg.source_system = self._source_system
        msg.source_component = self._source_component
        msg.from_external = True
        self.pub_command.publish(msg)
        self.get_logger().info(
            f'arm/disarm requested: param1={cmd.param1} '
            f'(observed={self._arming.observed.name})')


def main(args: Optional[list] = None) -> None:
    rclpy.init(args=args)
    node = ManualControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
