"""Mock Pixhawk node.

Publishes fake PX4 telemetry on /fmu/out/* at the same rates as the real
flight stack and prints anything received on /fmu/in/*.

Frequencies (per ros2_plan.md §2.1):
- vehicle_local_position: 50 Hz (NED)
- vehicle_attitude:       50 Hz
- vehicle_status:          2 Hz
- battery_status:          1 Hz
"""

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
    QoSProfile,
    QoSReliabilityPolicy,
)

from px4_msgs.msg import (
    BatteryStatus,
    ManualControlSetpoint,
    OffboardControlMode,
    VehicleAttitude,
    VehicleCommand,
    VehicleLocalPosition,
    VehicleStatus,
)


def px4_pub_qos() -> QoSProfile:
    return QoSProfile(
        reliability=QoSReliabilityPolicy.BEST_EFFORT,
        durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=5,
    )


def px4_sub_qos() -> QoSProfile:
    return QoSProfile(
        reliability=QoSReliabilityPolicy.BEST_EFFORT,
        durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=5,
    )


VEHICLE_CMD_COMPONENT_ARM_DISARM = 400


class MockPx4Node(Node):
    def __init__(self) -> None:
        super().__init__('mock_px4_node')

        self._arming_state = VehicleStatus.ARMING_STATE_DISARMED

        pub_qos = px4_pub_qos()
        self.pub_local_pos = self.create_publisher(
            VehicleLocalPosition, '/fmu/out/vehicle_local_position', pub_qos)
        self.pub_attitude = self.create_publisher(
            VehicleAttitude, '/fmu/out/vehicle_attitude', pub_qos)
        self.pub_status = self.create_publisher(
            VehicleStatus, '/fmu/out/vehicle_status', pub_qos)
        self.pub_battery = self.create_publisher(
            BatteryStatus, '/fmu/out/battery_status', pub_qos)

        sub_qos = px4_sub_qos()
        self.create_subscription(
            OffboardControlMode, '/fmu/in/offboard_control_mode',
            self._on_offboard_mode, sub_qos)
        self.create_subscription(
            ManualControlSetpoint, '/fmu/in/manual_control_setpoint',
            self._on_manual_setpoint, sub_qos)
        self.create_subscription(
            VehicleCommand, '/fmu/in/vehicle_command',
            self._on_vehicle_command, sub_qos)

        self._t = 0.0
        self.create_timer(1.0 / 50.0, self._tick_local_pos)
        self.create_timer(1.0 / 50.0, self._tick_attitude)
        self.create_timer(1.0 / 2.0, self._tick_status)
        self.create_timer(1.0, self._tick_battery)

        self.get_logger().info(
            'mock_px4_node up: publishing /fmu/out/* and listening on /fmu/in/*')

    def _now_us(self) -> int:
        return self.get_clock().now().nanoseconds // 1000

    def _tick_local_pos(self) -> None:
        self._t += 1.0 / 50.0
        msg = VehicleLocalPosition()
        ts = self._now_us()
        msg.timestamp = ts
        msg.timestamp_sample = ts
        msg.xy_valid = True
        msg.z_valid = True
        msg.v_xy_valid = True
        msg.v_z_valid = True
        msg.x = float(math.cos(self._t))
        msg.y = float(math.sin(self._t))
        msg.z = -2.0
        msg.vx = float(-math.sin(self._t))
        msg.vy = float(math.cos(self._t))
        msg.vz = 0.0
        msg.heading = float(math.atan2(msg.vy, msg.vx))
        msg.xy_global = False
        msg.z_global = False
        self.pub_local_pos.publish(msg)

    def _tick_attitude(self) -> None:
        msg = VehicleAttitude()
        ts = self._now_us()
        msg.timestamp = ts
        msg.timestamp_sample = ts
        msg.q = [1.0, 0.0, 0.0, 0.0]
        self.pub_attitude.publish(msg)

    def _tick_status(self) -> None:
        msg = VehicleStatus()
        msg.timestamp = self._now_us()
        msg.arming_state = self._arming_state
        msg.nav_state = VehicleStatus.NAVIGATION_STATE_MANUAL
        msg.vehicle_type = VehicleStatus.VEHICLE_TYPE_ROTARY_WING
        msg.pre_flight_checks_pass = True
        self.pub_status.publish(msg)

    def _tick_battery(self) -> None:
        msg = BatteryStatus()
        msg.timestamp = self._now_us()
        msg.connected = True
        msg.voltage_v = 16.4
        msg.voltage_filtered_v = 16.4
        msg.current_a = 5.0
        msg.current_filtered_a = 5.0
        msg.remaining = 0.85
        msg.cell_count = 4
        self.pub_battery.publish(msg)

    def _on_offboard_mode(self, msg: OffboardControlMode) -> None:
        self.get_logger().info(
            f'[offboard_control_mode] position={msg.position} '
            f'velocity={msg.velocity} attitude={msg.attitude} '
            f'body_rate={msg.body_rate}')

    def _on_manual_setpoint(self, msg: ManualControlSetpoint) -> None:
        self.get_logger().info(
            f'[manual_control_setpoint] throttle={msg.throttle:.3f} '
            f'roll={msg.roll:.3f} pitch={msg.pitch:.3f} yaw={msg.yaw:.3f}')

    def _on_vehicle_command(self, msg: VehicleCommand) -> None:
        self.get_logger().info(
            f'[vehicle_command] cmd={msg.command} '
            f'param1={msg.param1:.3f} param2={msg.param2:.3f} '
            f'target_system={msg.target_system}')
        if int(msg.command) == VEHICLE_CMD_COMPONENT_ARM_DISARM:
            if msg.param1 >= 0.5:
                self._arming_state = VehicleStatus.ARMING_STATE_ARMED
                self.get_logger().info('[mock_px4] arming_state -> ARMED')
            else:
                self._arming_state = VehicleStatus.ARMING_STATE_DISARMED
                self.get_logger().info('[mock_px4] arming_state -> DISARMED')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MockPx4Node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
