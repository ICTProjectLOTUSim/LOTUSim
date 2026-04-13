# LOTUSim Student Project Guide

This guide is meant to help a new contributor understand **how the repository is organized**, **which modules do what**, and **where to start reading and experimenting**.

For a more beginner-oriented architecture overview and learning roadmap, see
[`BEGINNER_SYSTEM_ARCHITECTURE.md`](BEGINNER_SYSTEM_ARCHITECTURE.md).

For a Gazebo-first pathway focused on worlds, models, and Gazebo source code,
see [`GAZEBO_LEARNING_PATHWAY.md`](GAZEBO_LEARNING_PATHWAY.md).

---

## 1) What LOTUSim is (in one minute)

LOTUSim is a multi-agent maritime simulator built around Gazebo (gz sim) + ROS 2.
It supports cross-domain simulation (surface vessels, underwater vehicles, aerial drones), and it is designed as a plugin-based system:

- **World + models** are described in SDF files.
- **Simulation behavior** is implemented as Gazebo system plugins in `systems/`.
- **ROS 2 interfaces** are defined in `interfaces/` and used by plugins.
- **Build/run orchestration** is done by the `launch/lotusim` helper script.

---

## 2) High-level repository structure

```text
LOTUSim/
├── assets/              # Simulation worlds and 3D models (SDF, meshes, configs)
├── docs/                # Architecture figures, PDFs, Doxygen config, this guide
├── examples/            # Example notebook(s)
├── interfaces/          # ROS 2 message/service/action packages
├── launch/              # Main CLI script (`lotusim`), install/build/run helpers
├── physics/             # External physics binaries / runtime artifacts (xdyn)
├── systems/             # Core Gazebo plugins and sensor plugins
├── dockerfile           # Containerized build/runtime setup
├── README.md            # Project-level introduction
└── CONTRIBUTING.md      # Contribution process and governance
```

---

## 3) Core runtime architecture

The default world (`assets/worlds/lotusim.world`) loads several key plugins:

1. **Physics interface plugin**
   - Connects simulation entities to external/alternate physics interfaces.
2. **Entity manager plugin**
   - Manages entities and multi-agent interactions through ROS 2.
3. **Sensor plugin**
   - Registers and updates custom sensor stack (AIS / IMU / pressure depth).
4. **Render interface plugin**
   - Bridges simulation state to an external renderer (ROS2 or TCP/UDP modes).
5. **Waypoint follower plugin**
   - Executes navigation behavior based on waypoints.

A simplified mental model:

```text
SDF World + Models
      |
      v
Gazebo (gz sim)
  |   |   |   |
  |   |   |   +--> Render plugin --> ROS2 / TCPUDP renderer pipeline
  |   |   +------> Sensor plugin --> ROS2 sensor topics
  |   +----------> Entity manager --> ROS2 commands/actions/services
  +--------------> Physics interface --> external physics backends

ROS 2 interface types come from interfaces/lotusim_msgs and interfaces/lotusim_sensor_msgs
```

---

## 4) Directory-by-directory deep dive

## `interfaces/` (ROS 2 API contracts)

These packages define communication types used by systems.

- `interfaces/lotusim_msgs/`
  - Core platform-level messages and actions (e.g., vessel commands/positions, stats, renderer commands, MAS commands).
- `interfaces/lotusim_sensor_msgs/`
  - Sensor-specific messages/services (e.g., AIS, GPS, pressure depth, collision reports).

If you need to add new data exchanged between plugins and applications, this is usually where you start.

## `systems/` (simulation logic plugins)

Main plugin packages:

- `systems/lotusim_common/`
  - Shared utilities (logging, common helpers, entity grouping).
- `systems/entity_manager/`
  - Multi-agent orchestration plugin handling entity-level operations and ROS interaction.
- `systems/aerial_demo_entity_manager/`
  - Specialized extension of entity manager for aerial demo needs.
- `systems/physics_engine_interface/`
  - Physics bridge/plugin; includes ROS2 and websocket-oriented integration classes.
- `systems/render_interface/`
  - Output bridge to renderer through ROS2 or TCP/UDP.
- `systems/waypoint_follower/`
  - Navigation control logic for waypoint following.
- `systems/sensors/*`
  - Sensor framework:
    - `lotusim_sensor_base`: custom sensor base class and shared sensor internals.
    - `lotusim_sensor_plugin`: Gazebo system plugin that coordinates sensors.
    - `ais_sensor`, `imu_sensor`, `subsea_pressure_sensor`: concrete sensor implementations.

## `assets/` (world + model content)

- `assets/worlds/`
  - Prebuilt simulation scenes (`lotusim.world`, demos/tests).
- `assets/models/`
  - Vehicle and environment models (mesh files + SDF + config/yaml).

When adding a new robot/vessel/environment object, this is the area you modify.

## `launch/` (developer UX commands)

The `launch/lotusim` script is the main CLI entrypoint. Typical commands:

- `lotusim install`
- `lotusim build`
- `lotusim run [world.world]`
- `lotusim ui`
- `lotusim doc`

This script also handles environment setup and ROS/Gazebo variables.

## `docs/` (design artifacts)

Contains architecture imagery and technical PDFs (`xdyn.pdf`, `xdyn_tutorial.pdf`), plus Doxygen config.

---

## 5) How build and run work in practice

Typical flow:

1. Install dependencies and build packages with colcon.
2. Source ROS + workspace setup scripts.
3. Launch a selected world in Gazebo with LOTUSim plugins.

In this repo, the process is wrapped by:

```bash
lotusim install
lotusim run lotusim.world
```

The script sets variables like:

- `GZ_SIM_SYSTEM_PLUGIN_PATH`
- `GZ_GUI_PLUGIN_PATH`
- `GZ_SIM_RESOURCE_PATH`

so Gazebo can locate custom LOTUSim plugins and assets.

---

## 6) Suggested learning path for a new student

### Step A — Build a map in your head

Read in this order:

1. `README.md` (project purpose)
2. `launch/lotusim` (how people actually run it)
3. `assets/worlds/lotusim.world` (which plugins load by default)
4. `interfaces/lotusim_msgs` + `interfaces/lotusim_sensor_msgs` (data contracts)
5. `systems/entity_manager` and `systems/waypoint_follower` (core behaviors)

### Step B — Understand one end-to-end pipeline

Pick one behavior, e.g. “waypoint command to vessel movement”, and trace:

- command type in `interfaces/`
- subscriber/callback in a `systems/*` plugin
- effect on entity state / published outputs

### Step C — Make one tiny change safely

Examples:

- Add an extra log line in a plugin callback.
- Add one debug topic publication.
- Add a simple parameter (from SDF plugin tag) and print it.

This helps you validate your environment and understand plugin lifecycle (`Configure`, `PreUpdate`, `PostUpdate` patterns in Gazebo systems).

---

## 7) Practical tips for first contributions

- Start with **one package at a time**; do not attempt to understand every sensor and manager simultaneously.
- Keep an eye on package dependencies in each `package.xml`.
- Use world files as the “wiring diagram” showing which plugins are active.
- When adding interfaces, regenerate/rebuild before debugging runtime behavior.
- Prefer extending existing plugin patterns over creating a new package too early.

---

## 8) Quick reference: “Where should I edit?”

- Add/modify command/status message types → `interfaces/`
- Add entity-level orchestration logic → `systems/entity_manager/`
- Add new sensor model behavior → `systems/sensors/`
- Add renderer bridge behavior → `systems/render_interface/`
- Add navigation behavior → `systems/waypoint_follower/`
- Add simulation scene or models → `assets/worlds/` and `assets/models/`
- Add workflow automation → `launch/lotusim`

---

## 9) Suggested next document (optional)

If you want, the next useful artifact would be a **message-flow catalog** listing:

- each ROS topic/service/action,
- which plugin publishes/subscribes to it,
- and where it appears in the code.

That document makes onboarding and debugging much faster for new contributors.
