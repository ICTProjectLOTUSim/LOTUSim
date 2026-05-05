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

## Workspace layout

This repo is meant to live at `src/ROS2/` inside a colcon workspace, next to
the two cloned dependencies:

```
<workspace>/
├── src/
│   ├── ROS2/          # this repo
│   ├── px4_msgs/      # https://github.com/PX4/px4_msgs (release/1.15)
│   └── LOTUSim/       # https://github.com/naval-group/LOTUSim (only lotusim_msgs is built)
├── build/   install/   log/    # populated by colcon
```

`<workspace>` is mounted into the container as `/lotusim_ws`.

## Quickstart with Docker

The canonical environment is **ROS 2 Jazzy on Ubuntu 24.04** in a container.
Host install only needs Docker — no ROS, no colcon.

### 1. Pull the image

```bash
docker pull ros:jazzy
```

### 2. Start a long-lived dev container

Run from the host. Replace `<workspace>` with the path that contains `src/`,
e.g. `~/lotusim_ws` or `~/Coding/ICT`.

```bash
docker run -it \
    --name lotusim-dev \
    -v <workspace>:/lotusim_ws \
    -w /lotusim_ws \
    -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 \
    ros:jazzy bash
```

Re-attach later:

```bash
docker start -ai lotusim-dev          # resume
docker exec  -it lotusim-dev bash     # extra terminal in the same container
```

### 3. One-time setup inside the container

```bash
apt update && apt install -y \
    python3-colcon-common-extensions \
    ros-jazzy-geographic-msgs

echo 'source /opt/ros/jazzy/setup.bash'        >> ~/.bashrc
echo 'source /lotusim_ws/install/setup.bash'   >> ~/.bashrc
source ~/.bashrc
```

### 4. Build the mock stack

```bash
cd /lotusim_ws
colcon build --merge-install --packages-select \
    lotusim_msgs px4_msgs lotusim_drone_msgs lotusim_drone_mocks
source install/setup.bash
```

`lotusim_msgs` is the only `LOTUSim` subpackage that gets built — the C++
Gazebo plugins pull in Gazebo Harmonic and are out of scope here.

### 5. Run mocks

Two terminals into the same container (`docker exec -it lotusim-dev bash`):

```bash
# terminal 1
ros2 run lotusim_drone_mocks mock_px4_node          # publishes /fmu/out/*, logs /fmu/in/*

# terminal 2
ros2 run lotusim_drone_mocks mock_entity_manager    # serves /mas_cmd_array action
```

### 6. Acceptance checks

In a third terminal in the same container:

```bash
# ROS-05
ros2 interface show lotusim_drone_msgs/msg/DroneManualCmd

# ROS-06
ros2 topic hz /fmu/out/vehicle_local_position   # expect ~50 Hz

# ROS-07
ros2 action list                                # expect /mas_cmd_array
```

### Common gotchas

| Symptom | Fix |
|---|---|
| `ros2: command not found` after `docker exec` | `source /opt/ros/jazzy/setup.bash` (add to `~/.bashrc`). |
| `ros2 topic list` hangs | Make sure the container was started with `-e FASTDDS_BUILTIN_TRANSPORTS=UDPv4`. |
| `colcon build` tries to build the LOTUSim Gazebo systems and fails | Use `--packages-select` as shown in step 4 — never `colcon build` without it. |
| `lotusim_msgs` build complains about `geographic_msgs` | `apt install ros-jazzy-geographic-msgs` (step 3). |
| Two nodes in different containers can't see each other | Easiest: run both in the same container. Cross-container DDS needs `--network host` on Linux. |

## Coordinates

PX4 uses NED, LOTUSim/Gazebo uses ENU. The conversion is isolated in
`lotusim_drone_bridge/src/tf_ned_enu.cpp` (Sprint 4); message payloads are
never axis-flipped in place.

## Replacing mocks with the real systems

When the rest of the stack lands, the mocks drop in 1:1 — see the *replaced
by* column in [`docs/topics.md`](docs/topics.md). No downstream node should
need code changes.
