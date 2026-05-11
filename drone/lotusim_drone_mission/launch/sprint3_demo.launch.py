"""
Sprint 3 end-to-end mock chain.

Brings up:
- mock_px4_node            (fake /fmu/out/*, listens on /fmu/in/*)
- mock_entity_manager      (action server /mas_cmd_array)
- mock_ui_cmd_pub          (20 Hz sine on /lotusim/ui/drone_manual_cmd)
- manual_control_node      (UI cmd -> /fmu/in/manual_control_setpoint
                            + /fmu/in/offboard_control_mode heartbeat
                            + ~/arm_disarm service)

Record evidence with:
    ros2 bag record /lotusim/ui/drone_manual_cmd /fmu/in/manual_control_setpoint
        /fmu/in/offboard_control_mode /fmu/in/vehicle_command /fmu/out/vehicle_status

Trigger arming from another shell:
    ros2 service call /manual_control_node/arm_disarm
        std_srvs/srv/SetBool '{data: true}'
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    ui_mode = LaunchConfiguration('ui_mode')

    return LaunchDescription([
        DeclareLaunchArgument(
            'ui_mode', default_value='sine',
            description='mock_ui_cmd_pub waveform: hold|sine|step'),

        Node(
            package='lotusim_drone_mocks',
            executable='mock_px4_node',
            name='mock_px4_node',
            output='screen',
        ),
        Node(
            package='lotusim_drone_mocks',
            executable='mock_entity_manager',
            name='mock_entity_manager',
            output='screen',
        ),
        Node(
            package='lotusim_drone_mocks',
            executable='mock_ui_cmd_pub',
            name='mock_ui_cmd_pub',
            output='screen',
            parameters=[{'mode': ui_mode}],
        ),
        Node(
            package='lotusim_drone_mission',
            executable='manual_control_node',
            name='manual_control_node',
            output='screen',
        ),
    ])
