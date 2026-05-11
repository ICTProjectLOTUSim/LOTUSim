# Integration Guide — LOTUSim Drone ROS2 Packages

Project 2026-S1-45 · ROS2 lead: Ruojun Hu
Audience: anyone who needs to publish to, subscribe from, or extend the
drone ROS2 packages.

> Source of truth for topic / action schemas: [`topics.md`](./topics.md).
> Sprint status / known issues: [`sprint3_review.md`](./sprint3_review.md).
> This file tells you **how to wire your code in**.

---

## 1. Workspace bring-up

Everything lives under `src/LOTUSim/drone/`. The host workspace root is
`/Users/zrzz/Coding/ICT/` which is bind-mounted into the Docker container
at `/lotusim_ws`.

```bash
# Inside the ros:humble container:
source /opt/ros/humble/setup.bash
cd /lotusim_ws

colcon build --merge-install --packages-select \
    lotusim_drone_msgs lotusim_drone_mocks lotusim_drone_mission

source install/setup.bash
```

If `ros2: command not found` after sourcing `install/setup.bash`, you
forgot the underlay (`/opt/ros/humble/setup.bash`). The workspace overlay
does not pull it in automatically.

---

## 2. One-command demo (start here)

```bash
ros2 launch lotusim_drone_mission sprint3_demo.launch.py
```

This spins up the full mock chain (`mock_px4_node`,
`mock_entity_manager`, `mock_ui_cmd_pub`, `manual_control_node`). Use it
as a development backdrop — your new node can come up against this
running setup and start exchanging messages immediately.

Optional waveform on the UI driver:
```bash
ros2 launch lotusim_drone_mission sprint3_demo.launch.py ui_mode:=hold
# values: sine (default) | hold | step
```

---

## 3. The four integration surfaces

### 3.1 `/lotusim/ui/drone_manual_cmd` — manual stick input (you publish)

If you are building a UI replacement or a higher-level controller that
wants to drive the drone in manual stick mode, publish here.

| Field | Type | Range | Meaning |
|---|---|---|---|
| `throttle` | float32 | `[-1, 1]` | PX4 convention: `-1` = min thrust |
| `roll` | float32 | `[-1, 1]` | |
| `pitch` | float32 | `[-1, 1]` | |
| `yaw` | float32 | `[-1, 1]` | yaw rate command |

QoS: `RELIABLE`, `VOLATILE`, `KEEP_LAST(10)`. Default rclpy publisher QoS
works.

Recommended rate: **20 Hz** (matches what `manual_control_node`
re-emits). Higher is fine; lower means slower control loop response.

Python example:
```python
import rclpy
from rclpy.node import Node
from lotusim_drone_msgs.msg import DroneManualCmd


class MyUiBridge(Node):
    def __init__(self):
        super().__init__('my_ui_bridge')
        self.pub = self.create_publisher(
            DroneManualCmd, '/lotusim/ui/drone_manual_cmd', 10)
        self.create_timer(1.0 / 20.0, self._tick)

    def _tick(self):
        msg = DroneManualCmd()
        msg.throttle = 0.5
        msg.roll = 0.0
        msg.pitch = 0.0
        msg.yaw = 0.0
        self.pub.publish(msg)


def main():
    rclpy.init()
    rclpy.spin(MyUiBridge())
    rclpy.shutdown()
```

### 3.2 `/manual_control_node/arm_disarm` — arming service (you call)

Trigger PX4 arm / disarm via `std_srvs/SetBool`. The state machine
inside `manual_control_node` deduplicates redundant requests (calling
`arm` when already armed returns `noop: already ARMED` and emits no
VehicleCommand).

CLI usage:
```bash
ros2 service call /manual_control_node/arm_disarm \
    std_srvs/srv/SetBool '{data: true}'    # arm
ros2 service call /manual_control_node/arm_disarm \
    std_srvs/srv/SetBool '{data: false}'   # disarm
```

Python client:
```python
from std_srvs.srv import SetBool

class MyArmer(Node):
    def __init__(self):
        super().__init__('my_armer')
        self.cli = self.create_client(
            SetBool, '/manual_control_node/arm_disarm')
        self.cli.wait_for_service(timeout_sec=5.0)

    def arm(self, on: bool) -> str:
        req = SetBool.Request()
        req.data = on
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result().message
```

### 3.3 `/mas_cmd_array` — entity manager action (you send goals)

This is the action the (real or mocked) entity manager exposes for
spawning / moving / deleting vessels and drones in the LOTUSim scene.
The mock currently just logs goals and replies success; the real
`entity_manager_plugin` will execute them in Gazebo.

Action type: `lotusim_msgs/action/MASCmdArray`. See
[`topics.md` §3](./topics.md) for `MASCmd` field semantics.

Goal payload:
```
MASCmd[] cmd
```

`cmd_type`:
- `0` CREATE — needs `model_name`, `sdf_file` or `sdf_string`, pose
- `1` DELETE — needs `entity` (id) or `vessel_name`
- `2` MOVE   — needs `entity` or `vessel_name`, pose

Pose payload is `geometry_msgs/Pose` in **LOTUSim ENU**. Do not pass
PX4 NED here — the bridge layer (Sprint 4) will do the conversion;
direct callers should already be in ENU.

Python example:
```python
from rclpy.action import ActionClient
from lotusim_msgs.action import MASCmdArray
from lotusim_msgs.msg import MASCmd

class MyEntityClient(Node):
    def __init__(self):
        super().__init__('my_entity_client')
        self.ac = ActionClient(self, MASCmdArray, 'mas_cmd_array')
        self.ac.wait_for_server(timeout_sec=5.0)

    def spawn(self, model: str, x: float, y: float, z: float):
        cmd = MASCmd()
        cmd.cmd_type = 0  # CREATE
        cmd.model_name = model
        cmd.vessel_name = f'{model}_1'
        cmd.vessel_position.position.x = x
        cmd.vessel_position.position.y = y
        cmd.vessel_position.position.z = z
        cmd.vessel_position.orientation.w = 1.0

        goal = MASCmdArray.Goal()
        goal.cmd = [cmd]
        future = self.ac.send_goal_async(goal)
        # ... handle accept / result
```

### 3.4 `/fmu/out/*` — PX4 telemetry (you subscribe)

If you want to observe drone state (position, attitude, arming, battery),
subscribe to the `/fmu/out/*` topics published by `mock_px4_node`
(future: real Pixhawk via uXRCE-DDS Agent).

| Topic | Type | Rate |
|---|---|---|
| `/fmu/out/vehicle_local_position` | `px4_msgs/VehicleLocalPosition` | 50 Hz, **NED** |
| `/fmu/out/vehicle_attitude` | `px4_msgs/VehicleAttitude` | 50 Hz, FRD→NED quaternion |
| `/fmu/out/vehicle_status` | `px4_msgs/VehicleStatus` | 2 Hz |
| `/fmu/out/battery_status` | `px4_msgs/BatteryStatus` | 1 Hz |

⚠️ **QoS must match.** These publishers use PX4 convention:
`BEST_EFFORT` + `TRANSIENT_LOCAL` + `KEEP_LAST(5)`. Default rclpy
subscriber QoS (`RELIABLE` + `VOLATILE`) **will silently fail to
receive any messages**. Use this profile in code:

```python
from rclpy.qos import (
    QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy)

def px4_out_sub_qos() -> QoSProfile:
    return QoSProfile(
        reliability=QoSReliabilityPolicy.BEST_EFFORT,
        durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=5,
    )

self.create_subscription(
    VehicleStatus, '/fmu/out/vehicle_status',
    self._on_status, px4_out_sub_qos())
```

For `ros2 topic echo` from the CLI, you need explicit flags:
```bash
ros2 topic echo --once \
    --qos-reliability best_effort --qos-durability transient_local \
    /fmu/out/vehicle_status
```

Coordinate frame note: `vehicle_local_position` is **NED** (X north, Y
east, Z down). Convert to ENU before mixing with Gazebo / `/poses` data.
The Sprint 4 `lotusim_drone_bridge` package owns this conversion in
`tf_ned_enu.cpp` — once it lands, prefer using the tf2 transform over
hand-rolling sign flips.

---

## 4. Where to put your code

| You are building... | Add it under... | Type |
|---|---|---|
| New PX4 downstream node (e.g. position mission, RTL controller) | `lotusim_drone_mission/lotusim_drone_mission/your_node.py` | ament_python |
| New mock for an external dependency | `lotusim_drone_mocks/lotusim_drone_mocks/mock_your_thing.py` | ament_python |
| New C++ bridge between PX4 and LOTUSim domains | `lotusim_drone_bridge/src/your_translator.cpp` | ament_cmake |
| New message / service / action contract | `lotusim_drone_msgs/{msg,srv,action}/YourType.{msg,srv,action}` + update `CMakeLists.txt` | ament_cmake |

For ament_python additions, remember three things:
1. Register the executable in `setup.py` under `entry_points.console_scripts`.
2. Add any new ROS deps to `package.xml` (`<depend>...</depend>`).
3. Re-run `colcon build --merge-install --packages-select <your_pkg>`.

For new messages, edit `lotusim_drone_msgs/CMakeLists.txt`:
```cmake
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/DroneManualCmd.msg"
  "msg/YourNewMsg.msg"
)
```

Then rebuild and `source install/setup.bash` so generated bindings show
up on `PYTHONPATH`.

---

## 5. QoS reference card

The single biggest source of "my publisher is sending but the subscriber
sees nothing" issues. Memorize this table:

| Surface | Profile |
|---|---|
| `/fmu/out/*` (pub & matching sub) | `BEST_EFFORT` + `TRANSIENT_LOCAL` + depth 5 |
| `/fmu/in/*` (pub & matching sub) | `BEST_EFFORT` + `TRANSIENT_LOCAL` + depth 1 or 10 |
| `/lotusim/ui/drone_manual_cmd` | `RELIABLE` + `VOLATILE` + depth 10 (rclpy default) |
| Services / actions | rmw default, no special handling needed |

Rule of thumb for compatibility:
- Publisher's offered policy must be **at least as strong** as the
  subscriber's requested policy (`RELIABLE > BEST_EFFORT`,
  `TRANSIENT_LOCAL > VOLATILE`).
- If they don't match, DDS silently drops the connection. Check with
  `ros2 topic info <topic> --verbose`.

---

## 6. Coordinate convention (read before touching positions)

- **PX4 = NED** (X north, Y east, Z down). All `/fmu/out/vehicle_*` and
  `/fmu/in/trajectory_setpoint` payloads are NED.
- **LOTUSim / Gazebo / `/poses` / `/mas_cmd_array` = ENU** (X east, Y
  north, Z up).
- **All conversion lives in `tf_ned_enu.cpp`** (Sprint 4 deliverable in
  `lotusim_drone_bridge`). **Do not flip axes inline in your message
  payloads.** That's a quick way to make pose bugs untraceable across
  three nodes.

User-facing inputs (CLI, UI, target coordinates the operator types in)
should be in ENU. Convert to NED only at the PX4 boundary.

---

## 7. Build / run / test workflow

```bash
# Build only your package (fast iteration):
colcon build --merge-install --packages-select <your_pkg>
source install/setup.bash

# Run a single node:
ros2 run <your_pkg> <your_executable>

# Run the full mock chain in another shell:
ros2 launch lotusim_drone_mission sprint3_demo.launch.py

# Inspect what's on the bus:
ros2 topic list
ros2 topic info /fmu/out/vehicle_status --verbose   # check QoS
ros2 topic hz /lotusim/ui/drone_manual_cmd
ros2 node list
ros2 service list
ros2 action list

# Unit tests (Python pkg):
colcon test --merge-install --packages-select <your_pkg>
colcon test-result --verbose --test-result-base build/<your_pkg>
```

---

## 8. Known limitations / things to ask the lead before assuming

- `mock_px4_node` publishes a **static `cos/sin` orbit** on
  `vehicle_local_position`. It does **not** respond to setpoint inputs.
  If your node needs "drone actually moves toward target" in the mock
  era, talk to the ROS2 lead — that's a planned mock kinematics task,
  not done yet.
- `mock_entity_manager` does **not yet publish `/poses`**. It only
  serves `/mas_cmd_array`. If you depend on `/poses`, flag it.
- Real Pixhawk / real UI-backend / real `entity_manager_plugin` are
  **out of scope this semester** by project decision (see
  `ros2_plan.md §0`). Build against the mocks; the contract topics are
  the integration boundary.
- The `lotusim_drone_bridge` package is currently a skeleton (no C++
  yet). NED↔ENU conversion + `MASCmdArray` action client land in
  Sprint 4. Don't write your own conversion in a mission node — wait
  for the bridge.

---

## 9. Contact / handoff

- ROS2 lead: Ruojun Hu.
- Plan / sprint tickets: `ros2_plan.md` at workspace root.
- Topic / action contract: [`topics.md`](./topics.md).
- Sprint status: [`sprint3_review.md`](./sprint3_review.md).

Before adding a new topic or breaking an existing schema, raise it with
the ROS2 lead and update `topics.md` in the same PR.
