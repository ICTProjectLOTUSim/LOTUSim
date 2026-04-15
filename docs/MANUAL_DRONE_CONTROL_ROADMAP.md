# Manual Drone Control Roadmap for LOTUSim

## Current State of the Project

### What already exists

- The project has an `x500` quadcopter model at `assets/models/x500/`.
- The drone model already includes:
  - 4 rotors
  - IMU sensor
  - Air pressure sensor
  - `gz-sim-multicopter-motor-model-system` plugins that receive motor speed commands.
- There is an `aerialWorld.world` at `assets/worlds/aerialWorld.world`.
- Gazebo Harmonic and ROS 2 are already used in the repository architecture.

### What is currently missing for manual control

- No PX4 / Pixhawk SITL integration in this repository.
- No MAVLink bridge setup.
- No joystick or keyboard teleoperation node.
- No multicopter velocity controller plugin wiring for user-level control input.
- Aerial world uses zero gravity in current configuration (`<gravity>0 0 0</gravity>`), which is not suitable for realistic drone flight.

---

## Target System Architecture

For manual control with realistic behavior, the team should target this flow:

1. User input device (joystick/gamepad/QGroundControl)
2. PX4 autopilot in SITL mode (Pixhawk-equivalent firmware in simulation)
3. ROS 2 communication layer and bridges
4. Gazebo Harmonic world with x500 model + flight dynamics plugins
5. Sensor feedback loop from Gazebo back to PX4

This creates a full closed-loop system:

- Input commands -> controller -> simulated motors
- Simulated sensor outputs -> controller state estimation -> stable flight

---

## Work Breakdown by Area

## 1) Gazebo Workstream (Primary focus for your role)

This is the core simulation-side work needed to make the drone controllable.

### 1.1 Fix flight physics in `aerialWorld.world`

Current values are not flight-ready.

- Change gravity to:
  - `<gravity>0 0 -9.8066</gravity>`
- Improve physics update timing for flight:
  - `max_step_size` around `0.004`
  - `real_time_update_rate` around `250`

Why: PX4 and multicopter control loops need much faster, stable simulation timing.

### 1.2 Spawn x500 in the aerial world

Include the x500 model in `assets/worlds/aerialWorld.world` if not already included.

Why: currently the world is mostly infrastructure plugins; manual flight requires an actual drone entity spawned at startup.

### 1.3 Add multicopter velocity control layer

The x500 already has motor model plugins, but manual control also needs a controller plugin that converts velocity setpoints into motor commands.

Use Gazebo's multicopter control system (velocity control path) and map it to the x500 rotors.

Why: without this layer, high-level control input (e.g., `cmd_vel`) cannot be translated into rotor speeds in a stable way.

### 1.4 Complete required flight sensor set

Current model has IMU + air pressure. Add and validate:

- Magnetometer
- GPS/NavSat

Target rates (starting point):

- IMU: 50 Hz or higher
- Magnetometer: 25-50 Hz
- Barometer: 25-50 Hz
- GPS: 5-10 Hz

Why: PX4 requires these sensor streams for robust attitude and position control.

### 1.5 Bridge Gazebo transport <-> ROS 2 topics

Set up `ros_gz_bridge` for:

- Sensor data out (IMU, pressure, magnetometer, GPS, odometry)
- Command inputs in (velocity or actuator commands)

Why: Gazebo transport messages are not automatically ROS 2 messages.

### 1.6 Validate and tune drone behavior

Perform staged checks:

1. Hover stability
2. Basic manual commands (up/down/forward/yaw)
3. Wind disturbance response
4. Sensor sanity checks
5. Controller gain tuning

---

## 2) ROS 2 Workstream (team dependency)

Needed to make control and observability practical.

### 2.1 Teleop input node

Implement joystick/gamepad node:

- Subscribe to `sensor_msgs/msg/Joy`
- Publish control setpoints (velocity/offboard setpoints)

Optional:

- Keyboard teleop fallback

### 2.2 Launch orchestration

Create one ROS 2 launch workflow that starts:

- Gazebo world
- Bridges
- Teleop node
- PX4-related processes (if included in same launch)

### 2.3 Monitoring and tooling

Provide standard introspection:

- Topic echo scripts
- Flight-state dashboards/logging
- Failsafe indicators (arming status, offboard status, link status)

---

## 3) PX4 / Pixhawk Workstream (team dependency)

Needed for realistic autopilot behavior.

### 3.1 PX4 SITL setup

- Build PX4-Autopilot SITL target for Gazebo Harmonic.
- Use x500-compatible airframe configuration.

### 3.2 MAVLink and ground station flow

- Configure MAVLink UDP endpoints.
- Connect QGroundControl for:
  - Arming
  - Flight mode changes
  - Manual control/virtual joystick

### 3.3 PX4-ROS 2 bridge layer

Set up micro XRCE-DDS agent so PX4 uORB data is available in ROS 2.

Why: this is now the standard modern PX4-to-ROS 2 path.

---

## Recommended Execution Plan (Practical Sequence)

### Phase A: Fast minimal manual control (without PX4)

Goal: prove controllability quickly.

1. Fix aerial world gravity and physics timing.
2. Spawn x500.
3. Wire multicopter velocity control plugin.
4. Add ROS-Gazebo bridge for `cmd_vel`.
5. Drive drone manually via ROS 2 teleop.

Outcome: fast demo of manual drone movement in simulator.

### Phase B: Full realistic control stack (with PX4)

1. Integrate PX4 SITL + x500.
2. Add MAVLink/QGroundControl control flow.
3. Feed Gazebo sensors into PX4 loop.
4. Validate arming, mode switching, stabilized flight.
5. Tune and document repeatable test scenarios.

Outcome: simulation behaves closer to real Pixhawk workflow.

---

## Priority Task Table (Gazebo Owner)

1. Flight physics fix in `aerialWorld.world` (highest priority)
2. x500 spawn in world
3. Multicopter velocity controller wiring
4. Sensor completion (mag + GPS)
5. Topic bridges (`ros_gz_bridge`)
6. Hover and command-response tuning
7. End-to-end test with team ROS/PX4 stack

---

## Deliverables You Can Own

1. A working `aerialWorld.world` configured for drone flight.
2. x500 model/control plugin configuration committed in repo.
3. Sensor + bridge mapping documentation (`Gazebo topic -> ROS 2 topic`).
4. Test checklist for "manual control ready".
5. Tuning notes (what parameters were changed and why).

---

## Acceptance Criteria ("Manual Control Ready")

The internship goal can be considered achieved when all are true:

1. Drone can arm and disarm reliably.
2. Drone can be manually controlled (throttle, pitch, roll, yaw) in simulator.
3. Drone can hold stable hover for at least 30 seconds.
4. Sensor streams are continuous and plausible.
5. Manual control path is documented so another team member can reproduce it.

---

## Useful References

- PX4 + Gazebo Harmonic: [https://docs.px4.io/main/en/sim_gazebo_gz/](https://docs.px4.io/main/en/sim_gazebo_gz/)
- Gazebo Sim API docs: [https://gazebosim.org/api/sim/](https://gazebosim.org/api/sim/)
- `ros_gz_bridge`: [https://github.com/gazebosim/ros_gz](https://github.com/gazebosim/ros_gz)
- PX4 middleware (XRCE-DDS): [https://docs.px4.io/main/en/middleware/uxrce_dds/](https://docs.px4.io/main/en/middleware/uxrce_dds/)

