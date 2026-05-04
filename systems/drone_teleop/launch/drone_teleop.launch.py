"""
Launch file for manual drone teleoperation in LOTUSim.

Starts three things in order:
  1. ros_gz_bridge  — maps ROS 2 topics ↔ Gazebo transport topics
                      (cmd_vel, enable, imu, navsat, magnetometer, air_pressure)
  2. enable publisher — arms the velocity controller 3 seconds after the bridge
                        is up (gives Gazebo time to initialise)
  3. teleop_twist_keyboard — keyboard control remapped to /drone/cmd_vel

Prerequisites (start BEFORE this launch file):
    lotusim run --gui drone_test.world   (or drone_px4.world for PX4 mode)

Usage:
    ros2 launch drone_teleop drone_teleop.launch.py

    # With GUI (opens Gazebo GUI — only needed if lotusim was run in server mode)
    ros2 launch drone_teleop drone_teleop.launch.py gui:=true

    # With joystick instead of keyboard
    ros2 launch drone_teleop drone_teleop.launch.py input:=joystick
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    LogInfo,
    TimerAction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():

    pkg_share = get_package_share_directory("drone_teleop")

    # ---------------------------------------------------------------------------
    # Launch arguments
    # ---------------------------------------------------------------------------
    input_arg = DeclareLaunchArgument(
        "input",
        default_value="keyboard",
        description="Control input type: 'keyboard' or 'joystick'",
    )

    gui_arg = DeclareLaunchArgument(
        "gui",
        default_value="false",
        description="Launch Gazebo GUI separately (set true if lotusim was run without --gui)",
    )

    # ---------------------------------------------------------------------------
    # ros_gz_bridge — ROS 2 <-> Gazebo topic bridge
    # ---------------------------------------------------------------------------
    bridge_config = os.path.join(pkg_share, "config", "bridges", "drone_teleop_bridges.yaml")

    bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="drone_gz_bridge",
        output="screen",
        parameters=[{"config_file": bridge_config}],
    )

    # ---------------------------------------------------------------------------
    # Arm the velocity controller 3 s after bridge starts
    # The bridge must be connected to Gazebo before the enable message is sent.
    # ---------------------------------------------------------------------------
    arm_controller = TimerAction(
        period=3.0,
        actions=[
            LogInfo(msg="[drone_teleop] Arming velocity controller..."),
            ExecuteProcess(
                cmd=[
                    "ros2", "topic", "pub", "--once",
                    "/drone/enable",
                    "std_msgs/msg/Bool",
                    "{data: true}",
                ],
                output="screen",
            ),
        ],
    )

    # ---------------------------------------------------------------------------
    # Keyboard teleop (default input)
    # ---------------------------------------------------------------------------
    is_joystick = IfCondition(
        PythonExpression(["'", LaunchConfiguration("input"), "' == 'joystick'"])
    )
    is_keyboard = UnlessCondition(
        PythonExpression(["'", LaunchConfiguration("input"), "' == 'joystick'"])
    )

    keyboard_teleop = Node(
        package="teleop_twist_keyboard",
        executable="teleop_twist_keyboard",
        name="drone_keyboard_teleop",
        output="screen",
        remappings=[("cmd_vel", "/drone/cmd_vel")],
        condition=is_keyboard,
    )

    # ---------------------------------------------------------------------------
    # Joystick teleop (optional)
    # ---------------------------------------------------------------------------
    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="drone_joy_node",
        output="screen",
        condition=is_joystick,
    )

    joystick_config = os.path.join(pkg_share, "config", "joystick", "teleop_joy_drone.yaml")

    joystick_teleop = Node(
        package="teleop_twist_joy",
        executable="teleop_twist_joy_node",
        name="drone_joystick_teleop",
        output="screen",
        parameters=[joystick_config],
        remappings=[("cmd_vel", "/drone/cmd_vel")],
        condition=is_joystick,
    )

    # ---------------------------------------------------------------------------
    # Launch description
    # ---------------------------------------------------------------------------
    return LaunchDescription(
        [
            input_arg,
            gui_arg,

            LogInfo(msg="[drone_teleop] Starting Gazebo <-> ROS 2 bridge..."),
            bridge_node,

            LogInfo(msg="[drone_teleop] Bridge started. Arming controller in 3 s..."),
            arm_controller,

            # keyboard or joystick — only one runs based on 'input' arg
            keyboard_teleop,
            joy_node,
            joystick_teleop,
        ]
    )
