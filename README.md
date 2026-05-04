# LOTUSim Drone Integration — ROS 2 packages

ROS 2 side of project **2026-S1-45 · LOTUSim Drone Integration**. Delivers a
mocked drone bridge between PX4 and LOTUSim so the rest of the stack can be
developed and tested without a real Pixhawk, the LOTUSim Gazebo plugins, or
the UI backend.

Scope this semester is deliberately ROS 2 + mocks only. Real Pixhawk /
`entity_manager_plugin` / UI integration is parked.

## Packages

| Package | Type | Role |
|---|---|---|
| [`lotusim_drone_msgs`](lotusim_drone_msgs/) | `ament_cmake` (msg) | Custom interfaces we own (currently `DroneManualCmd`). |
| [`lotusim_drone_bridge`](lotusim_drone_bridge/) | `ament_cmake` (C++) | PX4 telemetry → LOTUSim `mas_cmd_array`, NED↔ENU via tf2. *(Sprint 4)* |
| [`lotusim_drone_mission`](lotusim_drone_mission/) | `ament_python` | Manual control + mission recorder nodes. *(Sprint 3+)* |
| [`lotusim_drone_mocks`](lotusim_drone_mocks/) | `ament_python` | Stand-ins for Pixhawk, LOTUSim entity_manager, UI, env sensors. |

External dependencies cloned alongside this repo in the same colcon workspace:

- [`px4_msgs`](https://github.com/PX4/px4_msgs) — PX4 message schemas (no agent, no SITL).
- [`LOTUSim`](https://github.com/naval-group/LOTUSim) — only `interfaces/lotusim_msgs` is built; the C++ Gazebo systems are not.

The end-to-end topic / action contract (PX4 ↔ bridge ↔ LOTUSim ↔ UI) lives in
[`docs/topics.md`](docs/topics.md).

## Status

- [x] **Sprint 1 — Environment Foundation** (ROS-01..04): workspace, `px4_msgs`, `lotusim_msgs`, four package skeletons.
- [x] **Sprint 2 — Msgs + Mocks** (ROS-05..08): `DroneManualCmd`, `mock_px4_node`, `mock_entity_manager`, topic contract doc.
- [ ] **Sprint 3** — `manual_control_node`, arming state machine, rosbag E2E.
- [ ] **Sprint 4** — `drone_bridge_node` (NED→ENU), `mock_env_sensors`, `mission_recorder_node`.
- [ ] **Sprint 5** — `full_mock_demo.launch.py`, final demo.

## Build

The canonical environment is **ROS 2 Jazzy on Ubuntu 24.04**, typically run as
a Docker container. See `dev_setup.md` in the parent workspace for the full
Docker recipe.

Inside a colcon workspace where this repo lives at `src/ROS2/` next to
`src/px4_msgs/` and `src/LOTUSim/`:

```bash
sudo apt install -y python3-colcon-common-extensions ros-jazzy-geographic-msgs
source /opt/ros/jazzy/setup.bash

colcon build --merge-install --packages-select \
    lotusim_msgs px4_msgs lotusim_drone_msgs lotusim_drone_mocks
source install/setup.bash
```

`lotusim_msgs` is the only `LOTUSim` subpackage that needs to be built — the
C++ Gazebo plugins pull in Gazebo Harmonic and are out of scope here.

## Run mocks

```bash
ros2 run lotusim_drone_mocks mock_px4_node          # publishes /fmu/out/*, logs /fmu/in/*
ros2 run lotusim_drone_mocks mock_entity_manager    # serves /mas_cmd_array action
```

## Acceptance checks

```bash
# ROS-05
ros2 interface show lotusim_drone_msgs/msg/DroneManualCmd

# ROS-06
ros2 topic hz /fmu/out/vehicle_local_position   # expect ~50 Hz

# ROS-07
ros2 action list                                # expect /mas_cmd_array
```

## Coordinates

PX4 uses NED, LOTUSim/Gazebo uses ENU. The conversion is isolated in
`lotusim_drone_bridge/src/tf_ned_enu.cpp` (Sprint 4); message payloads are
never axis-flipped in place.

## Replacing mocks with the real systems

When the rest of the stack lands, the mocks drop in 1:1 — see the *replaced
by* column in [`docs/topics.md`](docs/topics.md). No downstream node should
need code changes.
