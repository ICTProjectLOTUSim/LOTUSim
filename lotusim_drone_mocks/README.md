# lotusim_drone_mocks

Test doubles for the parts of the system we do **not** own this semester:
Pixhawk, LOTUSim `entity_manager_plugin`, the UI WebSocket bridge, and the
environment sensor plugins. They let `lotusim_drone_bridge` and
`lotusim_drone_mission` run end-to-end without any external system.

Each mock is wired so that the real component can be dropped in later without
touching downstream nodes — see the "replaced by" column in
[`../docs/topics.md`](../docs/topics.md).

## Nodes

| Node | Replaces | Publishes | Subscribes / serves |
|---|---|---|---|
| `mock_px4_node` | Pixhawk + Micro-XRCE-DDS Agent | `/fmu/out/vehicle_local_position` (50 Hz), `/fmu/out/vehicle_attitude` (50 Hz), `/fmu/out/vehicle_status` (2 Hz), `/fmu/out/battery_status` (1 Hz) | `/fmu/in/offboard_control_mode`, `/fmu/in/manual_control_setpoint`, `/fmu/in/vehicle_command` (logged on receipt) |
| `mock_entity_manager` | LOTUSim `entity_manager_plugin` | — | `/mas_cmd_array` action server (logs each goal as JSON, returns synthetic `name`/`entity` per cmd) |

## Run

```bash
colcon build --merge-install --packages-select lotusim_drone_mocks
source install/setup.bash

ros2 run lotusim_drone_mocks mock_px4_node
ros2 run lotusim_drone_mocks mock_entity_manager
```

## Acceptance checks (Sprint 2)

```bash
# ROS-06: PX4 telemetry is at the spec rate.
ros2 topic hz /fmu/out/vehicle_local_position   # ~50 Hz

# ROS-07: action endpoint exists.
ros2 action list                                 # contains /mas_cmd_array
```
