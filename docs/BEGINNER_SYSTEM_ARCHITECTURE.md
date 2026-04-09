# LOTUSim Beginner System Architecture and Learning Roadmap

This document is for a new contributor who is starting LOTUSim with little or
no robotics, ROS 2, or Gazebo experience.

The short version:

- Learn Gazebo and SDF first if you want to add models, worlds, or scenarios.
- Learn ROS 2 next when you need models to communicate, publish sensor data, or
  receive commands.
- Learn the maritime and autonomy concepts gradually through one small feature
  at a time.

## 1. What LOTUSim Is

LOTUSim is a real-time maritime simulator built around Gazebo and ROS 2. It is
designed for multi-agent scenarios involving surface vessels, underwater
vehicles, aerial drones, sensors, mission logic, and external rendering.

In practical terms:

- Gazebo runs the simulated world.
- SDF files describe worlds, models, sensors, and plugins.
- ROS 2 provides communication between simulator modules and external tools.
- C++ Gazebo system plugins implement most simulator behavior.
- Model assets define ships, drones, underwater vehicles, obstacles, terrain,
  sensors, and configuration files.

## 2. Beginner Mental Model

Think of LOTUSim as five layers:

```text
User or mission script
        |
        v
ROS 2 commands, services, actions, and topics
        |
        v
LOTUSim Gazebo system plugins in systems/
        |
        v
Gazebo simulation world, entities, poses, sensors, physics
        |
        v
Assets in assets/worlds/ and assets/models/
```

If you add a new model, you usually start at the bottom. If you add a new
command, sensor output, mission behavior, or validation workflow, you usually
move upward into ROS 2 and C++ plugins.

## 3. Repository Map

```text
LOTUSim/
+-- assets/
|   +-- worlds/          # Gazebo world files, scenarios, plugin wiring
|   +-- models/          # Model folders with SDF, meshes, config, previews
+-- interfaces/
|   +-- lotusim_msgs/    # Core ROS 2 messages, services, and actions
|   +-- lotusim_sensor_msgs/
|                       # Sensor-specific ROS 2 messages and services
+-- systems/
|   +-- lotusim_common/  # Shared helper code and logging
|   +-- entity_manager/  # Creates, moves, deletes, and reports entities
|   +-- physics_engine_interface/
|   |                   # Bridge to external or alternate physics systems
|   +-- render_interface/
|   |                   # Bridge from simulation state to rendering
|   +-- waypoint_follower/
|   |                   # Basic waypoint navigation behavior
|   +-- sensors/         # Sensor framework and concrete sensors
+-- launch/
|   +-- lotusim          # Main install, build, run, UI, and doc helper
+-- physics/             # XDyn and related physics runtime artifacts
+-- docs/                # Architecture images, PDFs, and contributor docs
+-- examples/            # Example usage material
```

## 4. Runtime Architecture

The default world is `assets/worlds/lotusim.world`. It loads the core plugins:

```text
assets/worlds/lotusim.world
        |
        +-- physics_interface_plugin
        +-- entity_manager_plugin
        +-- lotusim_sensor_plugin
        +-- render_plugin
        +-- waypoint_plugin
```

Each plugin has a different responsibility:

| Plugin | Package | Responsibility |
| --- | --- | --- |
| `physics_interface_plugin` | `systems/physics_engine_interface/` | Connects Gazebo entities to external or alternate physics logic, including XDyn-related integration. |
| `entity_manager_plugin` | `systems/entity_manager/` | Creates, moves, deletes, and publishes simulated entities through ROS 2 actions and topics. |
| `lotusim_sensor_plugin` | `systems/sensors/lotusim_sensor_plugin/` | Finds and updates custom LOTUSim sensors. |
| `render_plugin` | `systems/render_interface/` | Publishes simulation state for rendering through ROS 2 or TCP/UDP. |
| `waypoint_plugin` | `systems/waypoint_follower/` | Moves configured vessels through waypoint, line, or circle behavior. |

The world file is the best first "wiring diagram" because it shows which
systems are active in a scenario.

## 5. Build and Run Flow

The main entrypoint is `launch/lotusim`.

Typical workflow:

```bash
lotusim install
lotusim build
lotusim run lotusim.world
```

The script handles important environment variables:

```text
GZ_SIM_SYSTEM_PLUGIN_PATH -> where Gazebo finds compiled LOTUSim plugins
GZ_GUI_PLUGIN_PATH        -> where Gazebo finds GUI plugins
GZ_SIM_RESOURCE_PATH      -> where Gazebo finds model assets
LOTUSIM_SPDLOG_LEVEL      -> logging level for LOTUSim plugins
```

This matters because Gazebo will not find custom LOTUSim plugins or model
assets unless these paths are set correctly.

## 6. How Data Moves Through the System

### Entity Management Flow

The entity manager is responsible for managing simulated assets.

```text
ROS 2 MAS command
        |
        v
interfaces/lotusim_msgs/msg/MASCmd.msg
        |
        v
systems/entity_manager/
        |
        v
Gazebo entity is created, moved, or deleted
        |
        v
Entity poses are published back through ROS 2
```

Important interface:

- `interfaces/lotusim_msgs/msg/MASCmd.msg`
- `interfaces/lotusim_msgs/action/MASCmd.action`
- `interfaces/lotusim_msgs/action/MASCmdArray.action`
- `interfaces/lotusim_msgs/msg/VesselPositionArray.msg`

Use this path when you want to add dynamic scenario behavior, such as spawning a
vessel, moving an asset, or deleting an object at runtime.

### Waypoint Flow

The waypoint follower gives vessels simple navigation behavior.

```text
World/model contains lotus_param waypoint settings
        |
        v
waypoint_plugin reads follower settings
        |
        v
Plugin computes movement toward waypoint
        |
        v
Vessel pose changes in Gazebo
        |
        v
Status is published through ROS 2
```

Typical waypoint configuration appears in world files such as
`assets/worlds/circling_ship_example.world`.

Useful concepts:

- Local XY waypoints
- Geographic waypoints
- Circle behavior
- Line behavior
- PID-style guidance settings
- Range tolerance
- Velocity and acceleration limits

### Sensor Flow

Sensors are defined in model SDF files and updated by the sensor system.

```text
Model SDF contains <sensor>
        |
        v
lotusim_sensor_plugin discovers sensor
        |
        v
Concrete sensor code reads Gazebo components
        |
        v
ROS 2 sensor message is published
```

Current sensor packages include:

- `systems/sensors/ais_sensor/`
- `systems/sensors/imu_sensor/`
- `systems/sensors/subsea_pressure_sensor/`
- `systems/sensors/lotusim_sensor_base/`
- `systems/sensors/lotusim_sensor_plugin/`

Use this path when you want to improve realism by adding or enhancing sensor
behavior.

### Render Flow

The render interface bridges simulation state to an external renderer.

```text
Gazebo simulation state
        |
        v
render_plugin
        |
        +-- ROS 2 mode
        |
        +-- TCP/UDP mode
```

Use this path when you want to improve visualization, external UI integration,
or renderer compatibility.

### Physics Flow

The physics interface bridges simulation entities to the external physics layer.

```text
Gazebo entity pose and commands
        |
        v
physics_interface_plugin
        |
        v
XDyn or external physics logic
        |
        v
Updated entity state
```

This area is more advanced. It is important for realism, but it is not the best
first place for a beginner unless the internship specifically focuses on
hydrodynamics or physics validation.

## 7. If You Want To Add A New Model

Start here if your goal is "I want to add a new ship, buoy, drone, underwater
vehicle, obstacle, terrain object, or sensor carrier."

### Technologies To Learn First

Learn these before deep ROS 2:

- Gazebo Harmonic basics
- SDF model files
- SDF world files
- Mesh formats such as `.dae` and `.stl`
- Model folder structure
- Basic coordinate frames: X, Y, Z, roll, pitch, yaw
- Basic Git workflow

Then learn:

- ROS 2 topics, messages, services, and actions
- How LOTUSim uses `lotus_param`
- How sensors are attached to model SDF files
- How models are spawned dynamically through the entity manager

### Model Folder Structure

A typical model folder looks like this:

```text
assets/models/my_model/
+-- model.config
+-- model.sdf
+-- preview
+-- my_model_config.yaml
+-- meshes/
    +-- body.dae
    +-- body.stl
```

Minimum useful files:

- `model.config`: Gazebo model metadata.
- `model.sdf`: The actual model definition.
- `meshes/`: Optional visual or collision geometry.

### Beginner Model Workflow

1. Pick an existing similar model.
2. Copy its folder into `assets/models/my_new_model/`.
3. Rename the model in `model.config` and `model.sdf`.
4. Replace or adjust the mesh.
5. Check collision and visual geometry.
6. Add sensors only after the model appears correctly.
7. Add the model to a world with `<include>`.
8. Run the world and verify the model appears.
9. Add `lotus_param` only when you need LOTUSim-specific behavior.
10. Document what the model represents and how to run it.

### Example World Include Pattern

```xml
<include>
  <uri>model://my_new_model</uri>
  <name>my_new_model_01</name>
  <pose>0 0 0 0 0 0</pose>
</include>
```

### When The Model Needs LOTUSim Behavior

Add a `lotus_param` block in the world include when the model needs behavior
from LOTUSim plugins:

```xml
<include>
  <uri>model://dtmb_hull</uri>
  <name>demo_ship</name>
  <pose>0 0 0 0 0 0</pose>

  <lotus_param>
    <waypoint_follower>
      <follower>
        <loop>true</loop>
        <circle>
          <radius>20</radius>
        </circle>
      </follower>
    </waypoint_follower>
    <render_interface>
      <publish_render>true</publish_render>
      <renderer_type_name>wamv</renderer_type_name>
    </render_interface>
  </lotus_param>
</include>
```

This is a good first scenario contribution because it does not require writing
C++ immediately.

## 8. If You Want To Add A New Scenario

A scenario is usually a world file that combines:

- Environment settings
- Core plugins
- Included models
- Initial poses
- LOTUSim parameters
- Waypoint or mission settings
- Sensor and renderer settings

Beginner scenario ideas:

- A surface vessel circles a buoy.
- A vessel follows a line path near a mine.
- An underwater vehicle passes over a seabed object.
- Multiple assets are placed in a harbor-like scene.
- A simple monitoring scenario publishes AIS and depth data.

This directly supports the project deliverables because it creates demonstrated
use cases and mission scenarios.

## 9. If You Want To Add Or Improve A Sensor

Start with existing sensors instead of creating a new framework.

Recommended reading order:

1. `systems/sensors/lotusim_sensor_base/`
2. `systems/sensors/lotusim_sensor_plugin/`
3. `systems/sensors/ais_sensor/`
4. `systems/sensors/imu_sensor/`
5. `systems/sensors/subsea_pressure_sensor/`
6. `interfaces/lotusim_sensor_msgs/`

Useful first sensor contributions:

- Add noise configuration.
- Add update-rate configuration.
- Add clearer activation/deactivation behavior.
- Add validation examples.
- Add documentation for sensor topic names.
- Fix incorrect field mapping if found during testing.

## 10. If You Want To Add Navigation Or Mission Behavior

Start with `systems/waypoint_follower/`.

Learn:

- Local XY coordinates
- Geographic latitude and longitude conversion
- Heading and bearing
- Velocity and acceleration limits
- Basic PID control concepts
- ROS 2 services for setting waypoints

Good beginner-to-intermediate features:

- Add a new waypoint pattern.
- Improve status reporting.
- Add validation for invalid waypoint inputs.
- Create documented mission scenarios.
- Add simple metrics such as distance-to-goal or completion time.

## 11. If You Want To Work On Project Realism

Realism can come from many places. Do not jump straight into physics unless that
is your assigned topic.

Beginner-friendly realism:

- Better model geometry and scale.
- Better sensor noise and update rates.
- More realistic scenario layouts.
- Clearer environmental objects.
- Validation scenarios with expected outputs.

Intermediate realism:

- Better waypoint controller behavior.
- Better collision or contact reporting.
- Sensor models based on range, occlusion, or environment.
- Mission scenario metrics.

Advanced realism:

- XDyn physics integration.
- Hydrodynamic parameter tuning.
- Multi-agent coordination.
- Real-time performance profiling.
- Renderer synchronization and external visualization.

## 12. Technology Roadmap

### Phase 1: Basic Development Comfort

Learn:

- Linux terminal
- Git basics
- C++ basics
- CMake basics
- `colcon build`
- Reading logs and command output

Practice:

- Build LOTUSim.
- Run one world.
- Change one SDF value and observe the effect.
- Read the default world file.

### Phase 2: Gazebo And SDF

Learn:

- Gazebo Harmonic
- SDF world files
- SDF model files
- Links, visuals, collisions, sensors
- Poses and coordinate frames
- `model://` asset resolution

Practice:

- Add a static object to a world.
- Add an existing model to a new world.
- Create a simple model folder.
- Attach an existing sensor to a model.

This is the ideal phase for model and scenario contribution.

### Phase 3: ROS 2 Basics

Learn:

- Nodes
- Topics
- Publishers and subscribers
- Services
- Actions
- Messages
- `rclcpp`
- `package.xml`
- ROS 2 workspace sourcing

Practice:

- Inspect LOTUSim topics while a world is running.
- Read custom message files in `interfaces/`.
- Send or observe a simple ROS 2 command.
- Trace one message from interface file to plugin code.

### Phase 4: LOTUSim Plugin Internals

Learn:

- Gazebo system plugin lifecycle
- `Configure`
- `PreUpdate`
- `Update`
- `PostUpdate`
- EntityComponentManager
- Shared plugin utilities in `lotusim_common`

Practice:

- Add a log line to a plugin.
- Add one SDF parameter.
- Add one validation check.
- Add one small status field or topic.

### Phase 5: Maritime And Autonomy Concepts

Learn:

- ENU coordinate frame
- Latitude and longitude
- Heading and bearing
- Waypoints and mission plans
- AIS concepts
- IMU basics
- Depth and pressure basics
- Surface and underwater vehicle concepts

Practice:

- Create a mission scenario with expected behavior.
- Add simple validation results.
- Compare simulated output against expected ranges.

### Phase 6: Advanced Contribution Areas

Learn as needed:

- XDyn and hydrodynamics
- WebSocket or TCP/UDP integration
- External rendering architecture
- Performance profiling
- Multi-agent planning
- More advanced control systems

Practice:

- Improve physics realism.
- Improve renderer data flow.
- Add complex multi-agent scenarios.
- Add repeatable validation benchmarks.

## 13. Suggested First Contributions

Choose one of these before attempting a large feature:

- Add a new static maritime object model, such as a buoy, marker, dock, or
  obstacle.
- Create a new world demonstrating one existing vessel and one new object.
- Document how to add a model to `assets/models/`.
- Document the ROS 2 topics/services/actions produced by one plugin.
- Add a simple validation scenario for the waypoint follower.
- Add better comments or examples for `lotus_param`.
- Improve one existing sensor configuration example.

## 14. Recommended Personal Path

For your stated interest in adding models and "stuff", use this path:

```text
Gazebo/SDF basics
        |
        v
Existing model structure in assets/models/
        |
        v
World include patterns in assets/worlds/
        |
        v
lotus_param for waypoint/render/sensor behavior
        |
        v
ROS 2 basics for communication and commands
        |
        v
C++ plugin internals only when needed
```

This path lets you contribute to project delivery early through models,
scenarios, documentation, and validation while gradually building toward deeper
ROS 2 and robotics work.

## 15. What Not To Start With

Avoid starting with these unless your supervisor specifically asks:

- XDyn internals
- Hydrodynamics tuning
- External renderer protocol details
- Multi-agent autonomy algorithms
- Full ROS 2 action server implementation
- Large C++ plugin refactors

Those areas matter, but they are easier after you understand how a world, model,
plugin, and message flow fit together.

## 16. Simple Definition Cheat Sheet

| Term | Beginner meaning |
| --- | --- |
| Gazebo | The simulator that runs the world. |
| SDF | XML format used to describe worlds, models, sensors, and plugins. |
| ROS 2 | Communication framework used by simulator modules and tools. |
| Topic | A named stream of messages. |
| Service | A request and response interaction. |
| Action | A longer-running goal with result and feedback. |
| Plugin | C++ code loaded by Gazebo to add behavior. |
| Model | A simulated object such as a ship, drone, mine, or terrain. |
| World | A complete simulation scene. |
| Sensor | Simulated data source such as AIS, IMU, pressure, GPS, or contact. |
| Entity | Gazebo's internal ID for a simulated object. |
| `lotus_param` | LOTUSim-specific settings attached to included models. |

## 17. Best Files To Read First

Read these in order:

1. `README.md`
2. `docs/STUDENT_PROJECT_GUIDE.md`
3. `launch/lotusim`
4. `assets/worlds/lotusim.world`
5. `assets/worlds/circling_ship_example.world`
6. `assets/models/wamv/model.sdf`
7. `interfaces/lotusim_msgs/msg/MASCmd.msg`
8. `systems/entity_manager/include/entity_manager/entity_manager.hpp`
9. `systems/waypoint_follower/include/waypoint_follower/waypoint_follower.hpp`
10. `systems/sensors/lotusim_sensor_base/include/lotusim_sensor_base/custom_sensor.hpp`

After that, pick one contribution path and follow only the files related to it.
Trying to understand every subsystem at once will slow you down.
