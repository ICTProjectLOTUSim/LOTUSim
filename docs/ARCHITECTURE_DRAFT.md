# LOTUSim Drone Control — Architecture Draft

**For:** Client meeting  
**Date:** May 2026  
**Goal:** Integrate PX4 flight controller into LOTUSim, usable from the
LOTUSim-generic-scenario framework

---

## 1. The Two Repos

| Repo | Role |
|------|------|
| `~/lotusim_ws/src/LOTUSim` | Core simulation engine — Gazebo worlds, SDF models, `lotusim` CLI |
| `~/Documents/workspace/lotusim/LOTUSim-generic-scenario` | Scenario runner — JSON configs, Python agent plugins, XDyn, Unity |

The generic scenario **calls into** LOTUSim core. It does not replace it.
All worlds and models live in the core repo.

---

## 2. How the Generic Scenario Currently Launches

```
scenario_launch.sh --config defenseScenario.json
        │
        ├── reads aerial_domain: true  →  lotusim run aerialWorld.world
        │                                 (separate gnome-terminal)
        ├── reads world_file            →  lotusim run defenseScenario.world
        │                                 (separate gnome-terminal)
        ├── for each marine agent with xdyn: true  →  xdyn-for-cs (separate terminal)
        ├── optionally:  Unity executable
        │
        └── ros2 run simulation_run main --config defenseScenario.json
                │
                ├── spawns ROS 2 agent nodes (LRAUV, BlueROV2, FREMM, ...)
                └── spawns X500 agent node  ← aerial, no XDyn, no PX4 today
```

The **X500 agent** (`src/agents/x500/x500.py`) is a Python plugin loaded via
`lotusim.agents` entry points. It currently has no flight controller — the
Gazebo velocity controller plugin handles flight.

---

## 3. What Is Implemented Today (LOTUSim Core)

### Simulation world — `drone_test.world`

- Realistic gravity (`-9.8066 m/s²`), 250 Hz physics
- Ground plane
- X500 model (`x500_manual_control`) with all required sensors:
  - IMU (50 Hz), Air pressure (50 Hz), Magnetometer (50 Hz), GPS/NavSat (10 Hz)
  - 4 motor model plugins
  - Gazebo `MulticopterVelocityControl` plugin ← **temporary, replaced by PX4**

### ROS 2 bridge — `config/bridges/drone_teleop_bridges.yaml`

Connects ROS 2 ↔ Gazebo for monitoring and keyboard control:

| ROS 2 topic | Direction | Purpose |
|---|---|---|
| `/drone/cmd_vel` | → Gazebo | velocity commands |
| `/drone/enable` | → Gazebo | arm/disarm |
| `/drone/imu` | ← Gazebo | sensor data |
| `/drone/navsat` | ← Gazebo | GPS data |
| `/drone/magnetometer` | ← Gazebo | compass data |
| `/drone/air_pressure` | ← Gazebo | barometer data |

### Keyboard control — working today

```
Keyboard  →  teleop_twist_keyboard  →  ros_gz_bridge  →  Gazebo velocity controller  →  X500
```

**Can it be controlled with a keyboard? Yes — it works today.**

---

## 4. Target Architecture — PX4 in the Generic Scenario

```
┌──────────────────────────────────────────────────────────────────────────┐
│               TARGET ARCHITECTURE (full integration)                     │
└──────────────────────────────────────────────────────────────────────────┘

  scenario_launch.sh --config defenseScenario.json
          │
          ├── lotusim run drone_px4.world          ← NEW world (no velocity controller)
          │       │  Gazebo Harmonic simulation
          │       │  x500 model with 4 sensors + motor models
          │       │
          │       │  gz-transport topics exposed:
          │       │    /world/drone_px4/model/x500_0/link/base_link/sensor/imu_sensor/imu
          │       │    /world/drone_px4/model/x500_0/link/base_link/sensor/navsat_sensor/navsat
          │       │    /world/drone_px4/model/x500_0/link/base_link/sensor/...
          │       │    /model/x500_0/command/motor_speed  ← written by PX4
          │
          ├── PX4 SITL (instance per X500 agent)   ← NEW process
          │       │  same firmware as real Pixhawk
          │       │  reads sensor topics from Gazebo (gz-transport, no bridge needed)
          │       │  writes /model/x500_0/command/motor_speed to Gazebo
          │       │  exposes MAVLink on UDP port 14550
          │
          ├── QGroundControl                        ← control station
          │       │  connects to PX4 via MAVLink UDP
          │       │  provides: arm/disarm, flight modes, joystick/keyboard input
          │
          ├── ros_gz_bridge (sensor monitoring)     ← optional, for ROS 2 tools
          │       bridges sensor topics to /drone/imu, /drone/navsat, ...
          │
          └── ros2 run simulation_run main --config defenseScenario.json
                  │
                  └── X500 agent node (modified)
                          │
                          ├── today:   does nothing (velocity controller handles flight)
                          └── target:  spawns PX4 SITL process for this agent instance
                                       configures sensor topic paths per drone instance
                                       opens QGroundControl connection
```

---

## 5. What Changes in Each Repo

### LOTUSim core (`~/lotusim_ws/src/LOTUSim`)

| File | Change |
|------|--------|
| `assets/worlds/drone_px4.world` | **New file** — copy of drone_test.world but with `MulticopterVelocityControl` removed. Motor models remain. |
| `assets/models/x500_manual_control/model.sdf` | No change — sensors already match PX4's expected format |
| `launch/lotusim` | Already fixed (`GZ_CONFIG_PATH` fix for `gz sim` command) |

### LOTUSim-generic-scenario (`~/Documents/workspace/lotusim/LOTUSim-generic-scenario`)

| File | Change |
|------|--------|
| `src/agents/x500/x500/x500.py` | **Extended** — `__init__` spawns a PX4 SITL subprocess, assigns unique MAVLink port per instance |
| `src/simulation_run/simulation_run/simulation_runner.py` | **Modified** — replace `aerialWorld.world` with `drone_px4.world` when PX4 agents are present |
| `src/simulation_run/config/defenseScenario.json` | **Extended** — add `"px4": true` flag to X500 agent config |
| `src/gz_ros2_bridge/launch/bridge_nodes.launch.py` | **Extended** — add drone sensor bridges (IMU, GPS, etc.) |

---

## 6. X500 Agent — Before vs After

**Today (`x500.py`):**
```python
class X500(Agent):
    def __init__(self, sdf_string, world_name, xdyn_enabled=False):
        self.domains = ["Aerial"]
        super().__init__(sdf_string, world_name, self.xdyn_port)
        # no flight controller process started
```

**After PX4 integration:**
```python
class X500(Agent):
    def __init__(self, sdf_string, world_name, xdyn_enabled=False, px4_enabled=False):
        self.domains = ["Aerial"]
        self.px4_process = None
        super().__init__(sdf_string, world_name, self.xdyn_port)

        if px4_enabled:
            mavlink_port = 14550 + self.num  # unique port per drone instance
            self.px4_process = self._start_px4_sitl(mavlink_port)

    def _start_px4_sitl(self, mavlink_port):
        # launches: px4 -s px4.config -d
        # with PX4_SIM_MODEL=gz_x500 and correct Gazebo topic namespace
        ...
```

---

## 7. Keyboard / Joystick Control with PX4

**Yes — keyboard and joystick control work with PX4.**

| Method | How |
|--------|-----|
| **QGroundControl virtual joystick** | Built into QGC, works with mouse. Enabled in QGC settings → Joystick. |
| **Physical gamepad** | Plug USB gamepad into PC. QGC detects it automatically. Maps sticks to roll/pitch/throttle/yaw. |
| **ROS 2 keyboard → MAVLink** | `teleop_twist_keyboard` → `px4_ros_com` → PX4. More work but no QGC needed. |

For the demo, QGroundControl with a physical gamepad is the most reliable option.

---

## 8. Implementation Plan

### Phase 8 — One-command launch (~1 day)
Write a ROS 2 launch file that starts the bridge + keyboard teleop together for
the current (velocity controller) stack. Validates the launch file pattern before
applying it to PX4.

### Phase 9 — PX4 SITL integration (~1 week)

| Step | Task | Repo |
|------|------|------|
| 9.1 | Build PX4 SITL: `make px4_sitl gz_x500` | PX4-Autopilot (new clone) |
| 9.2 | Create `drone_px4.world` — remove velocity controller | LOTUSim core |
| 9.3 | Test PX4 + Gazebo standalone (no generic scenario) | LOTUSim core |
| 9.4 | Arm and fly with QGroundControl | — |
| 9.5 | Extend `x500.py` to spawn PX4 SITL per agent instance | LOTUSim-generic-scenario |
| 9.6 | Test inside full `scenario_launch.sh` with `defenseScenario.json` | LOTUSim-generic-scenario |
| 9.7 | Add sensor bridges to `bridge_nodes.launch.py` | LOTUSim-generic-scenario |
| 9.8 | Multi-drone test (if `nb_agents > 1`) | both |

---

## 9. Key Dependencies Already Satisfied

| Dependency | Status |
|---|---|
| Gazebo Harmonic | Installed, working |
| ROS 2 Jazzy | Installed, working |
| X500 model with IMU, GPS, magnetometer, baro | Done — sensor topic paths match PX4 |
| `ros_gz_bridge` | Installed |
| `teleop_twist_keyboard`, `joy`, `teleop_twist_joy` | Installed |
| `gz sim` CLI fix (GZ_CONFIG_PATH) | Done |
| Generic scenario X500 agent plugin | Exists, needs PX4 extension |

**Remaining:** Build PX4 SITL (~30 min, ~10 GB disk), create `drone_px4.world`,
extend X500 agent.
