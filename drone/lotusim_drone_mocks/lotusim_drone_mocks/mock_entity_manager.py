"""Mock LOTUSim entity_manager.

Stands in for the real entity_manager_plugin during ROS2-only development:
- Exposes /mas_cmd_array as a rclpy ActionServer<lotusim_msgs/MASCmdArray>.
- On goal accept, prints every MASCmd in the request and immediately succeeds.
- Returns synthetic name/entity arrays so downstream nodes can wire up.
"""

import json

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from lotusim_msgs.action import MASCmdArray


_CMD_TYPE_LABEL = {0: 'CREATE', 1: 'DELETE', 2: 'MOVE'}


def _summarize_cmd(cmd) -> dict:
    pose = cmd.vessel_position
    return {
        'cmd_type': _CMD_TYPE_LABEL.get(int(cmd.cmd_type), str(cmd.cmd_type)),
        'model_name': cmd.model_name,
        'vessel_name': cmd.vessel_name,
        'entity': int(cmd.entity),
        'sdf_file': cmd.sdf_file,
        'sdf_string_len': len(cmd.sdf_string or ''),
        'pose': {
            'x': pose.position.x,
            'y': pose.position.y,
            'z': pose.position.z,
            'qx': pose.orientation.x,
            'qy': pose.orientation.y,
            'qz': pose.orientation.z,
            'qw': pose.orientation.w,
        },
        'heading': float(cmd.heading),
    }


class MockEntityManager(Node):
    def __init__(self) -> None:
        super().__init__('mock_entity_manager')
        self._next_entity_id = 1
        self._server = ActionServer(
            self, MASCmdArray, 'mas_cmd_array', self._execute)
        self.get_logger().info(
            'mock_entity_manager up: action server /mas_cmd_array ready')

    def _execute(self, goal_handle):
        request = goal_handle.request
        cmds = list(request.cmd)
        summary = [_summarize_cmd(c) for c in cmds]
        self.get_logger().info(
            f'/mas_cmd_array goal received ({len(cmds)} cmd):\n'
            f'{json.dumps(summary, indent=2)}')

        result = MASCmdArray.Result()
        result.result = [True] * len(cmds)
        result.name = []
        result.entity = []
        for cmd in cmds:
            name = cmd.vessel_name or f'mock_vessel_{self._next_entity_id}'
            entity = int(cmd.entity) if int(cmd.entity) > 0 else self._next_entity_id
            self._next_entity_id += 1
            result.name.append(name)
            result.entity.append(entity)

        goal_handle.succeed()
        return result


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MockEntityManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
