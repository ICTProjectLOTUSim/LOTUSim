# Gazebo-Focused Learning Pathway for LOTUSim

This document is a beginner pathway for learning LOTUSim from scratch with a
focus on Gazebo first. It tells you which folders matter, which files to read,
and where the Gazebo-related source code lives.

If your current goal is to add models, create worlds, or understand how the
simulator scene is assembled, start here before going deep into ROS 2.

## 1. What To Learn First

For a Gazebo-first contributor, learn in this order:

1. Basic Linux, Git, and terminal workflow.
2. Gazebo Harmonic basics.
3. SDF world files.
4. SDF model files.
5. Mesh assets and model folders.
6. Gazebo plugins at a high level.
7. LOTUSim `lotus_param` blocks.
8. ROS 2 basics only after you understand how worlds and models are loaded.

Do not start with ROS 2 actions, XDyn physics, or hydrodynamics. Those are
important later, but they are not the easiest entry point.

## 2. Main Folder Map

```text
LOTUSim/
+-- assets/
|   +-- worlds/          # Gazebo world/scenario files
|   +-- models/          # Gazebo model folders and meshes
+-- systems/             # C++ Gazebo system plugins
+-- interfaces/          # ROS 2 messages/services/actions used by plugins
+-- launch/              # Build/run helper scripts
+-- docs/                # Architecture and onboarding docs
+-- examples/            # Example notebook usage
+-- physics/             # XDyn binaries and physics artifacts
+-- dockerfile           # Container setup
+-- README.md            # Project overview
+-- CONTRIBUTING.md      # Contribution guidance
```

For your current Gazebo focus, prioritize:

- `assets/worlds/`
- `assets/models/`
- `systems/`
- `launch/lotusim`

Read `interfaces/` later when you need ROS 2 communication.

## 3. The Big Picture

LOTUSim starts from a Gazebo world file.

```text
World file
        |
        +-- Loads global simulation settings
        +-- Loads Gazebo/LOTUSim plugins
        +-- Includes model assets
        +-- Passes LOTUSim-specific settings through lotus_param
```

The default world is:

```text
assets/worlds/lotusim.world
```

That file loads the core LOTUSim plugins:

```xml
<plugin filename="physics_interface_plugin"
    name="lotusim::gazebo::PhysicsInterfacePlugin">
</plugin>

<plugin filename="entity_manager_plugin"
    name="lotusim::gazebo::EntityManager">
</plugin>

<plugin filename="lotusim_sensor_plugin"
    name="lotusim::sensor::LotusimSensorPlugin">
</plugin>

<plugin filename="render_plugin" name="lotusim::gazebo::RenderPlugin">
    <connection_protocol>ROS2</connection_protocol>
</plugin>

<plugin filename="waypoint_plugin"
    name="lotusim::gazebo::WaypointFollowerPlugin" />
```

This means Gazebo is the runtime host, and the C++ plugins in `systems/` add
LOTUSim behavior to Gazebo.

## 4. Learning Pathway By Week

### Week 1: Understand The Repo Shape

Goal: know where things live and how Gazebo launches.

Read these files:

1. `README.md`
2. `docs/STUDENT_PROJECT_GUIDE.md`
3. `docs/BEGINNER_SYSTEM_ARCHITECTURE.md`
4. `launch/lotusim`
5. `assets/worlds/lotusim.world`

Focus on:

- What command runs the simulator.
- Where model assets are loaded from.
- Which plugins the default world loads.
- What `GZ_SIM_RESOURCE_PATH` and `GZ_SIM_SYSTEM_PLUGIN_PATH` mean.

Important command:

```bash
lotusim run lotusim.world
```

Why this matters:

- `GZ_SIM_RESOURCE_PATH` lets Gazebo find folders under `assets/models/`.
- `GZ_SIM_SYSTEM_PLUGIN_PATH` lets Gazebo find compiled plugins from `systems/`.

### Week 2: Learn SDF Worlds

Goal: understand how a world file creates a scenario.

Read these files:

1. `assets/worlds/lotusim.world`
2. `assets/worlds/circling_ship_example.world`
3. `assets/worlds/gz_sensor_example.world`
4. `assets/worlds/aerialWorld.world`
5. `assets/worlds/defenseScenario.world`

What to look for:

- `<world name="...">`
- `<scene>`
- `<physics>`
- `<spherical_coordinates>`
- `<gravity>`
- `<plugin>`
- `<include>`
- `<pose>`
- `<lotus_param>`

Best beginner file:

```text
assets/worlds/circling_ship_example.world
```

Why:

- It loads the core LOTUSim plugins.
- It includes a model with `<include>`.
- It shows `lotus_param`.
- It configures waypoint following without requiring you to write C++.

### Week 3: Learn SDF Models

Goal: understand how Gazebo objects are defined.

Read these model files first:

1. `assets/models/mine/model.sdf`
2. `assets/models/wamv/model.sdf`
3. `assets/models/dtmb_hull/model.sdf`
4. `assets/models/lrauv/model.sdf`
5. `assets/models/x500/model.sdf`

Start with `mine` because it is simple:

```text
assets/models/mine/model.sdf
```

Then read `dtmb_hull` because it introduces sensors:

```text
assets/models/dtmb_hull/model.sdf
```

What to look for:

- `<model>`
- `<pose>`
- `<static>`
- `<link>`
- `<collision>`
- `<visual>` if present
- `<geometry>`
- `<mesh>`
- `<uri>model://...</uri>`
- `<sensor>`

Important idea:

```xml
<uri>model://mine/meshes/mine.stl</uri>
```

This tells Gazebo to find the model named `mine` in the model search path, then
load a mesh from its `meshes/` folder.

### Week 4: Add Your First Model Or Scenario

Goal: make a small visible change in Gazebo.

Good first tasks:

- Add an existing model to a world.
- Copy an existing model folder and rename it.
- Create a new world that includes one vessel and one obstacle.
- Change a model pose.
- Change a mesh scale.
- Add or remove a simple sensor from a model SDF.

Recommended first experiment:

1. Copy `assets/worlds/circling_ship_example.world`.
2. Rename it to something like `assets/worlds/my_first_scenario.world`.
3. Add an extra `<include>` for `mine`.
4. Run the world.
5. Confirm the mine appears.

Example:

```xml
<include>
  <uri>model://mine</uri>
  <name>mine_01</name>
  <pose>30 0 0 0 0 0</pose>
</include>
```

This is a valuable first contribution style because it builds toward
deliverables such as demonstrated use cases and mission scenarios.

### Week 5: Understand Gazebo Plugins

Goal: know where Gazebo behavior is implemented in C++.

Read only the headers first:

1. `systems/entity_manager/include/entity_manager/entity_manager.hpp`
2. `systems/waypoint_follower/include/waypoint_follower/waypoint_follower.hpp`
3. `systems/sensors/lotusim_sensor_plugin/include/lotusim_sensor_plugin/lotusim_sensor_plugin.hpp`
4. `systems/render_interface/include/render_interface/render_plugin.hpp`
5. `systems/physics_engine_interface/include/physics_engine_interface/physics_interface_plugin.hpp`

What to look for:

- `gz::sim::System`
- `ISystemConfigure`
- `ISystemPreUpdate`
- `ISystemUpdate`
- `ISystemPostUpdate`
- `gz::sim::EntityComponentManager`
- `GZ_ADD_PLUGIN`

Beginner meaning:

- `Configure`: plugin setup when the world loads.
- `PreUpdate`: runs before the simulation step.
- `Update`: runs during the simulation step.
- `PostUpdate`: runs after the simulation step.
- `EntityComponentManager`: Gazebo's database of simulated entities and
  components.
- `GZ_ADD_PLUGIN`: registers a C++ class so Gazebo can load it from a world
  file.

### Week 6: Trace One Gazebo Behavior End To End

Goal: connect a world file to the C++ code that reacts to it.

Recommended trace:

```text
assets/worlds/circling_ship_example.world
        |
        v
<plugin filename="waypoint_plugin" ...>
        |
        v
systems/waypoint_follower/include/waypoint_follower/waypoint_follower.hpp
        |
        v
systems/waypoint_follower/src/waypoint_follower.cpp
        |
        v
Gazebo model pose is updated
```

This is the best first code trace because it starts in a world file and ends in
visible movement.

## 5. Folder-By-Folder Explanation

### `assets/worlds/`

Purpose:

- Contains Gazebo world files.
- Defines complete simulation scenarios.
- Loads plugins.
- Includes models.
- Sets physics, coordinates, and environment.

Important files:

- `lotusim.world`: default LOTUSim world.
- `circling_ship_example.world`: best beginner scenario.
- `gz_sensor_example.world`: useful when learning Gazebo sensors.
- `aerialWorld.world`: aerial/drone-focused world.
- `defenseScenario.world`: larger scenario with multiple systems.
- `xdyn_multithread_test.world`: advanced physics/XDyn-related test world.

Learn this folder first if:

- You want to add a scenario.
- You want to place models.
- You want to change initial positions.
- You want to load/unload plugins.

### `assets/models/`

Purpose:

- Contains Gazebo model folders.
- Defines ships, drones, underwater vehicles, obstacles, terrain, and props.
- Stores meshes and model metadata.

Important model folders:

- `mine/`: simple object, good first model to study.
- `wamv/`: simple surface vehicle model with AIS sensor.
- `dtmb_hull/`: ship hull with contact and AIS sensors.
- `lrauv/`: underwater vehicle with AIS and IMU custom sensors.
- `bluerov2_heavy/`: underwater robot model.
- `x500/` and `x500_base/`: aerial drone models.
- `landscape/`: environment/terrain model.
- `fremm/`, `pha/`, `commando/`: vessel or maritime platform models.

Typical model folder:

```text
assets/models/example_model/
+-- model.config
+-- model.sdf
+-- preview
+-- meshes/
    +-- body.stl
    +-- body.dae
```

Learn this folder first if:

- You want to add a model.
- You want to modify a model mesh.
- You want to attach a sensor.
- You want to create maritime objects for scenarios.

### `systems/`

Purpose:

- Contains C++ Gazebo system plugins.
- Adds LOTUSim behavior to Gazebo.
- Reads Gazebo entities and components.
- Publishes or receives ROS 2 data.

Important subfolders:

- `entity_manager/`: manages Gazebo entities and dynamic spawning.
- `waypoint_follower/`: moves models along waypoint/line/circle paths.
- `sensors/`: discovers and updates custom sensors.
- `render_interface/`: bridges Gazebo state to rendering.
- `physics_engine_interface/`: bridges Gazebo to external physics/XDyn logic.
- `lotusim_common/`: shared helper functions.
- `aerial_demo_entity_manager/`: specialized aerial demo manager.

Learn this folder after:

- You understand world and model SDF files.
- You can run a world and add a model.
- You want to understand plugin behavior.

### `systems/entity_manager/`

Gazebo relevance:

- Uses `gz::sim::SdfEntityCreator` to create entities.
- Watches newly added and removed Gazebo models.
- Stores mappings between Gazebo entity IDs and model names.
- Publishes model poses.

Main files:

- `systems/entity_manager/include/entity_manager/entity_manager.hpp`
- `systems/entity_manager/src/entity_manager.cpp`
- `systems/entity_manager/CMakeLists.txt`
- `systems/entity_manager/package.xml`

Read this when:

- You want to understand spawning, moving, or deleting models.
- You want runtime scenario control.
- You want to know how Gazebo entities are tracked.

### `systems/waypoint_follower/`

Gazebo relevance:

- Reads model SDF/`lotus_param` data.
- Reads and writes Gazebo model pose.
- Implements simple movement behavior.

Main files:

- `systems/waypoint_follower/include/waypoint_follower/waypoint_follower.hpp`
- `systems/waypoint_follower/src/waypoint_follower.cpp`
- `systems/waypoint_follower/CMakeLists.txt`
- `systems/waypoint_follower/package.xml`

Read this when:

- You want to understand movement in Gazebo.
- You want to add new waypoint patterns.
- You want to create mission scenarios with simple autonomous behavior.

### `systems/sensors/`

Gazebo relevance:

- Finds custom sensors defined in model SDF files.
- Reads Gazebo components such as pose, velocity, orientation, and pressure.
- Publishes simulated sensor outputs.

Important files:

- `systems/sensors/lotusim_sensor_plugin/src/lotusim_sensor_plugin.cpp`
- `systems/sensors/lotusim_sensor_base/include/lotusim_sensor_base/custom_sensor.hpp`
- `systems/sensors/ais_sensor/src/ais_sensor.cpp`
- `systems/sensors/imu_sensor/src/imu_sensor.cpp`
- `systems/sensors/subsea_pressure_sensor/src/subsea_pressure_sensor.cc`

Read this when:

- You want to attach sensors to models.
- You want to improve simulated sensor realism.
- You want to understand custom Gazebo sensors.

### `systems/render_interface/`

Gazebo relevance:

- Reads model poses from Gazebo.
- Publishes rendering commands or position arrays.
- Supports ROS 2 and TCP/UDP style external rendering.

Main files:

- `systems/render_interface/include/render_interface/render_plugin.hpp`
- `systems/render_interface/src/render_plugin.cpp`
- `systems/render_interface/src/ros_interface.cpp`
- `systems/render_interface/src/tcpudp_interface.cpp`

Read this later unless your work involves visualization.

### `systems/physics_engine_interface/`

Gazebo relevance:

- Connects Gazebo entities to external or alternate physics behavior.
- Interacts with XDyn-related configuration.
- Updates vessel state through plugin logic.

Main files:

- `systems/physics_engine_interface/include/physics_engine_interface/physics_interface_plugin.hpp`
- `systems/physics_engine_interface/src/physics_interface_plugin.cpp`
- `systems/physics_engine_interface/src/ros2_interface.cpp`
- `systems/physics_engine_interface/src/xdyn_websocket.cpp`

Read this later. It is important but advanced.

### `interfaces/`

Purpose:

- Defines ROS 2 messages, services, and actions.
- These are communication contracts used by C++ plugins and external tools.

Important files:

- `interfaces/lotusim_msgs/msg/MASCmd.msg`
- `interfaces/lotusim_msgs/msg/VesselPosition.msg`
- `interfaces/lotusim_msgs/msg/VesselPositionArray.msg`
- `interfaces/lotusim_msgs/srv/SetWaypoints.srv`
- `interfaces/lotusim_sensor_msgs/msg/AIS.msg`
- `interfaces/lotusim_sensor_msgs/msg/PressureDepth.msg`

For a Gazebo-first pathway, read this later when you ask:

- What data is this plugin publishing?
- What command controls this model?
- What service sets waypoints?

### `launch/`

Purpose:

- Contains the `lotusim` helper command.
- Builds the workspace.
- Runs Gazebo.
- Sets Gazebo resource and plugin paths.

Important file:

- `launch/lotusim`

Read this early because it explains how the project actually starts.

### `docs/`

Purpose:

- Contains architecture images, onboarding docs, and technical PDFs.

Important files:

- `docs/STUDENT_PROJECT_GUIDE.md`
- `docs/BEGINNER_SYSTEM_ARCHITECTURE.md`
- `docs/GAZEBO_LEARNING_PATHWAY.md`
- `docs/lotusim_archi.png`
- `docs/mas_detailed_uml.png`
- `docs/xdyn.pdf`
- `docs/xdyn_tutorial.pdf`

### `examples/`

Purpose:

- Contains Python/Jupyter example material.
- Useful after you can run the simulator and want to interact with it externally.

### `physics/`

Purpose:

- Contains XDyn-related binaries/artifacts.
- More relevant for advanced physics integration than beginner Gazebo work.

## 6. Gazebo Source Code Map

Use this section when you ask, "Where is the Gazebo-related source code?"

### World And Model Definitions

```text
assets/worlds/*.world
assets/models/*/model.sdf
assets/models/*/model.config
assets/models/*/meshes/
```

These are not C++ source code, but they are the main Gazebo inputs.

### Gazebo Plugin Classes

```text
systems/entity_manager/include/entity_manager/entity_manager.hpp
systems/entity_manager/src/entity_manager.cpp

systems/waypoint_follower/include/waypoint_follower/waypoint_follower.hpp
systems/waypoint_follower/src/waypoint_follower.cpp

systems/sensors/lotusim_sensor_plugin/include/lotusim_sensor_plugin/lotusim_sensor_plugin.hpp
systems/sensors/lotusim_sensor_plugin/src/lotusim_sensor_plugin.cpp

systems/render_interface/include/render_interface/render_plugin.hpp
systems/render_interface/src/render_plugin.cpp

systems/physics_engine_interface/include/physics_engine_interface/physics_interface_plugin.hpp
systems/physics_engine_interface/src/physics_interface_plugin.cpp
```

### Gazebo Plugin Registration

Look for:

```cpp
GZ_ADD_PLUGIN(...)
```

This macro connects a C++ class to the plugin name used by Gazebo world files.

Examples:

- `entity_manager_plugin` is registered in `systems/entity_manager/src/entity_manager.cpp`.
- `waypoint_plugin` is registered in `systems/waypoint_follower/src/waypoint_follower.cpp`.
- `lotusim_sensor_plugin` is registered in `systems/sensors/lotusim_sensor_plugin/src/lotusim_sensor_plugin.cpp`.
- `render_plugin` is registered in `systems/render_interface/src/render_plugin.cpp`.
- `physics_interface_plugin` is registered in `systems/physics_engine_interface/src/physics_interface_plugin.cpp`.

### Gazebo CMake Dependencies

Look inside each plugin package's `CMakeLists.txt` for dependencies such as:

```cmake
find_package(gz-cmake3 REQUIRED)
find_package(sdformat14 REQUIRED)
find_package(gz-sim8 REQUIRED)
find_package(gz-plugin2 REQUIRED)
```

These tell you the package is building against Gazebo and SDF libraries.

## 7. Best Reading Order For You

Because you are mainly focused on Gazebo, use this order:

1. `docs/GAZEBO_LEARNING_PATHWAY.md`
2. `launch/lotusim`
3. `assets/worlds/lotusim.world`
4. `assets/worlds/circling_ship_example.world`
5. `assets/models/mine/model.sdf`
6. `assets/models/dtmb_hull/model.sdf`
7. `assets/models/wamv/model.sdf`
8. `systems/waypoint_follower/include/waypoint_follower/waypoint_follower.hpp`
9. `systems/waypoint_follower/src/waypoint_follower.cpp`
10. `systems/entity_manager/include/entity_manager/entity_manager.hpp`
11. `systems/entity_manager/src/entity_manager.cpp`
12. `systems/sensors/lotusim_sensor_plugin/src/lotusim_sensor_plugin.cpp`

Stop after item 7 if you only want to add models and worlds.

Continue into item 8 and onward when you want to understand behavior.

## 8. What To Practice

### Practice 1: Read A World File

Open:

```text
assets/worlds/circling_ship_example.world
```

Identify:

- Which plugins are loaded.
- Which model is included.
- What pose the model starts at.
- What `lotus_param` configures.

### Practice 2: Add An Existing Model To A World

Add this to a copied world file:

```xml
<include>
  <uri>model://mine</uri>
  <name>mine_01</name>
  <pose>30 0 0 0 0 0</pose>
</include>
```

Run the world and check that the object appears.

### Practice 3: Modify A Model

Open:

```text
assets/models/mine/model.sdf
```

Try changing:

- `<pose>`
- `<static>`
- mesh `<scale>`

Run a world containing the model and observe the change.

### Practice 4: Trace A Plugin

Open:

```text
assets/worlds/circling_ship_example.world
systems/waypoint_follower/src/waypoint_follower.cpp
```

Find:

- The `<plugin filename="waypoint_plugin">` block in the world.
- `GZ_ADD_PLUGIN` in the C++ file.
- `Configure`.
- `Update`.
- Where the plugin reads or changes Gazebo pose.

## 9. Contribution Ideas For A Gazebo-Focused Beginner

Good first contributions:

- Add a new simple maritime prop model.
- Add a new scenario world using existing models.
- Add documentation explaining a model folder.
- Add a scenario that demonstrates waypoint following.
- Improve `model.config` metadata for existing models.
- Add preview images for models that do not have them.
- Add a simple obstacle field or harbor-like world.
- Add validation notes for a Gazebo scenario.

Avoid as first contributions:

- Rewriting C++ plugins.
- Changing XDyn physics integration.
- Adding complex ROS 2 actions.
- Refactoring build scripts.
- Creating a brand new sensor framework.

## 10. When To Learn ROS 2

Learn ROS 2 after you can answer these Gazebo questions:

- What is a world file?
- What is a model file?
- How does `<include>` work?
- How does `model://...` resolve meshes?
- What does a Gazebo plugin block do?
- Where does LOTUSim register C++ plugins?
- How do I run a world and check that a model appears?

Then start ROS 2 when you need to:

- Send commands to the simulator.
- Set waypoints at runtime.
- Read published vessel positions.
- Read sensor outputs.
- Spawn or delete models dynamically.
- Connect external scripts, notebooks, or UI tools.

For ROS 2, start with:

```text
interfaces/lotusim_msgs/msg/MASCmd.msg
interfaces/lotusim_msgs/srv/SetWaypoints.srv
interfaces/lotusim_sensor_msgs/msg/AIS.msg
```

## 11. Simple Glossary

| Term | Meaning |
| --- | --- |
| Gazebo | The simulation engine that runs the world. |
| SDF | XML format used by Gazebo for worlds and models. |
| World | A full simulation scene. |
| Model | A simulated object, such as a ship, drone, mine, or terrain. |
| Link | A physical part of a model. |
| Collision | Geometry used for physics/contact. |
| Visual | Geometry used for rendering. |
| Mesh | A `.stl` or `.dae` file used by visual/collision geometry. |
| Sensor | Simulated data source attached to a model/link. |
| Plugin | C++ behavior loaded by Gazebo. |
| Entity | Gazebo's internal ID for a world object. |
| Component | Data attached to an entity, such as pose or velocity. |
| EntityComponentManager | Gazebo's API for reading/writing entity data. |
| `lotus_param` | LOTUSim-specific SDF configuration for plugins. |

## 12. Your Recommended Path

For your current focus, follow this path:

```text
Read launch/lotusim
        |
        v
Read assets/worlds/lotusim.world
        |
        v
Read assets/worlds/circling_ship_example.world
        |
        v
Read assets/models/mine/model.sdf
        |
        v
Add an existing model to a copied world
        |
        v
Create or modify a model folder
        |
        v
Only then read waypoint_follower and entity_manager C++ plugins
```

This keeps your learning practical. You will understand how the simulator is
assembled before you try to understand how every plugin communicates internally.
