# Sprint 3 Evidence

Capture instructions and expected artifact list for the Sprint 3 acceptance.
Run everything from inside the ROS2 Humble dev container with the workspace
sourced:

```bash
source /opt/ros/humble/setup.bash
source /lotusim_ws/install/setup.bash
```

## 1. Build

```bash
cd /lotusim_ws
colcon build --merge-install --packages-select \
    lotusim_drone_msgs lotusim_drone_mocks lotusim_drone_mission
```

Expected: green for all three packages, no flake8/pep257 failures from
the mission package.

## 2. Unit test (7/8)

```bash
cd /lotusim_ws
colcon test --merge-install --packages-select lotusim_drone_mission
colcon test-result --verbose --test-result-base build/lotusim_drone_mission
```

Expected: `test_arming_state_machine.py` reports 8 passed.

## 3. Topic / interface checks (3/8 + 4/8 + 5/8)

```bash
ros2 interface show lotusim_drone_msgs/msg/DroneManualCmd
ros2 run lotusim_drone_mocks mock_px4_node &
ros2 topic hz /fmu/out/vehicle_local_position   # expect ~50 Hz
ros2 run lotusim_drone_mocks mock_entity_manager &
ros2 action list                                 # contains /mas_cmd_array
```

## 4. End-to-end demo and rosbag (6/8 + 7/8 + 8/8)

```bash
ros2 launch lotusim_drone_mission sprint3_demo.launch.py
```

In a second shell, record evidence:

```bash
ros2 bag record -o sprint3_demo \
    /lotusim/ui/drone_manual_cmd \
    /fmu/in/manual_control_setpoint \
    /fmu/in/offboard_control_mode \
    /fmu/in/vehicle_command \
    /fmu/out/vehicle_status
```

In a third shell, exercise arming:

```bash
ros2 service call /manual_control_node/arm_disarm \
    std_srvs/srv/SetBool '{data: true}'
# wait ~1 s, then disarm:
ros2 service call /manual_control_node/arm_disarm \
    std_srvs/srv/SetBool '{data: false}'
```

Watch `mock_px4_node` log lines for `arming_state -> ARMED` /
`arming_state -> DISARMED` and confirm `/fmu/out/vehicle_status` reflects
the transitions.

`ros2 topic echo` defaults to `RELIABLE/VOLATILE` and will silently block
against the PX4-style `BEST_EFFORT/TRANSIENT_LOCAL` publisher. Inspect
status with explicit QoS flags:

```bash
ros2 topic echo --once \
    --qos-reliability best_effort --qos-durability transient_local \
    /fmu/out/vehicle_status
```

## 5. Expected artifacts in this directory

- `sprint3_demo/` — rosbag2 directory (>= 60 s, contains all five topics).
- `topic_hz.txt` — output of `ros2 topic hz` for the four /fmu/out streams.
- `arming_log.txt` — `mock_px4_node` stdout slice covering the
  arm + disarm round trip.
- `colcon_test.txt` — `colcon test-result --verbose` output for
  `lotusim_drone_mission`.

The bag itself is intentionally not committed to git; capture it locally
and attach to the Jira ticket.
