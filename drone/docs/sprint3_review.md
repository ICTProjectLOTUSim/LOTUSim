# Sprint 3 Review — ROS2 Manual Control Foundation

Project 2026-S1-45 · ROS2 lead: Ruojun Hu · Closed: 2026-05-11

## Outcome vs. Goal

Sprint 3 delivered the full mock-first manual control chain end-to-end. A UI
waveform reaches `/fmu/in/manual_control_setpoint` through `manual_control_node`,
an offboard-mode heartbeat runs at 10 Hz, and arming round-trips through a
`std_srvs/SetBool` service and back via `/fmu/out/vehicle_status`.

| Subtask | Status |
|---|---|
| 1/8 Bootstrap workspace + external schemas | Done |
| 2/8 Scaffold four packages | Done |
| 3/8 `DroneManualCmd.msg` + `docs/topics.md` | Done |
| 4/8 `mock_px4_node` (`/fmu/out/*`, logs `/fmu/in/*`) | Done |
| 5/8 `mock_entity_manager` (`/mas_cmd_array` action) | Done |
| 6/8 `manual_control_node` + `mock_ui_cmd_pub` | Done |
| 7/8 Arming state machine + pytest + mock arming feedback | Done |
| 8/8 Launch file + rosbag evidence + handoff notes | Done |

## What works

- `lotusim_drone_mission/launch/sprint3_demo.launch.py` brings up the full
  four-node chain (`mock_px4_node`, `mock_entity_manager`, `mock_ui_cmd_pub`,
  `manual_control_node`) in one command.
- `mock_ui_cmd_pub` publishes `/lotusim/ui/drone_manual_cmd` at 20 Hz with
  `sine` / `hold` / `step` waveforms (ROS parameter `mode`).
- `manual_control_node` re-emits each UI command as
  `ManualControlSetpoint` within one frame and publishes
  `OffboardControlMode` at 10 Hz (configurable via
  `offboard_heartbeat_hz`).
- `/manual_control_node/arm_disarm` (`std_srvs/SetBool`) drives
  `VEHICLE_CMD_COMPONENT_ARM_DISARM` (400). `mock_px4_node` flips its
  internal `arming_state` on receipt, so `/fmu/out/vehicle_status` advances
  to `ARMING_STATE_ARMED` within the next 0.5 s tick.
- `lotusim_drone_mission/test/test_arming_state_machine.py` covers idle,
  arm, disarm, no-op, force, and unknown-state branches.

## What is still unstable / deferred

- **QoS divergence from `ros2_plan.md` §2.2.** The plan listed `/fmu/in/*`
  as `RELIABLE`, but `mock_px4_node` subscribes with `BEST_EFFORT +
  TRANSIENT_LOCAL`, and DDS rejects a `RELIABLE/VOLATILE` publisher
  against a `TRANSIENT_LOCAL` subscriber. `manual_control_node` therefore
  publishes with `BEST_EFFORT + TRANSIENT_LOCAL + KEEP_LAST(depth)`, which
  also matches what PX4 over uXRCE-DDS actually does. Update the contract
  doc in Sprint 4.
- **No ROS-level integration test.** Arming is covered by unit tests and
  the recorded bag; an `launch_testing` test would close the loop but is
  out of scope this sprint.
- **`mock_entity_manager` does not yet publish `/poses`.** The contract
  reserves the topic, but Sprint 3 only needed `/mas_cmd_array`. Add when
  `lotusim_drone_bridge` lands in Sprint 4.
- **Timing jitter.** Heartbeat and setpoint timers use rclpy
  `create_timer`, which drifts under host CPU contention. Acceptable for
  the mock chain; for hardware integration, switch to a deadline-aware
  publisher.

## Sprint 4 action list (handoff)

1. **`lotusim_drone_bridge` C++ implementation.** Subscribe
   `/fmu/out/vehicle_local_position` and `/fmu/out/vehicle_attitude`,
   convert NED → ENU in `tf_ned_enu.cpp`, send `MASCmdArray` goals to
   `/mas_cmd_array`. All axis conversion stays inside the tf2 helper;
   never flip components inside payloads.
2. **GTest for `tf_ned_enu`.** Round-trip identity and known-vector tests.
3. **`mission_recorder_node`** (`lotusim_drone_mission`, Python). Wrap
   `rosbag2_py` to record the contract topics for offline replay.
4. **`mock_env_sensors`** (`lotusim_drone_mocks`). Publish AIS / IMU /
   subsea pressure stand-ins matching `lotusim_sensor_msgs` schemas.
5. **Reconcile `docs/topics.md` QoS column** with the BEST_EFFORT +
   TRANSIENT_LOCAL reality on `/fmu/in/*`.
6. **`full_mock_demo.launch.py`** (Sprint 5 deliverable). Extend
   `sprint3_demo.launch.py` to also spawn the bridge, mission recorder,
   and env sensors.

## Evidence

See `docs/evidence/sprint3/README.md` for the recorded bag and the
verification command transcripts.
