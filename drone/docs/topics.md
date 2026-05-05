# LOTUSim Drone Integration — Topic / Action Contract

> Project 2026-S1-45 · ROS2 lead: Ruojun Hu
> Source of truth: `ros2_plan.md` §2 (this file mirrors that section as a standalone deliverable for ROS-08)
> Coordinate convention: PX4 = NED, LOTUSim/Gazebo = ENU. NED↔ENU conversion lives in `tf_ned_enu.cpp`. Never flip axes inside payloads.

## 1. Upstream — (mocked) Pixhawk → ROS2

Source package: `px4_msgs`. Producer in this workspace is `lotusim_drone_mocks/mock_px4_node`.
QoS: PX4 default (`BEST_EFFORT`, `TRANSIENT_LOCAL`, `KEEP_LAST(5)`).

| Topic | Type | Rate | Notes |
|---|---|---|---|
| `/fmu/out/vehicle_local_position` | `px4_msgs/VehicleLocalPosition` | 50 Hz | Local NED position + velocity |
| `/fmu/out/vehicle_attitude` | `px4_msgs/VehicleAttitude` | 50 Hz | Quaternion `q = [w, x, y, z]`, FRD body → NED earth |
| `/fmu/out/vehicle_status` | `px4_msgs/VehicleStatus` | 2 Hz | `arming_state`, `nav_state`, failsafe flags |
| `/fmu/out/battery_status` | `px4_msgs/BatteryStatus` | 1 Hz | UI battery readout |

## 2. Downstream — ROS2 → Pixhawk

Producers: `lotusim_drone_mission/manual_control_node` (Sprint 3+).
QoS: `RELIABLE`, `KEEP_LAST` with depth as listed.

| Topic | Type | QoS depth | Notes |
|---|---|---|---|
| `/fmu/in/offboard_control_mode` | `px4_msgs/OffboardControlMode` | 1 | Offboard heartbeat (must precede setpoints) |
| `/fmu/in/manual_control_setpoint` | `px4_msgs/ManualControlSetpoint` | 1 (20 Hz) | Stick channels in `[-1, 1]`, throttle `[-1, 1]` |
| `/fmu/in/vehicle_command` | `px4_msgs/VehicleCommand` | 10 | Arm / disarm / takeoff (`VEHICLE_CMD_COMPONENT_ARM_DISARM = 400`) |

## 3. LOTUSim side — `lotusim_msgs`

Producer: real `entity_manager_plugin`; mocked by `lotusim_drone_mocks/mock_entity_manager`.

| Channel | Type | Direction | Notes |
|---|---|---|---|
| `/poses` (topic) | `lotusim_msgs/VesselPositionArray` | entity_manager → subscribers | Drone poses get appended into the same array |
| `/mas_cmd_array` (action) | `lotusim_msgs/MASCmdArray` | `lotusim_drone_bridge` → entity_manager | Goal: `MASCmd[] cmd`. Result: `bool[] result, string[] name, uint16[] entity`. Feedback: `bool fb` |

`MASCmd.cmd_type` values: `0 CREATE_CMD`, `1 DELETE_CMD`, `2 MOVE_CMD`. Pose payload is `geometry_msgs/Pose` in LOTUSim ENU.

## 4. UI ↔ ROS2 (new)

Producer: `lotusim_drone_mocks/mock_ui_cmd_pub` (planned, Sprint 3) or LOTUSim-UI-backend in production.
Consumer: `lotusim_drone_mission/manual_control_node`.

| Topic | Type | Rate | Notes |
|---|---|---|---|
| `/lotusim/ui/drone_manual_cmd` | `lotusim_drone_msgs/DroneManualCmd` | 20 Hz | `float32 throttle, roll, pitch, yaw`. Range `[-1, 1]` per channel; throttle uses PX4 manual setpoint convention (`-1` is min thrust) |

## 5. Topic ownership matrix

| Topic / Action | Owning package | Replaced by (real system) |
|---|---|---|
| `/fmu/out/*` | `lotusim_drone_mocks/mock_px4_node` | Micro-XRCE-DDS Agent + Pixhawk |
| `/fmu/in/*` | `lotusim_drone_mission/manual_control_node` | unchanged |
| `/mas_cmd_array` | `lotusim_drone_mocks/mock_entity_manager` | LOTUSim `entity_manager_plugin` |
| `/poses` | `lotusim_drone_mocks/mock_entity_manager` (planned) | LOTUSim `entity_manager_plugin` |
| `/lotusim/ui/drone_manual_cmd` | `lotusim_drone_mocks/mock_ui_cmd_pub` (planned) | LOTUSim-UI-backend (rclnodejs) |

## 6. Verification commands

```bash
# Sprint 2 acceptance
ros2 interface show lotusim_drone_msgs/msg/DroneManualCmd
ros2 run lotusim_drone_mocks mock_px4_node
ros2 topic hz /fmu/out/vehicle_local_position   # ≈ 50 Hz
ros2 run lotusim_drone_mocks mock_entity_manager
ros2 action list                                 # contains /mas_cmd_array
```
