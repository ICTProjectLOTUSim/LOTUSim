"""Mock UI command publisher.

Stands in for LOTUSim-UI-backend during dev: publishes
/lotusim/ui/drone_manual_cmd at 20 Hz with a slow waveform so the
manual control path can be exercised without a UI.

Modes (ROS parameter `mode`):
- 'hold':   constant `(throttle, 0, 0, 0)` from parameter `throttle`
- 'sine':   slow sine sweep on all 4 channels (default)
- 'step':   square-wave alternating between +0.5 and -0.5 every 2 s on roll
"""

import math
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
    QoSProfile,
    QoSReliabilityPolicy,
)

from lotusim_drone_msgs.msg import DroneManualCmd


def ui_pub_qos() -> QoSProfile:
    return QoSProfile(
        reliability=QoSReliabilityPolicy.RELIABLE,
        durability=QoSDurabilityPolicy.VOLATILE,
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=10,
    )


class MockUiCmdPub(Node):
    def __init__(self) -> None:
        super().__init__('mock_ui_cmd_pub')

        self.declare_parameter('mode', 'sine')
        self.declare_parameter('rate_hz', 20.0)
        self.declare_parameter('throttle', 0.0)

        self._mode = str(self.get_parameter('mode').value)
        self._rate = float(self.get_parameter('rate_hz').value)
        self._throttle = float(self.get_parameter('throttle').value)

        self._pub = self.create_publisher(
            DroneManualCmd, '/lotusim/ui/drone_manual_cmd', ui_pub_qos())
        self._t = 0.0
        self.create_timer(1.0 / self._rate, self._tick)
        self.get_logger().info(
            f'mock_ui_cmd_pub up: mode={self._mode} rate={self._rate:.1f}Hz')

    def _tick(self) -> None:
        dt = 1.0 / self._rate
        self._t += dt
        msg = DroneManualCmd()
        if self._mode == 'hold':
            msg.throttle = max(-1.0, min(1.0, self._throttle))
            msg.roll = 0.0
            msg.pitch = 0.0
            msg.yaw = 0.0
        elif self._mode == 'step':
            sign = 1.0 if int(self._t / 2.0) % 2 == 0 else -1.0
            msg.throttle = 0.0
            msg.roll = 0.5 * sign
            msg.pitch = 0.0
            msg.yaw = 0.0
        else:  # 'sine' (default)
            msg.throttle = 0.5 * math.sin(0.5 * self._t)
            msg.roll = 0.3 * math.sin(0.7 * self._t)
            msg.pitch = 0.3 * math.cos(0.7 * self._t)
            msg.yaw = 0.2 * math.sin(0.25 * self._t)
        self._pub.publish(msg)


def main(args: Optional[list] = None) -> None:
    rclpy.init(args=args)
    node = MockUiCmdPub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
